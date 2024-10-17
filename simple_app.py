# Database connection setup

from datetime import datetime
import random
import string
import sqlite3


def get_db_connection():
    conn = sqlite3.connect('bank_app.db')
    return conn


def create_tables():
        conn = get_db_connection()
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    password TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    type TEXT,
                    savings REAL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    tag TEXT PRIMARY KEY,
                    date TEXT,
                    action TEXT,
                    amount REAL,
                    account_id INTEGER,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            ''')
        conn.close()

# Base Account Class: Handles bank account operations
class Account:
    def __init__(self, id, user_id, type, savings):
        self.id = id
        self.user_id = user_id  # New field for user ID
        self.type = type
        self.savings = savings
        self.transactions = {}
        self.conn = get_db_connection()
        
    
    def generate_unique_tag(self, length=5):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    def deposit(self, sum_depo):
        if sum_depo <= 0:
            raise ValueError("Deposit amount must be greater than 0")
        self.savings += sum_depo
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        unique_tag = self.generate_unique_tag()
        self.save_transaction(unique_tag, date, 'deposit', sum_depo)
        return f"Deposited {sum_depo}. Current balance: {self.savings}"

    def withdrawn(self, drawn):
        if drawn <= 0:
            raise ValueError("Withdrawal amount must be greater than 0")
        if self.savings >= drawn:
            self.savings -= drawn
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            unique_tag = self.generate_unique_tag()
            self.save_transaction(unique_tag, date, 'withdraw', drawn)
            return f"Withdrew {drawn}. Current balance: {self.savings}"
        else:
            raise ValueError("Insufficient balance")

    def save_account(self):
        with self.conn:
            self.conn.execute('''
                INSERT OR REPLACE INTO accounts (id, user_id, type, savings)
                VALUES (?, ?, ?, ?)
            ''', (self.id, self.user_id, self.type, self.savings))

    def save_transaction(self, tag, date, action, amount):
        with self.conn:
            self.conn.execute('''
                INSERT INTO transactions (tag, date, action, amount, account_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (tag, date, action, amount, self.id))

    def load_account(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id=?', (self.id,))
        row = cursor.fetchone()
        if row:
            self.user_id, self.type, self.savings = row[1], row[2], row[3]
            self.load_transactions()

    def load_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE account_id=?', (self.id,))
        rows = cursor.fetchall()
        for row in rows:
            self.transactions[row[0]] = [row[1], row[2], row[3]]

    def show_transactions(self):
        return "\n".join([f"{tag}: {info}" for tag, info in self.transactions.items()])

# Subclass for specific types of accounts (e.g., Savings, Checking)
class SavingsAccount(Account):
    def __init__(self, id, user_id, savings):
        super().__init__(id, user_id, type='savings', savings=savings)

class CheckingAccount(Account):
    def __init__(self, id, user_id, savings):
        super().__init__(id, user_id, type='checking', savings=savings)

if __name__ == "__main__":

    create_tables()  # Create tables if they don't exist
    
    # Creating an instance of an account
    edoardo = SavingsAccount('ET1', 'user_01', 200)  # Assuming user_id is 'user_01'
    
    # Save the account to the database
    edoardo.save_account()
    
    # Example deposit and withdrawal
    print(edoardo.deposit(50))  # Deposit 50
    print(edoardo.withdrawn(30))  # Withdraw 30
    
    # Saving changes to the account after transactions
    edoardo.save_account()


    riccardo = SavingsAccount('RT01','user_02',120)
    riccardo.save_account()