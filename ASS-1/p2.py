import sys
from collections import deque

class AhoCorasick:
    def __init__(self):
        self.trie = [{}]
        self.fail = [0]
        self.is_word = [False]

    def insert(self, word):
        curr = 0
        for char in word:
            if char not in self.trie[curr]:
                self.trie[curr][char] = len(self.trie)
                self.trie.append({})
                self.fail.append(0)
                self.is_word.append(False)
            curr = self.trie[curr][char]
        self.is_word[curr] = True

    def build(self):
        queue = deque()
        for char, child in self.trie[0].items():
            self.fail[child] = 0
            queue.append(child)
            
        while queue:
            curr = queue.popleft()
            for char, child in self.trie[curr].items():
                fail_state = self.fail[curr]
                while fail_state > 0 and char not in self.trie[fail_state]:
                    fail_state = self.fail[fail_state]
                if char in self.trie[fail_state]:
                    fail_state = self.trie[fail_state][char]
                self.fail[child] = fail_state
                self.is_word[child] |= self.is_word[fail_state]
                queue.append(child)

    def contains_banned(self, text):
        curr = 0
        for char in text:
            while curr > 0 and char not in self.trie[curr]:
                curr = self.fail[curr]
            if char in self.trie[curr]:
                curr = self.trie[curr][char]
            if self.is_word[curr]:
                return True
        return False

def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return
        
    b = int(input_data[0].strip())
    ac = AhoCorasick()
    
    for i in range(1, b + 1):
        ac.insert(input_data[i].strip().lower())
    ac.build()
    
    n_idx = b + 1
    n = int(input_data[n_idx].strip())
    
    passwords_start = n_idx + 1
    
    special_symbols = set('$#@')
    
    for idx in range(1, n + 1):
        line_idx = passwords_start + idx - 1
        if line_idx >= len(input_data):
            break
        pwd = input_data[line_idx].strip()
        length = len(pwd)
        

        if not (6 <= length <= 12):
            print(f"{idx}: WEAK_LENGTH")
            continue
            
        if ac.contains_banned(pwd.lower()):
            print(f"{idx}: COMPROMISED")
            continue
            
        # Priority 3: Check Weak Pattern Constraint
        has_lower = False
        has_upper = False
        has_digit = False
        has_special = False
        consecutive_fail = False
        
        consecutive_count = 0
        prev_char = ''
        
        for char in pwd:
            if char.islower():
                has_lower = True
            elif char.isupper():
                has_upper = True
            elif char.isdigit():
                has_digit = True
            elif char in special_symbols:
                has_special = True
                
            if char == prev_char:
                consecutive_count += 1
            else:
                consecutive_count = 1
                prev_char = char
                
            if consecutive_count > 3:
                consecutive_fail = True
                
        if consecutive_fail or not (has_lower and has_upper and has_digit and has_special):
            print(f"{idx}: WEAK_PATTERN")
        else:
            print(f"{idx}: STRONG")

if __name__ == '__main__':
    solve()
