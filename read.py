from Classes import *
import copy
import re
import math


def add_constraint(constraints, constraint, variables=None):

    if not isinstance(constraint, Constraint):
        if callable(constraint):
            constraint = FunctionConstraint(constraint)
        else:
            msg = "Constraints must be instances of subclasses " "of the Constraint class"
            raise ValueError(msg)
    constraints.append((constraint, variables))


def add_var(variables, variable, domain):

    if variable in variables:
        msg = "Tried to insert duplicated variable %s" % repr(variable)
        raise ValueError(msg)
    if isinstance(domain, Domain):
        domain = copy.deepcopy(domain)
    elif hasattr(domain, "__getitem__"):
        domain = Domain(domain)
    else:
        msg = "Domains must be instances of subclasses of the Domain class"
        raise TypeError(msg)
    if not domain:
        raise ValueError("Domain is empty")
    variables[variable] = domain


def check_lists(list1, list2):

    for item in list1:
        for item2 in list2:
            if item.lower() == item2.lower():
                return item
    return None


def split_array(array, split_string):

    try:
        split_index = array.index(split_string)
        return array[:split_index], array[split_index+1:]
    except ValueError:
        # Raise an exception if the split string is not found in the array
        raise ValueError("Split string not found in array")


def get_array(attribute1, attribute2=None):

    if attribute2:
        return [attribute1, attribute2]
    return [attribute1]


def get_constraints(text, D, p_constraints, houses_no):

    attributes = sum(list(D.values()), [])
    attributes = [string.lower() for string in attributes]
    sentences = text.split(".")
    first = 1
    middle = int(math.ceil(houses_no / 2))
    last = houses_no
    for i in range(len(sentences)):
        words = sentences[i].split()
        words = [string.lower() for string in words]
        if ("right" in words):
            attribute_value_1 = check_lists(words, attributes).lower()
            half_1, half_2 = split_array(words, attribute_value_1)
            attribute_value_2 = check_lists(half_2, attributes).lower()
            add_constraint(p_constraints, lambda a, b: a == b - 1,
                           get_array(attribute_value_2, attribute_value_1))
        elif ("left" in words):
            attribute_value_1 = check_lists(words, attributes).lower()
            half_1, half_2 = split_array(words, attribute_value_1)
            attribute_value_2 = check_lists(half_2, attributes).lower()
            add_constraint(p_constraints, lambda a, b: a == b - 1,
                           get_array(attribute_value_1, attribute_value_2))
        elif ("next" in words):
            attribute_value_1 = check_lists(words, attributes).lower()
            half_1, half_2 = split_array(words, attribute_value_1)
            attribute_value_2 = check_lists(half_2, attributes).lower()
            add_constraint(p_constraints, lambda a, b: a == b - 1 or a == b + 1,
                           get_array(attribute_value_1, attribute_value_2))
        elif ("notnext" in words):
            attribute_value_1 = check_lists(words, attributes).lower()
            half_1, half_2 = split_array(words, attribute_value_1)
            attribute_value_2 = check_lists(half_2, attributes).lower()
            add_constraint(p_constraints, lambda a, b: a != b - 1 and a != b + 1,
                           get_array(attribute_value_1, attribute_value_2))
        elif ("first" in words):
            attribute_value = check_lists(words, attributes).lower()
            add_constraint(p_constraints, lambda a: a ==
                           first, get_array(attribute_value))
        elif ("middle" in words):
            attribute_value = check_lists(words, attributes).lower()
            add_constraint(p_constraints, lambda a: a ==
                           middle, get_array(attribute_value))
        elif ("last" in words):
            attribute_value = check_lists(words, attributes).lower()
            add_constraint(p_constraints, lambda a: a ==
                           last, get_array(attribute_value))
        elif ("fourth" in words):
            attribute_value = check_lists(words, attributes).lower()
            add_constraint(p_constraints, lambda a: a ==
                           4, get_array(attribute_value))
        else:
            attribute_value_1 = check_lists(words, attributes).lower()
            half_1, half_2 = split_array(words, attribute_value_1)
            attribute_value_2 = check_lists(half_2, attributes).lower()
            add_constraint(p_constraints, lambda a, b: a == b,
                           get_array(attribute_value_1, attribute_value_2))

    return p_constraints


def prepare_data(filename):

    formated_variables = {}
    formated_constraints = []

    with open(filename, 'r') as file:
        content = file.read()

    A_str = re.search(r"A = (\[.*?\])", content, re.DOTALL).group(1)
    D_str = re.search(r"D = ({.*?})", content, re.DOTALL).group(1)
    Text = re.search(r"Text = \"(.+?)\"", content, re.DOTALL).group(1)
    Q = re.search(r"Q = \"(.+?)\"", content).group(1)

    Text = Text.replace('\\', '')

    D = None
    A = None

    lcls = locals()

    exec("A = " + A_str, globals(), lcls)
    A = lcls["A"]
    exec("D = " + D_str, globals(), lcls)
    D = lcls["D"]

    formated_constraints = []

    D = {key.lower(): [string.lower()
                       for string in value] for key, value in D.items()}

    houses_no = len(list(D.values())[0])

    for values in D.values():
        for value in values:
            add_var(formated_variables, value, range(1, houses_no + 1))
        add_constraint(formated_constraints, AllDifferentConstraint(), values)

    get_constraints(Text, D, formated_constraints, houses_no)

    return formated_variables, formated_constraints, D, A, Q
