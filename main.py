from icg import IntermediateCodeGenerator

def read_expressions_from_file(filename):
    with open(filename, 'r') as file:
        return file.read().splitlines()

def main():
    icg = IntermediateCodeGenerator()
    expressions = read_expressions_from_file('input.txt')
    
    for expression in expressions:
        if expression.strip() == 'exit':
            break
        quadruples, tokens, ast = icg.generate_quadruples(expression)
        
        print(f"Input Expression: {expression}\n")
        
        print("Lexer Output (Tokens):")
        for token in tokens:
            print(token)
        
        print("\nParser Output (AST):")
        print(ast)
        
        print("\nICG Output (Quadruples):")
        for quad in quadruples:
            print(quad)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
