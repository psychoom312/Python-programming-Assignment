import sys
import csv
from datetime import datetime

def validate_row(row):
    required_fields = ['tid', 'acc', 'type', 'amount', 'time']
    for field in required_fields:
        if field not in row or not row[field].strip():
            raise ValueError(f"Missing required field: {field}")
            
    tid = row['tid'].strip()
    acc = row['acc'].strip()
    t_type = row['type'].strip().upper()
    amount_str = row['amount'].strip()
    timestamp_str = row['time'].strip()
    
    if t_type not in ('CREDIT', 'DEBIT'):
        raise ValueError(f"Invalid transaction type: '{t_type}'. Must be CREDIT or DEBIT")
        
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError(f"Amount must be strictly greater than 0, got {amount}")
    except ValueError:
        raise ValueError(f"Invalid numeric amount format: '{amount_str}'")
        
    try:
        datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError(f"Invalid timestamp format: '{timestamp_str}'. Expected yyyy-mm-ddThh:mm:ss")
        
    return tid, acc, t_type, amount, timestamp_str

def solve():
    if len(sys.argv) < 2:
        input_path = input("Enter path of input CSV file: ").strip()
    else:
        input_path = sys.argv[1]
        
    balances = {}
    
    try:
        with open(input_path, mode='r', newline='', encoding='utf-8') as infile, \
             open('credit.csv', mode='w', newline='', encoding='utf-8') as cred_file, \
             open('debit.csv', mode='w', newline='', encoding='utf-8') as deb_file, \
             open('error.csv', mode='w', newline='', encoding='utf-8') as err_file:
             
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames if reader.fieldnames else ['tid', 'acc', 'type', 'amount', 'time']
            
            cred_writer = csv.DictWriter(cred_file, fieldnames=fieldnames)
            deb_writer = csv.DictWriter(deb_file, fieldnames=fieldnames)
            
            err_fieldnames = fieldnames + ['reason']
            err_writer = csv.DictWriter(err_file, fieldnames=err_fieldnames)
            
            cred_writer.writeheader()
            deb_writer.writeheader()
            err_writer.writeheader()
            
            for row in reader:
                try:
                    tid, acc, t_type, amount, time_str = validate_row(row)
                    
                    if t_type == 'CREDIT':
                        cred_writer.writerow(row)
                        balances[acc] = balances.get(acc, 0.0) + amount
                    else:
                        deb_writer.writerow(row)
                        balances[acc] = balances.get(acc, 0.0) - amount
                        
                except Exception as e:
                    error_row = dict(row)
                    error_row['reason'] = str(e)
                    err_writer.writerow(error_row)
                    
    except FileNotFoundError:
        print("INVALID")
        return

    sorted_accounts = sorted(
        balances.items(),
        key=lambda x: (-abs(x[1]), x[0])
    )
    
    for acc, bal in sorted_accounts:
        if bal.is_integer():
            print(f"{acc} {int(bal)}")
        else:
            print(f"{acc} {bal:.2f}")

if __name__ == '__main__':
    solve()
