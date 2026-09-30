import sys

class InsufficientFundsException(Exception):
    pass

class AccountNotFoundException(Exception):
    pass

class InvalidAmountException(Exception):
    pass

class Account:
    def __init__(self, account_id: str, initial_balance: int):
        self._account_id = account_id
        self._balance = initial_balance

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def balance(self) -> int:
        return self._balance

    @balance.setter
    def balance(self, value: int):
        if value < 0:
            raise InsufficientFundsException(f"Account {self._account_id} would overdraft.")
        self._balance = value

class Bank:
    def __init__(self):
        self._accounts = {}
        self._batch_counter = 0
        self._in_batch = False
        self._batch_checkpoint = {}

    def add_account(self, account_id: str, initial_balance: int):
        self._accounts[account_id] = Account(account_id, initial_balance)

    def get_account(self, account_id: str) -> Account:
        if account_id not in self._accounts:
            raise AccountNotFoundException(f"Account {account_id} does not exist.")
        return self._accounts[account_id]

    def _save_to_checkpoint(self, account_id: str):
        if self._in_batch and account_id not in self._batch_checkpoint:
            self._batch_checkpoint[account_id] = self._accounts[account_id].balance

    def deposit(self, account_id: str, amount: int):
        if amount <= 0:
            raise InvalidAmountException("Deposit amount must be positive.")
        account = self.get_account(account_id)
        self._save_to_checkpoint(account_id)
        account.balance += amount

    def withdraw(self, account_id: str, amount: int):
        if amount <= 0:
            raise InvalidAmountException("Withdrawal amount must be positive.")
        account = self.get_account(account_id)
        self._save_to_checkpoint(account_id)
        account.balance -= amount

    def transfer(self, from_id: str, to_id: str, amount: int):
        if amount <= 0:
            raise InvalidAmountException("Transfer amount must be positive.")
        if from_id == to_id:
            return
        
        # Validate existence before making updates
        self.get_account(from_id)
        self.get_account(to_id)
        
        self.withdraw(from_id, amount)
        try:
            self.deposit(to_id, amount)
        except Exception:
            # If deposit unexpectedly fails, restore immediate withdrawal step state
            self.deposit(from_id, amount)
            raise

    def begin_batch(self):
        self._in_batch = True
        self._batch_counter += 1
        self._batch_checkpoint.clear()

    def commit_batch(self):
        self._in_batch = False
        self._batch_checkpoint.clear()

    def rollback_batch(self) -> int:
        for account_id, original_balance in self._batch_checkpoint.items():
            self._accounts[account_id].balance = original_balance
        self._in_batch = False
        self._batch_checkpoint.clear()
        return self._batch_counter

    def print_balances(self):
        for acc_id in sorted(self._accounts.keys()):
            print(f"{acc_id} {self._accounts[acc_id].balance}")

def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    # Parse initial accounts config
    num_accounts = int(input_data[0].strip())
    bank = Bank()
    
    line_idx = 1
    for _ in range(num_accounts):
        parts = input_data[line_idx].split()
        bank.add_account(parts[0], int(parts[1]))
        line_idx += 1

    num_ops = int(input_data[line_idx].strip())
    line_idx += 1
    
    # Process queries and operations sequential steps
    ops_processed = 0
    while ops_processed < num_ops and line_idx < len(input_data):
        line = input_data[line_idx].strip()
        line_idx += 1
        if not line:
            continue
            
        ops_processed += 1
        parts = line.split()
        op_type = parts[0]
        
        try:
            if op_type == "BATCH_BEGIN":
                bank.begin_batch()
                # Read batch instructions iteratively until a BATCH_END token is collected
                batch_failed = False
                while line_idx < len(input_data):
                    b_line = input_data[line_idx].strip()
                    line_idx += 1
                    if not b_line:
                        continue
                    
                    b_parts = b_line.split()
                    if b_parts[0] == "BATCH_END":
                        ops_processed += 1
                        break
                    
                    if not batch_failed:
                        try:
                            if b_parts[0] == "DEPOSIT":
                                bank.deposit(b_parts[1], int(b_parts[2]))
                            elif b_parts[0] == "WITHDRAW":
                                bank.withdraw(b_parts[1], int(b_parts[2]))
                            elif b_parts[0] == "TRANSFER":
                                bank.transfer(b_parts[1], b_parts[2], int(b_parts[3]))
                        except Exception:
                            batch_failed = True
                            
                if batch_failed:
                    failed_id = bank.rollback_batch()
                    print(f"FAILED {failed_id}")
                else:
                    bank.commit_batch()
                    
            elif op_type == "DEPOSIT":
                bank.deposit(parts[1], int(parts[2]))
            elif op_type == "WITHDRAW":
                bank.withdraw(parts[1], int(parts[2]))
            elif op_type == "TRANSFER":
                bank.transfer(parts[1], parts[2], int(parts[3]))
                
        except Exception:
            # Standalone operations outside a batch that fail are quietly ignored
            pass

    bank.print_balances()

if __name__ == '__main__':
    solve()
