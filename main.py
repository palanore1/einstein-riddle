import sys
from timeit import default_timer as timer
from read import prepare_data
from Classes import *

'''
======================== FUNCTIONS ========================
'''


def get_args(domains, constraints):

    vconstraints = {}
    for variable in domains:
        vconstraints[variable] = []
    for constraint, variables in constraints:
        for variable in variables:
            vconstraints[variable].append((constraint, variables))
    for constraint, variables in constraints[:]:
        constraint.preProcess(variables, domains, constraints, vconstraints)
    for domain in domains.values():
        domain.resetState()
        if not domain:
            return None, None, None
    return vconstraints


def recursive_backtracking(solutions, domains, vconstraints, assignments, forwardcheck=True):

    recursive_backtracking.count += 1
    # Degree and Minimum Remaing Values (MRV) heuristics
    lst = [
        (-len(vconstraints[variable]), len(domains[variable]), variable)
        for variable in domains
    ]
    lst.sort()
    for item in lst:
        if item[-1] not in assignments:
            # Found an unassigned variable. Let's go.
            break
    else:
        # No unassigned variables. We've got a solution.
        solutions.append(assignments.copy())
        return solutions

    variable = item[-1]
    assignments[variable] = None

    if forwardcheck:
        pushdomains = [domains[x] for x in domains if x not in assignments]
    else:
        pushdomains = None

    for value in domains[variable]:
        assignments[variable] = value
        if pushdomains:
            for domain in pushdomains:
                domain.pushState()
        for constraint, variables in vconstraints[variable]:
            if not constraint(variables, domains, assignments, pushdomains):
                # Value is not good.
                break
        else:
            # Value is good. Recurse and get next variable.
            recursive_backtracking(
                solutions, domains, vconstraints, assignments, forwardcheck)
            if solutions:
                return solutions
        if pushdomains:
            for domain in pushdomains:
                domain.popState()
    del assignments[variable]
    return solutions


# Print function
def order(key, domain):

    for position, array in enumerate(domain.values()):
        if key in array:
            return position


def print_v2(solution, domain):

    ordered = [
        sorted([k for k, v in solution.items() if v == i],
               key=lambda x: order(x, domain))
        for i in range(1, max(solution.values())+1)
    ]
    # transpose & format output
    for i in map(list, zip(*ordered)):
        print("{:10s} {:10s} {:10s} {:10s} {:10s}".format(*i))


'''
==================================== AC-3 =====================================
'''


def is_constraint_satisfied(constraint, variables, assignments):

    constraint_obj, constraint_vars = constraint
    assigned_vars = {var: assignments[var]
                     for var in constraint_vars if var in assignments}
    return constraint_obj(constraint_vars, variables, assigned_vars, forwardcheck=False)


def initialize_arcs(constraints):

    arcs = []
    for constraint in constraints:
        _, constraint_vars = constraint
        for var1 in constraint_vars:
            for var2 in constraint_vars:
                if var1 != var2:
                    arcs.append((var1, var2, constraint))
    return arcs


def ac3(variables, domains, constraints):
    queue = [(var1, var2, constraint) for constraint in constraints for var1 in constraint[1]
             for var2 in constraint[1] if var1 != var2]

    while queue:
        var1, var2, constraint = queue.pop(0)
        if revise(domains, var1, var2, constraint):
            if not domains[var1]:
                return False
            for neighbor_constraint in constraints:
                if var1 in neighbor_constraint[1]:
                    for neighbor in neighbor_constraint[1]:
                        if neighbor != var1 and (neighbor, var1, neighbor_constraint) not in queue and (var1, neighbor, neighbor_constraint) not in queue:
                            queue.append((neighbor, var1, neighbor_constraint))
    return True


def revise(domains, var1, var2, constraint):

    revised = False
    domain1 = domains[var1]
    for value1 in domain1[:]:
        assignments = {var1: value1}
        is_satisfied = False
        for value2 in domains[var2]:
            assignments[var2] = value2
            if is_constraint_satisfied(constraint, domains, assignments):
                is_satisfied = True
                break
        if not is_satisfied:
            domain1.remove(value1)
            revised = True
    return revised


'''
======================== MAIN ========================
'''


def main():
    args = sys.argv[1:]
    start = timer()
    how = None
    forwardcheck = True
    ac3_result = None
    recursive_backtracking.count = 0

    try:
        variables, constraints, domains, A, Q = prepare_data(
            './inputs/' + args[0])
        try:
            how = args[1]
        except IndexError:
            print("ERROR: Only 1 arg !")
    except IndexError:
        print("ERROR: Args not sent correctly !")
    except FileNotFoundError:
        print("ERROR: File not found !")

    # print(variables)
    # print(A)
    # print(Q)
    # print(domains)

    A = [string.lower() for string in A]
    main_attr = domains[A[0]]

    val_list = [element for lst in list(domains.values()) for element in lst]
    look_for = list(set(val_list) & {element.lower()
                    for element in set(Q.split(' '))})[0]
    vconstraints = get_args(variables, constraints)

    if how == 'fwd':
        forwardcheck = True
    elif how == 'normal':
        forwardcheck = False
    elif how == 'ac3':
        forwardcheck = False
        domains_ac3 = {var: values.copy() for var, values in variables.items()}
        ac3_result = ac3(variables, domains_ac3, constraints)

    if ac3_result == True:
        solution = recursive_backtracking(
            [], domains_ac3, vconstraints, {}, forwardcheck)[0]
    elif ac3_result == False:
        print("There is no solution for the given CSP.")
        return 0
    else:
        solution = recursive_backtracking(
            [], variables, vconstraints, {}, forwardcheck)[0]

    # Print the result (main attribute of the house where we found the object)
    house_no = solution[look_for]
    house = []
    for s in val_list:
        if solution[s] == house_no:
            house.append(s)
    # print(f'House no_{house_no}: {house}')
    # print_v2(solution, domains)

    answer = list(set(main_attr) & set(house))[0]

    end = timer()

    print(f'Answer = {answer}')
    print(f'Runtime = {end-start}')
    print(f'No of cycles = {recursive_backtracking.count}.')


if __name__ == '__main__':
    main()
