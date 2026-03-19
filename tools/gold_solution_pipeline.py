"""
Gold Solution Testcase Pipeline (Ollama Local AI Edition)

Uses verified C solutions from Lazygarde/THCS2_Code_PTIT repo
combined with Ollama local AI input generators to produce reliable testcases.
NO API QUOTA LIMITS - runs entirely on local hardware.

Pipeline:
1. Fetch gold solution C code from GitHub API
2. Use Ollama (local AI) to generate ONLY an input generator script
3. Compile gold .c solution with gcc
4. Run generator → pipe into compiled solution → capture output
5. Save input/output pairs to database
"""
import os
import sys
import time
import re
import json
import subprocess
import tempfile
import requests

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from database import SessionLocal
from models import Problem, TestCase

GITHUB_API_URL = "https://api.github.com/repos/Lazygarde/THCS2_Code_PTIT/contents"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:3b"


def fetch_gold_solutions_map():
    """Fetch the list of files from GitHub API and map problem codes to raw URLs."""
    print("Fetching solution list from GitHub...")
    resp = requests.get(GITHUB_API_URL)
    if resp.status_code != 200:
        print(f"Failed to fetch repo contents: {resp.status_code}")
        return {}
    
    solution_map = {}
    for item in resp.json():
        name = item.get("name", "")
        match = re.match(r'^(C\d{5})', name)
        if match:
            code = match.group(1)
            download_url = item.get("download_url", "")
            if download_url:
                solution_map[code] = download_url
    
    print(f"Found {len(solution_map)} gold solutions.")
    return solution_map


def generate_input_generator_only(problem):
    """Use Ollama local AI to generate ONLY an input generator. No quota limits!"""
    
    prompt = f"""Write a Python 3 script that generates a SINGLE random valid input for this problem. Print the input to stdout.

Problem: {problem.code} - {problem.title}
Description: {problem.description[:500]}
{problem.input_description or ''}
Sample Input: {problem.sample_input or 'N/A'}

Rules:
- DO NOT use input() or sys.stdin. Only generate and print output.
- Use random module for randomness.
- Generate values within the problem's constraints.
- Print exactly one test case input.

Return ONLY the Python code, no explanation:
```python
import random
...
```"""

    try:
        resp = requests.post(OLLAMA_API_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 512,
            }
        }, timeout=120)
        
        if resp.status_code != 200:
            return None, f"Ollama API error: {resp.status_code}"
        
        text = resp.json().get("response", "")
        
        # Try to extract code from code blocks
        pattern = r"```(?:python)?\n?(.*?)```"
        blocks = re.findall(pattern, text, re.DOTALL)
        
        if blocks:
            return blocks[0].strip(), ""
        
        # If no code blocks, try to use the raw text if it looks like Python
        if "import" in text and "print" in text:
            # Clean up: remove any non-code text before 'import'
            idx = text.find("import")
            if idx >= 0:
                return text[idx:].strip(), ""
        
        return None, "AI did not return a valid code block"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to Ollama. Make sure 'ollama serve' is running."
    except Exception as e:
        return None, f"Ollama error: {str(e)}"


def run_pipeline_for_problem(problem, gold_solution_url, num_tests=10):
    """Run the full pipeline for a single problem."""
    db = SessionLocal()
    
    try:
        # Check existing testcase count  
        tc_count = db.query(TestCase).filter(TestCase.problem_id == problem.id).count()
        if tc_count >= 10:
            return 0, "Already has enough testcases"
        
        needed = 10 - tc_count
        
        # Step 1: Download gold solution
        resp = requests.get(gold_solution_url)
        if resp.status_code != 200:
            return 0, f"Failed to download gold solution: {resp.status_code}"
        gold_c_code = resp.text
        
        # Step 2: Generate input generator via local AI
        gen_code, err = generate_input_generator_only(problem)
        if not gen_code:
            return 0, f"Input generator failed: {err}"
        
        # Step 3: Compile gold solution and run pipeline
        with tempfile.TemporaryDirectory() as tmpdir:
            sol_path = os.path.join(tmpdir, "gold.c")
            exe_path = os.path.join(tmpdir, "gold.exe")
            gen_path = os.path.join(tmpdir, "gen.py")
            
            with open(sol_path, "w", encoding="utf-8") as f:
                f.write(gold_c_code)
            
            with open(gen_path, "w", encoding="utf-8") as f:
                f.write(gen_code)
            
            # Compile with gcc
            compile_res = subprocess.run(
                ["gcc", "-std=c11", "-O2", "-o", exe_path, sol_path],
                capture_output=True, text=True
            )
            if compile_res.returncode != 0:
                return 0, f"Compile error: {compile_res.stderr[:200]}"
            
            # Get max order
            max_order = 0
            existing = db.query(TestCase).filter(
                TestCase.problem_id == problem.id
            ).order_by(TestCase.order.desc()).first()
            if existing:
                max_order = existing.order
            
            # Step 4: Generate testcases
            generated = 0
            for i in range(needed):
                try:
                    # Run generator
                    gen_proc = subprocess.run(
                        ["python", gen_path, str(i)],
                        capture_output=True, text=True, timeout=5
                    )
                    if gen_proc.returncode != 0:
                        continue
                    
                    tc_input = gen_proc.stdout.strip()
                    if not tc_input:
                        continue
                    
                    # Run gold solution
                    sol_proc = subprocess.run(
                        [exe_path],
                        input=tc_input,
                        capture_output=True, text=True, timeout=10
                    )
                    if sol_proc.returncode != 0:
                        continue
                    
                    tc_output = sol_proc.stdout.strip()
                    
                    # Save to DB
                    max_order += 1
                    tc = TestCase(
                        problem_id=problem.id,
                        input_data=tc_input,
                        expected_output=tc_output,
                        is_sample=False,
                        order=max_order
                    )
                    db.add(tc)
                    generated += 1
                    
                except subprocess.TimeoutExpired:
                    continue
                except Exception as e:
                    continue
            
            db.commit()
            return generated, ""
    
    finally:
        db.close()


def run_bulk_gold_pipeline():
    """Run the gold solution pipeline for all problems in tin-hoc-co-so-2."""
    db = SessionLocal()
    
    try:
        CATEGORY_SLUG = "tin-hoc-co-so-2"
        problems = db.query(Problem).filter(Problem.category == CATEGORY_SLUG).all()
        print(f"Found {len(problems)} problems in '{CATEGORY_SLUG}'")
        
        # Fetch gold solutions map
        solution_map = fetch_gold_solutions_map()
        
        success_count = 0
        fail_count = 0
        skip_count = 0
        no_gold_count = 0
        
        for idx, p in enumerate(problems):
            # Check if already has enough
            tc_count = db.query(TestCase).filter(TestCase.problem_id == p.id).count()
            if tc_count >= 10:
                skip_count += 1
                continue
            
            # Check if gold solution exists
            if p.code not in solution_map:
                no_gold_count += 1
                print(f"  {p.code}: No gold solution found")
                continue
            
            needed = 10 - tc_count
            print(f"\n[{idx+1}/{len(problems)}] {p.code}: {tc_count} tc, need {needed} more...", end=" ")
            
            try:
                count, err = run_pipeline_for_problem(p, solution_map[p.code], needed)
                if count > 0:
                    print(f"SUCCESS +{count}")
                    success_count += 1
                else:
                    print(f"FAILED: {err[:80]}")
                    fail_count += 1
            except Exception as e:
                print(f"ERROR: {str(e)[:80]}")
                fail_count += 1
        
        print(f"\n{'='*50}")
        print(f"GOLD PIPELINE RESULTS (Ollama Local AI):")
        print(f"  Success:        {success_count}")
        print(f"  Failed:         {fail_count}")
        print(f"  Skipped (>=10): {skip_count}")
        print(f"  No gold sol:    {no_gold_count}")
        print(f"{'='*50}")
    
    finally:
        db.close()


if __name__ == "__main__":
    run_bulk_gold_pipeline()
