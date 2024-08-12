#######################################
# IMPORTS
#######################################
import string
from strings_with_arrows import *

#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'
ALPHABET = string.ascii_letters

#######################################
# ERRORS
#######################################


class Error:
	def __init__(self, pos_start, pos_end, error_name, details):
		self.pos_start = pos_start
		self.pos_end = pos_end
		self.error_name = error_name
		self.details = details
	
	def as_string(self):
		result  = f'{self.error_name}: {self.details}\n'
		result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result


class IllegalCharError(Error):
	def __init__(self, pos_start, pos_end, details):
		super().__init__(pos_start, pos_end, 'Illegal Character', details)


class InvalidSyntaxError(Error):
	def __init__(self, pos_start, pos_end, details=''):
		super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

#######################################
# POSITION
#######################################


class Position:
		def __init__(self, idx, ln, col, fn, ftxt):
				self.idx = idx
				self.ln = ln
				self.col = col
				self.fn = fn
				self.ftxt = ftxt

		def advance(self, current_char=None):
				self.idx += 1
				self.col += 1

				if current_char == '\n':
						self.ln += 1
						self.col = 0

				return self

		def copy(self):
				return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT			= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_SCOLON   = ':'
TT_EOF		= 'EOF'
TT_EQ       = 'EQ'
TT_NEWLINE  = 'NEWLINE'
TT_DEDENT   = 'DEDENT'

TT_KEYWORD = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_STRING = 'STRING'

KEYWORDS = {
	'var': 'var',
	'int': "int",
	'print': "print",
	'let': "let",
	'while': "while"
}

class Token:
		def __init__(self, type_, value=None, pos_start=None, pos_end=None):
				self.type = type_
				self.value = value

				if pos_start:
					self.pos_start = pos_start.copy()
					self.pos_end = pos_start.copy()
					self.pos_end.advance()

				if pos_end:
					self.pos_end = pos_end

		def matches(self, type_, value):
			return self.type == type_ and self.value == value

		def __repr__(self):
				if self.value: return f'{self.type}:{self.value}'
				return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
		def __init__(self, fn, text):
				self.fn = fn
				self.text = text
				self.pos = Position(-1, 0, -1, fn, text)
				self.current_char = None
				self.advance()
		
		def advance(self):
				self.pos.advance(self.current_char)
				self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

		def make_tokens(self):
				tokens = []

				while self.current_char != None:
					if self.current_char in ' \t':
						self.advance()
					elif self.current_char in DIGITS:
						tokens.append(self.make_number())
					elif self.current_char == '+':
						tokens.append(Token(TT_PLUS, pos_start=self.pos))
						self.advance()
					elif self.current_char == '-':
						tokens.append(Token(TT_MINUS, pos_start=self.pos))
						self.advance()
					elif self.current_char == '*':
						tokens.append(Token(TT_MUL, pos_start=self.pos))
						self.advance()
					elif self.current_char == '/':
						tokens.append(Token(TT_DIV, pos_start=self.pos))
						self.advance()
					elif self.current_char == '(':
						tokens.append(Token(TT_LPAREN, pos_start=self.pos))
						self.advance()
					elif self.current_char == ')':
						tokens.append(Token(TT_RPAREN, pos_start=self.pos))
						self.advance()
					elif self.current_char == ':':
						tokens.append(Token(TT_SCOLON, pos_start=self.pos))
						self.advance()
					elif self.current_char == '=':
						tokens.append(Token(TT_EQ, pos_start=self.pos))
						self.advance()
					elif self.current_char == '"':
						tokens.append(self.make_string())
					elif self.current_char.isalpha():
						tokens.append(self.make_identifier())
						
					else:
						pos_start = self.pos.copy()
						char = self.current_char
						self.advance()
						return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

				tokens.append(Token(TT_EOF, pos_start=self.pos))
				return tokens, None

		def make_identifier(self):
				identifier_str = ''
				pos_start = self.pos.copy()

				while self.current_char is not None and (self.current_char.isalnum() or self.current_char ==  '_'):
						identifier_str += self.current_char
						self.advance()
				tok_type = TT_KEYWORD if identifier_str in KEYWORDS else TT_IDENTIFIER
				return Token(tok_type, identifier_str, pos_start, self.pos)
            
            
		def make_number(self):
				num_str = ''
				dot_count = 0
				pos_start = self.pos.copy()

				while self.current_char != None and self.current_char in DIGITS + '.':
						if self.current_char == '.':
								if dot_count == 1: break
								dot_count += 1
								num_str += '.'
						else:
								num_str += self.current_char
						self.advance()

				if dot_count == 0:
						return Token(TT_INT, int(num_str), pos_start, self.pos)
				else:
						return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

		def make_string(self):
			str_value = ''
			pos_start = self.pos.copy()
			escape_character = False
			self.advance()
   
			escape_characters = {
				'n': '\n',
				't': '\t'
            }
			while self.current_char is not None and (self.current_char != '"' or escape_character):
				if escape_character:
					str_value += escape_characters.get(self.current_char, self.current_char)
					escape_character = False
				else:
					if self.current_char == '\\':
						escape_character = True
					else:
						str_value += self.current_char
				self.advance()
				escape_character = False

			self.advance()
			return Token(TT_STRING, '"' + str_value + '"', pos_start, self.pos)

#######################################
# AST NODES
#######################################


class NumberNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'{self.tok}'


class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'


class VarAssignNode:
	def __init__(self, var_name, value_node):
		self.var_name = var_name
		self.value_node = value_node

	def __repr__(self):
		return f'(VAR_ASSIGN: {self.var_name}, {self.value_node})'


class VarAccessNode:
	def __init__(self, var_name):
		self.var_name = var_name

	def __repr__(self):
		return f'(VAR_ACCESS: {self.var_name})'


class StringNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'({self.tok})'


class WhileNode:
	def __init__(self, condition_node, body_node):
		self.condition_node = condition_node
		self.body_node = body_node

	def __repr__(self):
		return f'(WHILE {self.condition_node} : {self.body_node})'


class PrintNode:
	def __init__(self, value_node):
		self.value_node = value_node

	def __repr__(self):
		return f'(PRINT: {self.value_node})'


class EmptyNode:
	def __repr__(self):
		return '(EMPTY)'


#######################################
# PARSE RESULT
#######################################

class ParseResult:
	def __init__(self):
		self.error = None
		self.node = None
		self.advance_count = 0
		self.to_reverse_count = 0

	def register_advancement(self):
		self.advance_count += 1

	def register(self, res):
		self.advance_count += res.advance_count
		if res.error:
			self.error = res.error
		return res.node

	def success(self, node):
		self.node = node
		return self

	def failure(self, error):
		if not self.error or self.advance_count == 0:
			self.error = error
		return self

#######################################
# PARSER
#######################################


class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.tok_idx = -1
		self.advance()

	def advance(self):
		self.tok_idx += 1
		if self.tok_idx < len(self.tokens):
			self.current_tok = self.tokens[self.tok_idx]
		return self.current_tok

	def parse(self):
		res = self.statements()
		if not res.error and self.current_tok.type != TT_EOF:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected end of file"
			))
		return res

	def statements(self):
		res = ParseResult()
		statements = []
		pos_start = self.current_tok.pos_start.copy()
  
		while self.current_tok.type != TT_EOF:
			stmt = res.register(self.statement())
			if res.error:
				return res
			statements.append(stmt)
			self.advance()

		return res.success(statements)

	def statement(self):
		res = ParseResult()
		pos_start = self.current_tok.pos_start.copy()

		if self.current_tok.matches(TT_KEYWORD, 'let'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected Identifier"
                ))

			var_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_EQ:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
                ))

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error:
				return res
			return res.success(VarAssignNode(var_name, expr))

		if self.current_tok.matches(TT_KEYWORD, 'var'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_IDENTIFIER:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected Identifier"
                ))

			var_name = self.current_tok
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_EQ:
				return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '='"
                ))

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error:
				return res
			return res.success(VarAssignNode(var_name, expr))

		if self.current_tok.matches(TT_KEYWORD, 'print'):
			res.register_advancement()
			self.advance()

			if self.current_tok.type != TT_LPAREN:
				return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected '('"
                ))

			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error:
				return res
			if self.current_tok.type != TT_RPAREN:
				return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
                ))

			res.register_advancement()
			self.advance()
			return res.success(PrintNode(expr))

		if self.current_tok.matches(TT_KEYWORD, 'while'):
			res.register_advancement()
			self.advance()

			condition = res.register(self.expr())
			if res.error: return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected condition after 'while'"
			))

			res.register_advancement()
			self.advance()

			condition = res.register(self.expr())
			if res.error:
				return res

			if not self.current_tok.type == TT_SCOLON:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ':' after condition"
				))

			res.register_advancement()
			self.advance()

			if self.current_tok.type == TT_NEWLINE:
				res.register_advancement()
				self.advance()
				body = res.register(self.statements())
				if res.error: return res
				if self.current_tok.type != TT_DEDENT:
					return res.failure(InvalidSyntaxError(
						self.current_tok.pos_start, self.current_tok.pos_end,
						"Expected dedent after block"
					))
				res.register_advancement()
				self.advance()
			else:
				body = res.register(self.statement())
				if res.error: return res
			return res.success(WhileNode(condition, body))

		expr = res.register(self.expr())
		if res.error:
			return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected Keyword, 'int', 'float', identifier, '+', '-', '('"
            ))
		return res.success(expr)

	def var_assign(self):
		res = ParseResult()
		if not self.current_tok.matches(TT_KEYWORD, 'let'):
			return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'let'"
            ))

		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_IDENTIFIER:
			return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected Identifier"
            ))

		var_name = self.current_tok
		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_EQ:
			return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '='"
            ))

		res.register_advancement()
		self.advance()
		expr = res.register(self.expr())
		if res.error:
			return res
		return res.success(VarAssignNode(var_name, expr))

	def print_statement(self):
		res = ParseResult()
		if not self.current_tok.matches(TT_KEYWORD, 'print'):
			return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected 'print'"
            ))

		res.register_advancement()
		self.advance()

		if self.current_tok.type != TT_LPAREN:
			return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected '('"
            ))

		res.register_advancement()
		self.advance()
		expr = res.register(self.expr())
		
		if res.error:
			return res
		if self.current_tok.type != TT_RPAREN:
			return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
				"Expected ')'"
            ))
		res.register_advancement()
		self.advance()
		return res.success(PrintNode(expr))

	def factor(self):
		res = ParseResult()
		tok = self.current_tok

		if tok.type in (TT_PLUS, TT_MINUS):
			res.register_advancement()
			self.advance()
			factor = res.register(self.factor())
			if res.error:
				return res
			return res.success(UnaryOpNode(tok, factor))
		
		elif tok.type in (TT_INT, TT_FLOAT):
			res.register_advancement()
			self.advance()
			return res.success(NumberNode(tok))

		elif tok.type == TT_LPAREN:
			res.register_advancement()
			self.advance()
			expr = res.register(self.expr())
			if res.error:
				return res
			if self.current_tok.type == TT_RPAREN:
				res.register_advancement()
				self.advance()
				return res.success(expr)
			else:
				return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Expected ')'"
				))

		elif tok.type == TT_IDENTIFIER:
			res.register_advancement()
			self.advance()
			return res.success(VarAccessNode(tok))

		elif tok.type == TT_STRING:
			res.register_advancement()
			self.advance()
			return res.success(StringNode(tok))
		
		return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int, float, Identifier, string, '+', '-', or '('"
		))

	def term(self):
		return self.bin_op(self.factor, (TT_MUL, TT_DIV))

	def expr(self):
		return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

	###################################

	def bin_op(self, func, ops):
		res = ParseResult()
		left = res.register(func())
		if res.error: return res

		while self.current_tok.type in ops:
			op_tok = self.current_tok
			res.register_advancement()
			self.advance()
			right = res.register(func())
			if res.error: return res
			left = BinOpNode(left, op_tok, right)

		return res.success(left)

#######################################
# RUN
#######################################

def run(fn, text, show_tokens=False):
    # Generate tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error, tokens

    # Generate AST
    parser = Parser(tokens)
    ast = parser.parse()

    if ast.error:
        return None, ast.error, tokens

    return ast.node, None, tokens
