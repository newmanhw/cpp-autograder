import os
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import time


def compile_solution(solution_path):
    exe_path = os.path.splitext(solution_path)[0]
    try:
        subprocess.run(["g++", solution_path, "-o", exe_path], check=True)
        print(f"Compiled {solution_path} successfully.")
        return exe_path
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")
        return None

def run_solution(input_file, output_dir, section_number, exe_path):
    if not exe_path:
        return
    output_file = os.path.join(output_dir, f"output{section_number}.txt")
    try:
        result = subprocess.run(
            [exe_path],
            stdin=open(input_file, 'r'),
            stdout=subprocess.PIPE,
            text=True
        )
        output_content = result.stdout.rstrip()
        with open(output_file, 'w') as outfile:
            outfile.write(output_content)
        print(f"Solution output saved to {output_file}")
    except Exception as e:
        print(f"Error running solution executable: {e}")

def split_file_and_run(input_file, exe_path):
    output_dir = "./build/tests/"
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    section_number = 1
    section_lines = []

    for line in lines:
        if line.strip() == "---":
            if section_lines:
                output_file = os.path.join(output_dir, f"input{section_number}.txt")
                with open(output_file, 'w') as section_file:
                    section_file.write(''.join([l.rstrip() + '\n' for l in section_lines]).strip('\n'))
                print(f"Written section {section_number} to {output_file}")
                run_solution(output_file, output_dir, section_number, exe_path)
                section_number += 1
                section_lines = []
        else:
            section_lines.append(line)

    if section_lines:
        output_file = os.path.join(output_dir, f"input{section_number}.txt")
        with open(output_file, 'w') as section_file:
            section_file.write(''.join([l.rstrip() + '\n' for l in section_lines]).strip('\n'))
        print(f"Written section {section_number} to {output_file}")
        run_solution(output_file, output_dir, section_number, exe_path)

def create_grading_script(student_filepath):
    test_folder = "./build/tests/"
    files = [f for f in os.listdir(test_folder) if os.path.isfile(os.path.join(test_folder, f))]
    num_test_cases = len(files) // 2 if len(files) > 1 else 0

    test_cases = []
    for i in range(1, num_test_cases + 1):
        test_cases.append(f'("tests/input{i}.txt", "tests/output{i}.txt", "visible")')

    with open("./template_files/run_tests_template.py") as f:
        script_content = f.read()

    student_filepath = os.path.basename(student_filepath)
    script_content = script_content.replace(
        'student_filepath = \"LabX.cpp\"',
        f'student_filepath = \"{student_filepath}\"'
    )

    new_test_cases_str = "test_cases = [\n    " + ",\n    ".join(test_cases) + "\n]"
    script_content = script_content.replace(
        "test_cases = []",
        new_test_cases_str
    )

    with open("./build/run_tests_final.py", "w") as f:
        f.write(script_content)

    print("Updated Grading Script")

def modify_shell_script(student_filepath):
    student_filepath = os.path.basename(student_filepath)
    with open("./template_files/run_autograder_template", "r") as f:
        autograder_script = f.read()

    autograder_script = autograder_script.replace(
        "cp /autograder/submission/ /autograder/source/",
        f'cp /autograder/submission/{student_filepath} /autograder/source/{student_filepath}'
    )

    with open("./build/run_autograder", "w") as f:
        f.write(autograder_script)

    print(f"Updated run_autograder with student file: {student_filepath}")

def select_input_file():
    file_path = filedialog.askopenfilename(title="Select Input File")
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)

def select_solution_file():
    file_path = filedialog.askopenfilename(title="Select Solution File", filetypes=[("C++ Files", "*.cpp")])
    solution_entry.delete(0, tk.END)
    solution_entry.insert(0, file_path)

def zip_build_folder():
    zip_path = "./autograder"
    shutil.make_archive(zip_path, 'zip', "./build")
    print(f"Created autograder.zip successfully.")

def clean_build_folder():
    build_path = "./build"
    if os.path.exists(build_path):
        shutil.rmtree(build_path) 

def run_script():
    input_file = input_entry.get()
    solution_file = solution_entry.get()
    
    if not input_file or not solution_file:
        messagebox.showerror("Error", "Please select both input and solution files.")
        return
    
    # close GUI
    root.destroy()  

    # create directories
    if not os.path.exists("./build"):
        os.makedirs("./build")

    if not os.path.exists("./build/tests"):
        os.makedirs("./build/tests")
    
    print("Generating files...")
    start_time = time.time()  
    exe_path = compile_solution(solution_file)
    split_file_and_run(input_file, exe_path)
    create_grading_script(solution_file)
    modify_shell_script(solution_file)
    shutil.copy("./template_files/setup.sh", "./build/setup.sh")
    shutil.copy("./template_files/requirements.txt", "./build/requirements.txt")
    print("File generation completed.")


    print("\nZipping files...")
    zip_build_folder()
    os.remove(exe_path)
    clean_build_folder()
    end_time = time.time()  
    print("Success! Upload autograder.zip to Gradescope.")
    elapsed_time = end_time - start_time
    print(f"\nAll files generated in {elapsed_time:.2f} seconds.")


# GUI driver code
root = tk.Tk()
root.title("Generate Test Case Files for Gradescope")

tk.Label(root, text="Test Case .txt File:").grid(row=0, column=0, padx=5, pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Solution File:").grid(row=1, column=0, padx=5, pady=5)
solution_entry = tk.Entry(root, width=50)
solution_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=select_solution_file).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Run", command=run_script).grid(row=2, column=1, pady=10)

root.mainloop()
