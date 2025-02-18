# C++ Gradescope Autograder
## Author: Newman Waters

This repository contains documentation, code, and test cases relating to the COP3502C Autograder. If planning to make changes to this project, make sure to follow the guide in [Git Workflow](#basic-git-workflow).

## Table of Contents
- [Usage](#usage)
- [About the Autograder](#about-cop3502c-autograder)
- [To-Do List](#to-do-list)
- [Git Workflow](#basic-git-workflow)
    - [Git Resources](#git-resources)

## Usage
Clone the repository onto a Unix-based machine **(tested for WSL)**.
```
cd cpp-autograder

// Add CPP Solution file to directory
// Add Test case file (ex): make sure to have "---" separating different test cases

//  Name: test_cases.txt
//     1 input1
//     2 ---
//     3 input2
//     4 ---
//     5 ...            -- add as many cases as you need
//     6 ---
//     7 inputN

python3 main.py
```

Add the test case file and solution file. Click Run.
This should generate a file called *autograder.zip*. 
Upload this zip file to Gradescope.
  
## About the Autograder
This autograder is written in Python to grade a student's submission to Gradescope. This is done through the following steps:

1. Gradescope creates a **Docker Container** to run the autograder in a controlled environment, where each submission runs in a fresh container. This ensures that the environment is isolated and identical for all students. The configuration we have set up is that this container is an **Ubuntu** machine, so we normalize any environment differences.
2. The autograder directory is set up as such **BEFORE** we upload it to Gradescope:
    
        /Lab XXX
            ├── setup.sh             # Script to install dependencies
            ├── run_autograder       # Main script to start run_tests.py
            ├── run_tests.py         # Python script that grades the submission
            ├── /tests               # Folder containing test cases
            ├── requirements.txt     # File containing any packages used (empty if none)
            # (ASSIGNMENT DEPENDENT):
            # Replaces run_tests.py if multi-part submission (LabX_A, LabX_B, etc.)
            ├── multiple_programs.py # Python script that grades the submission
3. We zip up all the files inside of the folder and name the zip file that is generated to `autograder.zip` -- <ins>it is very important that it is named this</ins>, since our python file generates files with this directory name.
4. Once the zip file is uploaded to Gradescope, it places all of our unzipped files into the directory `autograder/source/` of the Docker container so we want any student submissions to be moved here. The overall Docker directory system looks like this right now:

         /autograder
            ├── setup.sh             
            ├── run_autograder       
            /source
                ├── run_tests.py         
                ├── /tests               
                ├── requirements.txt
            /submission

6. The docker container by default starts in the directory `autograder/`, thus we need to change directories to run our grader:

        cd /autograder/source                 # Change directory to source files
        python3 multiple_programs.py          # or python3 run_tests.py

7. The Python scripts generate JSON files containing the results of the tests as per [Gradescope specifications - Output format](https://gradescope-autograders.readthedocs.io/en/latest/specs/). This will be placed as such in the new directory `/autograder/results/results.json` You can review exactly how this code works through the comments on the autograder template located in this repository. 

If you have any comments that could make this better, please submit an issue on this repository. Thank you!
