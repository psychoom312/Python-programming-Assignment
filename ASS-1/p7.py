import sys

class FormulaException(Exception):
    pass

class InvalidFormatError(FormulaException):
    pass

class UnknownVariableError(FormulaException):
    pass

class DivisionByZeroError(FormulaException):
    pass

class UnsupportedOperatorError(FormulaException):
    pass

class InteractiveCalculator:
    def __init__(self):
        self.variables = {}
        self.supported_operators = {'+', '-', '*', '/', '%'}

    def is_valid_identifier(self, s):
        return s.isidentifier()

    def parse_value(self, token):
        if token in self.variables:
            return self.variables[token]
        try:
            if '.' in token:
                return float(token)
            return int(token)
        except ValueError:
            raise UnknownVariableError(f"Unknown variable or invalid number: '{token}'")

    def evaluate_formula(self, line):
        tokens = line.split()
        if len(tokens) != 3:
            raise InvalidFormatError("Formula must be exactly in the format 'operand operator operand'")
        
        op1_str, op, op2_str = tokens
        
        if op not in self.supported_operators:
            # Check if it looks like an operator token to distinguish errors
            if any(c in '+-*/%' for c in op) or len(op) > 0:
                raise UnsupportedOperatorError(f"Operator '{op}' is not supported")
            raise InvalidFormatError("Formula format error")

        val1 = self.parse_value(op1_str)
        val2 = self.parse_value(op2_str)

        if op in ('/', '%') and val2 == 0:
            raise DivisionByZeroError("Division or modulo by zero scenario detected")

        if op == '+': return val1 + val2
        elif op == '-': return val1 - val2
        elif op == '*': return val1 * val2
        elif op == '/': return val1 / val2
        elif op == '%': return val1 % val2
        
        return None

    def process_line(self, line):
        line = line.strip()
        if not line:
            return None
        if line.lower() == 'quit':
            return 'QUIT'

        if '=' in line:
            parts = line.split('=', 1)
            var_name = parts[0].strip()
            expr = parts[1].strip()
            
            if not self.is_valid_identifier(var_name):
                raise InvalidFormatError(f"Invalid variable name definition: '{var_name}'")
            
            # Assignment could be a single value or an expression
            tokens = expr.split()
            if len(tokens) == 1:
                val = self.parse_value(tokens[0])
            else:
                val = self.evaluate_formula(expr)
                
            self.variables[var_name] = val
            return None
        else:
            return self.evaluate_formula(line)

def solve():
    # Read all lines from standard input efficiently to support batch processing
    input_lines = sys.stdin.read().splitlines()
    calc = InteractiveCalculator()
    
    for line in input_lines:
        if not line.strip():
            continue
        try:
            res = calc.process_line(line)
            if res == 'QUIT':
                break
            if res is not None:
                if isinstance(res, float) and res.is_integer():
                    print(int(res))
                else:
                    print(res)
        except FormulaException as e:
            print(e.__class__.__name__)
        except Exception:
            print("FormulaException")

if __name__ == '__main__':
    solve()
