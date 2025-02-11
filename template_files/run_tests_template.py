import json
import subprocess
import re
import os
import glob
import resource
from io import StringIO
from difflib import SequenceMatcher
from colorama import Fore, Back

def get_difference(actual_output, expected_output):
    """
    Highlight differences between actual and expected output
    :param actual_output: The actual output string.
    :param expected_output: The expected output string.
    :return: A string with color-coded differences.
    """
    # Create a StringIO object to capture output
    output = StringIO()

    # Display Color Coding
    output.write(f"{Back.LIGHTRED_EX}{Fore.BLACK} Delete {Back.RESET} ")
    output.write(f"{Back.LIGHTGREEN_EX}{Fore.BLACK} Insert {Back.RESET}\n\n")
    
    actual = actual_output.split()

    matcher = SequenceMatcher(None, actual_output, expected_output)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        text = ''
        if tag == 'equal':
            text = Fore.BLACK + actual_output[i1:i2]
        elif tag == 'replace':
            red_text = Back.LIGHTRED_EX + actual_output[i1:i2]
            grn_text = Back.LIGHTGREEN_EX + expected_output[j1:j2]
            text = red_text + grn_text
        elif tag == 'delete':
            text = Back.LIGHTRED_EX + actual_output[i1:i2]
        elif tag == 'insert':
            text = Back.LIGHTGREEN_EX + expected_output[j1:j2]
        
        output.write(text + Back.RESET)

    # Get the string from the StringIO object
    return output.getvalue()

def lenient_whitespace(text):
    return re.sub(r'\s+', '', text).strip()

def limit_resources():
    """Limit CPU & memory usage of the student script."""
    # Set CPU time limit (e.g., 5 seconds)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    
    # Set memory limit (e.g., 128MB)
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024 * 1024, 128 * 1024 * 1024))
    
    # Restrict user permissions
    nobody_uid = 65534  # 'nobody' user on most Linux systems
    os.setuid(nobody_uid)

def compile_and_run(student_cpp_path, input_data):
    executable = "student_program"
    
    cpp_files = glob.glob("**/*.cpp", recursive=True)

    if not cpp_files:
        raise FileNotFoundError("No .cpp files found!")
    
    compile_process = subprocess.run(
    ["g++", "-o", "student_program"] + cpp_files,
    capture_output=True,
    text=True
    )
    
    if compile_process.returncode != 0:
        return "", compile_process.stderr
    
    try:
        run_process = subprocess.Popen(
            ["./" + executable],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=limit_resources
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
    student_filepath = "LabX.cpp"
    
    test_cases = []
    
    test_results = []
    total_score = 0.0
    max_score = 100
    points_per_question = max_score/len(test_cases)
    rounded_points = round(points_per_question, 2)

    for i, (input_file, output_file, visibility) in enumerate(test_cases):
        with open(input_file, 'r') as f:
            input_data = f.read()
        
        with open(output_file, 'r') as f:
            expected_output = f.read()
        
        student_output, errors = compile_and_run(student_filepath, input_data)

        if errors:
            # If there's an error, the test fails
            if (visibility == "visible"):
                test_results.append({
                    "score": 0.0,
                    "max_score": rounded_points,
                    "status": "failed",
                    "name": f"{student_filepath} Test Case {i+1}",
                    "output": f"Inputs:\n\n{input_data}\n\nError in your script:\n{errors}",
                    "visibility": "visible"
                })
            elif (visibility == "hidden"):
                test_results.append({
                    "score": 0.0,
                    "max_score": rounded_points,
                    "status": "failed",
                    "name": f"{student_filepath} Test Case {i+1} (Hidden)",
                    "output": f"Error in your script:\n{errors}",
                    "visibility": "visible"
                })
                # FOR TA ONLY VIEWING ON GRADESCOPE, USEFUL FOR DEBUGGING
                test_results.append({
                    "score": 0.0,
                    "max_score": 0.0,
                    "status": "failed",
                    "name": f"TA ONLY - {student_filepath} Test Case {i+1} (Hidden)",
                    "output": f"Inputs:\n\n{input_data}\n\nError in their script:\n{errors}",
                    "visibility": "hidden"
                })
        else:
            if compare_outputs(student_output, expected_output):
                # Test passed
                if (visibility == "visible"):
                    test_results.append({
                        "score": rounded_points,
                        "max_score": rounded_points,
                        "status": "passed",
                        "name": f"{student_filepath} Test Case {i+1}",
                        "output": "Correct output.",
                        "visibility": "visible"
                    })
                elif (visibility == "hidden"):
                    test_results.append({
                        "score": rounded_points,
                        "max_score": rounded_points,
                        "status": "passed",
                        "name": f"{student_filepath} Test Case {i+1} (Hidden)",
                        "output": "Passed hidden test case.",
                        "visibility": "visible"
                    })
                total_score += points_per_question
            else:
                # Test failed
                if (visibility == "visible"):
                    test_results.append({
                        "score": 0.0,
                        "max_score": rounded_points,
                        "status": "failed",
                        "name": f"{student_filepath} Test Case {i+1}",
                        "output": f"{Fore.MAGENTA}Inputs:{Fore.RESET}\n\n{input_data}\n\n{Fore.MAGENTA}Expected:{Fore.RESET}\n\n{expected_output}\n\n{Fore.MAGENTA}Got:{Fore.RESET}\n\n{student_output}\n\n{Fore.MAGENTA}Difference:{Fore.RESET} {get_difference(student_output, expected_output)}",
                        "output_format": "ansi",
                        "visibility": "visible"
                    })
                elif (visibility == "hidden"):
                    test_results.append({
                        "score": 0.0,
                        "max_score": rounded_points,
                        "status": "failed",
                        "name": f"{student_filepath} Test Case {i+1} (Hidden)",
                        "output": f"Failed hidden test case, check your logic!\n\n(This means that you need to further test your code)",
                        "output_format": "text",
                        "visibility": "visible"
                    })
                    # FOR TA ONLY VIEWING ON GRADESCOPE, USEFUL FOR DEBUGGING
                    test_results.append({
                        "score": 0.0,
                        "max_score": 0.0,
                        "status": "failed",
                        "name": f"TA ONLY - {student_filepath} Test Case {i+1} (Hidden)",
                        "output": f"{Fore.MAGENTA}Inputs:{Fore.RESET}\n\n{input_data}\n\n{Fore.MAGENTA}Expected:{Fore.RESET}\n\n{expected_output}\n\n{Fore.MAGENTA}Got:{Fore.RESET}\n\n{student_output}\n\n{Fore.MAGENTA}Difference:{Fore.RESET} {get_difference(student_output, expected_output)}",
                        "output_format": "ansi",
                        "visibility": "hidden"
                    })
    
    # Create the output dictionary
    results = {
        "score": round(total_score),
        "output": "Autograder results below:\nInputs - what we are inputting into your program under test\nExpected - what we expect your program to output\nGot - what your program actually outputted based on the inputs\nDifference - this shows the difference between your output and the expected output",
        "visibility": "visible",
        "stdout_visibility": "visible",
        "tests": test_results
    }

    # Write the results to a JSON file
    with open('/autograder/results/results.json', 'w') as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    grade()
