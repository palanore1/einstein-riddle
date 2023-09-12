class Domain(list):

    def __init__(self, set):

        list.__init__(self, set)
        self._hidden = []
        self._states = []

    def resetState(self):

        self.extend(self._hidden)
        del self._hidden[:]
        del self._states[:]

    def pushState(self):

        self._states.append(len(self))

    def popState(self):

        diff = self._states.pop() - len(self)
        if diff:
            self.extend(self._hidden[-diff:])
            del self._hidden[-diff:]

    def hideValue(self, value):

        list.remove(self, value)
        self._hidden.append(value)


class Constraint(object):

    def __call__(self, variables, domains, assignments, forwardcheck=False):

        return True

    def preProcess(self, variables, domains, constraints, vconstraints):

        if len(variables) == 1:
            variable = variables[0]
            domain = domains[variable]
            for value in domain[:]:
                if not self(variables, domains, {variable: value}):
                    domain.remove(value)
            constraints.remove((self, variables))
            vconstraints[variable].remove((self, variables))

    def forwardCheck(self, variables, domains, assignments, _unassigned=None):

        unassignedvariable = _unassigned
        for variable in variables:
            if variable not in assignments:
                if unassignedvariable is _unassigned:
                    unassignedvariable = variable
                else:
                    break
        else:
            if unassignedvariable is not _unassigned:
                # Remove from the unassigned variable domain's all
                # values which break our variable's constraints.
                domain = domains[unassignedvariable]
                if domain:
                    for value in domain[:]:
                        assignments[unassignedvariable] = value
                        if not self(variables, domains, assignments):
                            domain.hideValue(value)
                    del assignments[unassignedvariable]
                if not domain:
                    return False
        return True


class FunctionConstraint(Constraint):

    def __init__(self, func, assigned=True):

        self._func = func
        self._assigned = assigned

    def __call__(
        self,
        variables,
        domains,
        assignments,
        forwardcheck=False,
        _unassigned=None,
    ):
        parms = [assignments.get(x, _unassigned) for x in variables]
        missing = parms.count(_unassigned)
        if missing:
            return (self._assigned or self._func(*parms)) and (
                not forwardcheck or
                missing != 1 or
                self.forwardCheck(variables, domains, assignments)
            )
        return self._func(*parms)


class AllDifferentConstraint(Constraint):

    def __call__(
        self,
        variables,
        domains,
        assignments,
        forwardcheck=False,
        _unassigned=None,
    ):
        seen = {}
        for variable in variables:
            value = assignments.get(variable, _unassigned)
            if value is not _unassigned:
                if value in seen:
                    return False
                seen[value] = True
        if forwardcheck:
            for variable in variables:
                if variable not in assignments:
                    domain = domains[variable]
                    for value in seen:
                        if value in domain:
                            domain.hideValue(value)
                            if not domain:
                                return False
        return True
