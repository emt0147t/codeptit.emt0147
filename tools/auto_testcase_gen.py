"""
AI Auto Testcase Generator

Uses Google Gemini API to read an existing problem description from the database,
write a Python Input Generator and a Python/C++ Solution Code, and runs the 
testcase_runner script to save the generated testcases back to the database.
"""
import os
import sys
import argparse
import google.generativeai as genai

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Problem
from tools.testcase_runner import run_local_generator

# Ensure your GEMINI_API_KEY is available in the environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables. Auto-generation will fail.")

def generate_scripts_for_problem(problem: Problem):
    """Calls Gemini to write generator and solution scripts."""    
    prompt = f"""
I have a programming problem on an Online Judge platform. I need two scripts to generate test data for it.
1. A Python 3 script capable of randomly generating a valid input file to STDOUT.
2. A Python 3 script capable of reading from STDIN and printing the correct output to STDOUT.

**Problem Code:** {problem.code}
**Problem Title:** {problem.title}

**Description:**
{problem.description}
{problem.input_description}
{problem.output_description}

**Sample Input:**
{problem.sample_input}

**Sample Output:**
{problem.sample_output}

Return your answer strictly in the following format with exactly two code blocks:
```python
# First code block: Python Input Generator Script.
# Must use random to generate different inputs.
# Print the results.
import random
...
```

```python
# Second code block: Python Solution Script.
# Read from standard input, process, and print correct result to standard output.
import sys
...
```
Do not include any extra text. Make sure the codes are clean and handle large edge cases based on problem limits.
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Parse output for two blocks
        blocks = text.split("```python")
        if len(blocks) < 3:
            raise ValueError("LLM response did not contain exactly two python code blocks")
            
        gen_code = blocks[1].split("```")[0].strip()
        sol_code = blocks[2].split("```")[0].strip()
        
        return gen_code, sol_code
    except Exception as e:
        print(f"Failed to generate scripts via LLM: {e}")
        return None, None

def auto_generate_testcases(problem_code: str, num_tests: int = 10):
    db = SessionLocal()
    problem = db.query(Problem).filter(Problem.code == problem_code).first()
    
    if not problem:
        db.close()
        return 0, f"Lỗi: Không tìm thấy bài tập {problem_code}"

    gen_code, sol_code = generate_scripts_for_problem(problem)
    
    if not gen_code or not sol_code:
        db.close()
        return 0, "Sinh script bằng AI thất bại. Vui lòng thử lại sau."
        
    count = run_local_generator(
        problem_code=problem_code,
        generator_code=gen_code,
        solution_code=sol_code,
        num_tests=num_tests,
        language="python"
    )
    
    db.close()
    
    if count is not False:
        return count, ""
    else:
        return 0, "Lỗi trong quá trình chạy testcase_runner."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Testcase Generator")
    parser.add_argument("--code", required=True, help="Problem code to generate test cases for")
    parser.add_argument("--num", type=int, default=10, help="Number of test cases to generate")
    
    args = parser.parse_args()
    auto_generate_testcases(args.code, args.num)
