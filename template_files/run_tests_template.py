import json
import subprocess
import re
import os

def lenient_whitespace(text):
    return re.sub(r'\s+', '', text).strip()

def compile_and_run(student_cpp_path, input_data):
    executable = "student_program"
    compile_process = subprocess.run([
        "g++", "-o", executable, student_cpp_path
    ], capture_output=True, text=True)
    
    if compile_process.returncode != 0:
        return "", compile_process.stderr
    
    try:
        run_process = subprocess.Popen(
            ["./" + executable],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = run_process.communicate(input=input_data)
        return stdout.strip(), stderr.strip()
    except Exception as e:
        return "", str(e)

def compare_outputs(student_output, expected_output):
    student_output = lenient_whitespace(student_output)
    expected_output = lenient_whitespace(expected_output)
    return student_output == expected_output

def grade():
    student_cpp_path = "LabX.cpp"
    
    test_cases = []
    
    test_results = []
    total_score = 0.0
    max_score = 100
    points_per_question = max_score / len(test_cases)
    
    for i, (input_file, output_file, visibility) in enumerate(test_cases):
        with open(input_file, 'r') as f:
            input_data = f.read()
        
        with open(output_file, 'r') as f:
            expected_output = f.read()
        
        student_output, errors = compile_and_run(student_cpp_path, input_data)
        
        if errors:
            test_results.append({
                "score": 0.0,
                "max_score": points_per_question,
                "status": "failed",
                "name": f"{student_cpp_path} Test Case {i+1}",
                "output": f"Inputs:\n\n{input_data}\n\nError in your program:\n{errors}",
                "visibility": visibility
            })
        else:
            if compare_outputs(student_output, expected_output):
                test_results.append({
                    "score": points_per_question,
                    "max_score": points_per_question,
                    "status": "passed",
                    "name": f"{student_cpp_path} Test Case {i+1}",
                    "output": "Correct output.",
                    "visibility": visibility
                })
                total_score += points_per_question
            else:
                test_results.append({
                    "score": 0.0,
                    "max_score": points_per_question,
                    "status": "failed",
                    "name": f"{student_cpp_path} Test Case {i+1}",
                    "output": f"Inputs:\n\n{input_data}\n\nExpected:\n\n{expected_output}\n\nGot:\n\n{student_output}",
                    "visibility": visibility
                })
    
    results = {
        "score": round(total_score),
        "output": "Autograder results below:",
        "visibility": "visible",
        "stdout_visibility": "visible",
        "tests": test_results
    }
    
    with open('/autograder/results/results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
if __name__ == "__main__":
    grade()
