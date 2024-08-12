import basic

while True:
	text = input('basic > ')
	if text.strip() == "":
		continue

	ast, error, tokens = basic.run('<stdin>', text)

	if error:
		print(error.as_string())
	else:
		print("Tokens: ")
		for token in tokens:
			print(token)
		print("\nParse Tree: ")
		print(ast)
