# eEinstein's riddle
A solution for the common CSP named Einstein's Riddle using backtracking + AC-3 and MRV heuristics

Defined a Domain class that represents the domain of a variable in the CSP problem. A domain is a set of values that a variable can be attributed with.

I defined a Constraint Class to represent the various constraints existent in the CSP, with two specific constraints: FunctionConstraint and allDifferentConstraints. Both of these 2 are derivates of the Constraint Class and are used to define every possible constraint: the first one is used to define any kind of positional constraints and the later one is used to make sure that all the values of a set of variables are different from one another.

For test cases I used the classic Einstein Riddle with 5 attributes, with 5 possible values each and 5 slots (houses). Along with the base test case, I used some others with different numbers of variables and slots.

For optimizations I used different methods:
  * MRV Heuristic: this heuristic is used to sort the variables that chooses the variable with the least possible values in it's domain.
  * Degree Heuristic: this is another sorting heuristic, that in case of an equality in the MRV Heuristic, will choose the variable that is implicated in more constraints.
  * Forward Checking: This is a constraint propagation technique that, after assigment of value to a variable, checks all constraints involving the variable and removes from the domains of unassigned variables any value that cannot be used in a valid solution
  * AC-3 (Arc Consistency 3): Improves the efficiency of backtracking by reducing the size of the search space. AC-3 works by eliminating values that are not consistent with the constraints from the domains of variables before starting the backtracking search. This is achieved by checking and ensuring "arc consistency" for each pair of variables linked by a constraint.

Performance comparison for the default test file (in.txt):

* Basic Backtracking: Runtime = 0.3138012229974265 | No of cycles = 31922
* AC-3 Backtracking: Runtime = 0.028189860000566114 | No of cycles = 1945
* Backtracking with Forward Checking: Runtime = 0.0060381430012057535 | No of cycles = 143


