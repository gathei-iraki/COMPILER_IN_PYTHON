from basic import Lexer


def run_lexer_tests():
    tests = [
        ("1234", "INT:1234"),
        ("12.34", "FLOAT:12.34"),
        ("+", "PLUS"),
        ("-", "MINUS"),
        ("*", "MUL"),
        ("/", "DIV"),
        ("(", "LPAREN"),
        (")", "RPAREN"),
        ('"Hello, World!"', 'STRING:"Hello, World!"'),
        ("var x = 5", "KEYWORD:var IDENTIFIER:x EQ INT:5"),
        ("let y = 10", "KEYWORD:let IDENTIFIER:y EQ INT:10"),
        ("print(x)", "KEYWORD:print LPAREN IDENTIFIER:x RPAREN"),
    ]

    for i, (input_text, expected_output) in enumerate(tests):
        lexer = Lexer('<stdin>', input_text)
        tokens, error = lexer.make_tokens()

        if error:
            print(f"Test {i + 1} failed: {error.as_string()}")
        else:
            tokens = [token for token in tokens if token.type != 'EOF']
            result = ' '.join([str(token) for token in tokens])
            if result == expected_output:
                print(f"Test {i + 1} passed")
            else:
                print(f"Test {i + 1} failed: expected '{expected_output}', got '{result}'")


if __name__ == "__main__":
    run_lexer_tests()
