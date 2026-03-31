import sys
import re

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if len(text) > 0 else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def string(self):
        result = ''
        self.advance() # " yi gec
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        self.advance() # kapanis " yi gec
        return ('STRING', result)

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return ('NUMBER', int(result))

    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        keywords = {
            'yazdir': 'YAZDIR',
            'koy': 'KOY',
            'eger': 'EGER',
            'ise': 'ISE',
            'bitti': 'BITTI',
            'dongu': 'DONGU',
            'oldukca': 'OLDUKCA',
        }
        token_type = keywords.get(result, 'ID')
        return (token_type, result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '"': return self.string()
            if self.current_char.isalpha(): return self.identifier()
            if self.current_char.isdigit(): return self.number()

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('EEQ', '==')
                return ('EQ', '=')

            if self.current_char == '>':
                self.advance()
                return ('GT', '>')
            if self.current_char == '<':
                self.advance()
                return ('LT', '<')
            if self.current_char == '+':
                self.advance()
                return ('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return ('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return ('MUL', '*')
            if self.current_char == '/':
                self.advance()
                return ('DIV', '/')
            if self.current_char == '(':
                self.advance()
                return ('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return ('RPAREN', ')')

            print(f"Hata: Tanimlanamayan Karakter '{self.current_char}'")
            sys.exit(1)

        return ('EOF', None)

    def tokenize(self):
        tokens = []
        while True:
            t = self.get_next_token()
            tokens.append(t)
            if t[0] == 'EOF': break
        return tokens

class Interpreter:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.variables = {}
        self.current_token = self.tokens[self.pos] if len(tokens) > 0 else ('EOF', None)

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = ('EOF', None)
        else:
            print(f"Sozdizimi (Syntax) Hatasi: Beklenen {token_type}, Bulunan {self.current_token[0]}")
            sys.exit(1)

    def factor(self):
        token = self.current_token
        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return token[1]
        elif token[0] == 'STRING':
            self.eat('STRING')
            return token[1]
        elif token[0] == 'ID':
            var_name = token[1]
            self.eat('ID')
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                print(f"Degisken Hatasi: '{var_name}' adinda bir degisken bulunamadi!")
                sys.exit(1)
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            result = self.expr()
            self.eat('RPAREN')
            return result
        else:
            print(f"Matematiksel Islem Bekleniyor, bulundu: {token[0]}")
            sys.exit(1)

    def term(self):
        result = self.factor()
        while self.current_token is not None and self.current_token[0] in ('MUL', 'DIV'):
            token = self.current_token
            if token[0] == 'MUL':
                self.eat('MUL')
                result = result * self.factor()
            elif token[0] == 'DIV':
                self.eat('DIV')
                result = result / self.factor()
        return result

    def expr(self):
        result = self.term()
        while self.current_token is not None and self.current_token[0] in ('PLUS', 'MINUS'):
            token = self.current_token
            if token[0] == 'PLUS':
                self.eat('PLUS')
                val = self.term()
                if isinstance(result, str) or isinstance(val, str):
                    result = str(result) + str(val)
                else:
                    result = result + val
            elif token[0] == 'MINUS':
                self.eat('MINUS')
                result = result - self.term()
        return result

    def condition(self):
        left = self.expr()
        op = self.current_token
        if op[0] in ('GT', 'LT', 'EEQ'):
            self.eat(op[0])
            right = self.expr()
            if op[0] == 'GT': return left > right
            if op[0] == 'LT': return left < right
            if op[0] == 'EEQ': return left == right
        return bool(left)

    def skip_block(self):
        depth = 1 # icerideyiz
        while depth > 0 and self.current_token[0] != 'EOF':
            if self.current_token[0] in ('EGER', 'DONGU'):
                depth += 1
            elif self.current_token[0] == 'BITTI':
                depth -= 1
                if depth == 0:
                    break
            self.eat(self.current_token[0])

    def parse_statement(self):
        if self.current_token[0] == 'YAZDIR':
            self.eat('YAZDIR')
            val = self.expr()
            print(val)
            
        elif self.current_token[0] == 'KOY':
            self.eat('KOY')
            var_name = self.current_token[1]
            self.eat('ID')
            self.eat('EQ')
            val = self.expr()
            self.variables[var_name] = val
            
        elif self.current_token[0] == 'EGER':
            self.eat('EGER')
            cond = self.condition()
            self.eat('ISE')
            
            if cond:
                while self.current_token[0] not in ('BITTI', 'EOF'):
                    self.parse_statement()
                self.eat('BITTI')
            else:
                self.skip_block()
                self.eat('BITTI')
            
        elif self.current_token[0] == 'DONGU':
            self.eat('DONGU')
            cond_start = self.pos
            
            while True:
                self.pos = cond_start
                self.current_token = self.tokens[self.pos]
                
                cond = self.condition()
                self.eat('OLDUKCA')
                
                if cond:
                    while self.current_token[0] not in ('BITTI', 'EOF'):
                        self.parse_statement()
                    # Dongu tamamlandi, tekrar basa saracagiz The While Loop continues.
                else:
                    self.skip_block()
                    self.eat('BITTI')
                    break
        else:
            # Beklenmeyen durumda atla (gelisme asamasinda guvenlik)
            self.eat(self.current_token[0])

    def run(self):
        while self.current_token[0] != 'EOF':
            self.parse_statement()

def calistir(dosya_yolu):
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            kod = f.read()
        lexer = Lexer(kod)
        tokens = lexer.tokenize()
        interpreter = Interpreter(tokens)
        interpreter.run()
    except Exception as e:
        print(f"\n[AnadoluKod Çöktü/Kapandı] -> {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        calistir(sys.argv[1])
    else:
        print("Kullanım: python anadolukod.py program.ak")
