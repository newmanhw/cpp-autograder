# C++ Gradescope Autograder
## Author: Newman Waters

### Usage:
First fork the repository, then clone onto a Unix-based machine **(tested for WSL)**.
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