import sys

sys.setrecursionlimit(2000000)

class Evaluator:
    def __init__(self, var_map):
        self.var_map = var_map
        self.memo = {}
        self.visited = set()

    def evaluate_expr(self, expr_str):
        tokens = self.tokenize(expr_str)
        if tokens is None:
            return "INVALID"
        
        pos = 0
        
        def parse_expression():
            nonlocal pos
            val = parse_term()
            if val is None:
                return None
            while pos < len(tokens) and tokens[pos] in ('+', '-'):
                op = tokens[pos]
                pos += 1
                next_val = parse_term()
                if next_val is None:
                    return None
                if op == '+':
                    val += next_val
                else:
                    val -= next_val
            return val

        def parse_term():
            nonlocal pos
            val = parse_factor()
            if val is None:
                return None
            while pos < len(tokens) and tokens[pos] == '*':
                pos += 1
                next_val = parse_factor()
                if next_val is None:
                    return None
                val *= next_val
            return val

        def parse_factor():
            nonlocal pos
            if pos >= len(tokens):
                return None
            
            token = tokens[pos]
            if token == '(':
                pos += 1
                val = parse_expression()
                if val is None:
                    return None
                if pos >= len(tokens) or tokens[pos] != ')':
                    return None
                pos += 1
                return val
            
            if token.isdigit():
                pos += 1
                return int(token)
            
            if token.isalpha():
                pos += 1
                var_val = self.evaluate_variable(token)
                if var_val == "CYCLE" or var_val == "INVALID" or var_val is None:
                    return None
                return var_val
                
            return None

        res = parse_expression()
        if res is None or pos != len(tokens):
            return "INVALID"
        return res

    def evaluate_variable(self, var_name):
        if var_name in self.memo:
            return self.memo[var_name]
        if var_name in self.visited:
            return "CYCLE"
        if var_name not in self.var_map:
            return "INVALID"
            
        self.visited.add(var_name)
        res = self.evaluate_expr(self.var_map[var_name])
        self.visited.remove(var_name)
        
        if res == "CYCLE" or res == "INVALID":
            return res
            
        self.memo[var_name] = res
        return res

    def tokenize(self, s):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            if s[i].isspace():
                i += 1
                continue
            if s[i] in ('+', '-', '*', '(', ')'):
                tokens.append(s[i])
                i += 1
            elif s[i].isdigit():
                start = i
                while i < n and s[i].isdigit():
                    i += 1
                tokens.append(s[start:i])
            elif s[i].isalpha():
                start = i
                while i < n and s[i].isalnum():
                    i += 1
                tokens.append(s[start:i])
            else:
                return None
        return tokens

def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return
        
    v = int(input_data[0].strip())
    var_map = {}
    
    for idx in range(1, v + 1):
        if idx >= len(input_data):
            break
        line = input_data[idx].strip()
        if '=' not in line:
            continue
        parts = line.split('=', 1)
        var_name = parts[0].strip()
        expression = parts[1].strip()
        var_map[var_name] = expression
        
    eval_expr_idx = v + 1
    if eval_expr_idx < len(input_data):
        target_expr = input_data[eval_expr_idx].strip()
    else:
        target_expr = ""
        
    evaluator = Evaluator(var_map)
    
    # Check for underlying cycles or invalid entries in the tracking variables first
    for var in list(var_map.keys()):
        status = evaluator.evaluate_variable(var)
        if status == "CYCLE":
            print("CYCLE")
            return
        elif status == "INVALID":
            print("INVALID")
            return
            
    final_res = evaluator.evaluate_expr(target_expr)
    if final_res is None:
        print("INVALID")
    else:
        print(final_res)

if __name__ == '__main__':
    solve()
