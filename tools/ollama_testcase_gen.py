"""
Ollama Local AI Testcase Generator

Uses local Ollama API to generate testcases for problems.
Pipeline:
1. Read problem description
2. Ask Ollama to generate an Input Generator (Python script)
3. Ask Ollama to generate a Solution (Python script)
4. Run generator + solution via testcase_runner to produce testcases
"""
import os
import sys
import re
import requests
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from database import SessionLocal
from models import Problem

logger = logging.getLogger(__name__)

OLLAMA_API_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")


def check_ollama_status():
    """Check if Ollama is running and which models are available."""
    try:
        resp = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            return {
                "status": "online",
                "models": models,
                "current_model": OLLAMA_MODEL,
                "model_available": any(OLLAMA_MODEL in m for m in models),
            }
        return {"status": "error", "error": f"HTTP {resp.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "error": "Ollama chưa chạy. Hãy chạy 'ollama serve' trước."}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def _call_ollama(prompt, max_tokens=1024):
    """Call Ollama API and return generated text."""
    try:
        resp = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens,
                }
            },
            timeout=120
        )
        if resp.status_code != 200:
            return None, f"Ollama API error: {resp.status_code}"
        return resp.json().get("response", ""), ""
    except requests.exceptions.ConnectionError:
        return None, "Không thể kết nối Ollama. Hãy chạy 'ollama serve'."
    except Exception as e:
        return None, f"Lỗi Ollama: {str(e)}"


def _extract_python_code(text):
    """Extract Python code from AI response."""
    # Try markdown code blocks first
    pattern = r"```(?:python)?\n?(.*?)```"
    blocks = re.findall(pattern, text, re.DOTALL)
    if blocks:
        return blocks[0].strip()
    
    # Fallback: try to find code starting with 'import' or 'def' or '#'
    for keyword in ["import ", "def ", "# ", "from "]:
        idx = text.find(keyword)
        if idx >= 0:
            return text[idx:].strip()
    
    return None


def _generate_input_generator(problem):
    """Use Ollama to generate an input generator script."""
    prompt = f"""Write a Python 3 script that generates a SINGLE random valid input for this competitive programming problem. Print the input to stdout.

Problem: {problem.code} - {problem.title}
Description: {(problem.description or '')[:600]}
Input Format: {(problem.input_description or '')[:300]}
Sample Input:
{(problem.sample_input or 'N/A')[:200]}

CRITICAL RULES:
- DO NOT use input() or sys.stdin. Only generate and print output.
- Use random module for randomness.
- Generate values WITHIN the problem's constraints.
- Print exactly ONE test case input to stdout.
- Accept sys.argv[1] as seed if provided.

Return ONLY the Python code inside a code block:
```python
import random
import sys
if len(sys.argv) > 1: random.seed(int(sys.argv[1]))
# ... your code ...
```"""

    text, err = _call_ollama(prompt, max_tokens=800)
    if text is None:
        return None, err
    
    code = _extract_python_code(text)
    if not code:
        return None, "AI không tạo được code generator hợp lệ"
    
    # Basic validation
    if "input()" in code:
        code = code.replace("input()", "# input() removed by system")
    
    return code, ""


def _generate_solution(problem):
    """Use Ollama to generate a solution script."""
    prompt = f"""Write a Python 3 solution for this competitive programming problem. Read from stdin and print to stdout.

Problem: {problem.code} - {problem.title}
Description: {(problem.description or '')[:600]}
Input Format: {(problem.input_description or '')[:300]}
Output Format: {(problem.output_description or '')[:300]}
Sample Input:
{(problem.sample_input or 'N/A')[:200]}
Sample Output:
{(problem.sample_output or 'N/A')[:200]}

RULES:
- Read from stdin using input()
- Print result to stdout using print()
- Handle all edge cases
- Code must be COMPLETE and RUNNABLE

Return ONLY the Python code inside a code block:
```python
# solution code here
```"""

    text, err = _call_ollama(prompt, max_tokens=1024)
    if text is None:
        return None, err
    
    code = _extract_python_code(text)
    if not code:
        return None, "AI không tạo được solution code hợp lệ"
    
    return code, ""


def ollama_generate_testcases(problem_code, num_tests=10):
    """
    Main entry point: Generate testcases for a problem using Ollama AI.
    
    Returns: (count, error_message)
    """
    # Check Ollama status first
    status = check_ollama_status()
    if status["status"] != "online":
        return 0, status.get("error", "Ollama không hoạt động")
    if not status.get("model_available", False):
        return 0, f"Model '{OLLAMA_MODEL}' chưa được cài. Chạy: ollama pull {OLLAMA_MODEL}"
    
    # Get problem from DB
    db = SessionLocal()
    try:
        problem = db.query(Problem).filter(Problem.code == problem_code).first()
        if not problem:
            return 0, f"Không tìm thấy bài tập {problem_code}"
    finally:
        db.close()
    
    # Step 1: Generate input generator
    logger.info(f"[{problem_code}] Asking Ollama to generate input generator...")
    gen_code, err = _generate_input_generator(problem)
    if not gen_code:
        return 0, f"Lỗi sinh Input Generator: {err}"
    
    # Step 2: Generate solution
    logger.info(f"[{problem_code}] Asking Ollama to generate solution...")
    sol_code, err = _generate_solution(problem)
    if not sol_code:
        return 0, f"Lỗi sinh Solution: {err}"
    
    # Step 3: Run generator + solution via testcase_runner
    logger.info(f"[{problem_code}] Running testcase generator ({num_tests} tests)...")
    
    tools_path = os.path.join(PROJECT_ROOT, "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    
    from testcase_runner import run_local_generator
    count, run_err = run_local_generator(
        problem_code=problem_code,
        generator_code=gen_code,
        solution_code=sol_code,
        num_tests=num_tests,
        language="python"
    )
    
    if count is False:
        return 0, f"Lỗi: {run_err}\n\n--- Generator Code (AI) ---\n{gen_code[:300]}...\n\n--- Solution Code (AI) ---\n{sol_code[:300]}..."
    
    # Build result message
    error_msg = ""
    if run_err:
        error_msg = run_err
    if count > 0:
        error_msg = f"Generator (AI):\n{gen_code[:200]}...\n\nSolution (AI):\n{sol_code[:200]}...\n\n{error_msg}" if error_msg else ""
    
    return count, error_msg


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ollama AI Testcase Generator")
    parser.add_argument("--code", required=True, help="Problem code")
    parser.add_argument("--num", type=int, default=10, help="Number of testcases")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    count, err = ollama_generate_testcases(args.code, args.num)
    if count > 0:
        print(f"✅ Generated {count} testcases for {args.code}")
    else:
        print(f"❌ Failed: {err}")
