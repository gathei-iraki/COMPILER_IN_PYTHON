class Quadruple:
    def __init__(self, operator, arg1, arg2, result):
        self.operator = operator
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __repr__(self):
        return f"({self.operator}, {self.arg1}, {self.arg2}, {self.result})"
