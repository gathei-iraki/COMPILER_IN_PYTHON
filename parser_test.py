from basic import Lexer, Parser


def run_parser_tests():
    test_cases = [
        ("20-1*(4/3)+2+(2+4)", "[(((INT:20, MINUS, (INT:1, MUL, (INT:4, DIV, INT:3))), PLUS, INT:2), PLUS, (INT:2, PLUS, INT:4))]"),
        ("print(hello)", "[(PRINT: (VAR_ACCESS: IDENTIFIER:hello))]"),
        ("var x = 5", "[(VAR_ASSIGN: IDENTIFIER:x, INT:5)]"),
        ("let y = 10", "[(VAR_ASSIGN: IDENTIFIER:y, INT:10)]"),
        ('print("Hello, World!")', '[(PRINT: (STRING:"Hello, World!"))]')
    ]

    for i, (input_text, expected_output) in enumerate(test_cases):
        lexer = Lexer("<stdin>", input_text)
        tokens, error = lexer.make_tokens()
        if error:
            print(f"Test {i + 1} failed: Lexer error: {error.as_string()}")
            continue

        parser = Parser(tokens)
        ast = parser.parse()

        if ast.error:
            print(f"Test {i + 1} failed: Parser error: {ast.error.as_string()}")
        else:
            result = repr(ast.node)
            if result == expected_output:
                print(f"Test {i + 1} passed")
            else:
                print(f"Test {i + 1} failed: expected {expected_output}, got {result}")


run_parser_tests()
