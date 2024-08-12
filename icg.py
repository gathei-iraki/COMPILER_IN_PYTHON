from quadruple import Quadruple
from basic import run, BinOpNode, NumberNode, VarAssignNode, VarAccessNode, PrintNode, WhileNode

class IntermediateCodeGenerator:
    def __init__(self):
        self.quadruples = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"T{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def generate_quadruples_from_ast(self, node):
        if isinstance(node, list):
            for sub_node in node:
                self.generate_quadruples_from_ast(sub_node)
        elif isinstance(node, BinOpNode):
            left = self.generate_quadruples_from_ast(node.left_node)
            right = self.generate_quadruples_from_ast(node.right_node)
            result = self.new_temp()
            self.quadruples.append(Quadruple(node.op_tok.type, left, right, result))
            return result
        elif isinstance(node, NumberNode):
            return node.tok.value
        elif isinstance(node, VarAssignNode):
            value = self.generate_quadruples_from_ast(node.value_node)
            self.quadruples.append(Quadruple('=', value, None, node.var_name.value))
            return node.var_name.value
        elif isinstance(node, VarAccessNode):
            return node.var_name.value
        elif isinstance(node, PrintNode):
            value = self.generate_quadruples_from_ast(node.value_node)
            self.quadruples.append(Quadruple('PRINT', value, None, None))
            return value
        elif isinstance(node, WhileNode):
            label_start = self.new_label()
            label_end = self.new_label()
            self.quadruples.append(Quadruple('LABEL', None, None, label_start))
            condition = self.generate_quadruples_from_ast(node.condition_node)
            self.quadruples.append(Quadruple('IF_FALSE', condition, None, label_end))
            self.generate_quadruples_from_ast(node.body_node)
            self.quadruples.append(Quadruple('GOTO', None, None, label_start))
            self.quadruples.append(Quadruple('LABEL', None, None, label_end))
        else:
            raise Exception(f"Unknown AST node: {node}")

    def generate_quadruples(self, expression):
        ast, error, tokens = run('<stdin>', expression)
        if error:
            print(error.as_string())
            return [], tokens, None
        self.generate_quadruples_from_ast(ast)
        return self.quadruples, tokens, ast
