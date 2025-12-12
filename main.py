import json
import re
from datetime import datetime
db_file="bank.json"


def load_db():
    with open(db_file,"r") as f:
        return json.load(f)
    
def save_db(data):
    with open(db_file,"w") as f:
        json.dump(data,f,indent=4) 

def valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) 

def valid_aadhar(aadhar):
    return aadhar.isdigit() and len(aadhar) == 12

def valid_pan(pan):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return re.match(pattern, pan.upper()) 

def generate_acc_no(db):
    db = load_db()
    if db["accounts"]:
        acc_number = str(max([int(a) for a in db["accounts"]]) + 1)
    else:
        acc_number = "1001"
    return acc_number

def add_transaction(user, msg):
    time = datetime.now().strftime('%Y-%m-%D %H:%M:%S')
    user['transactions'].append(f"{time} ---> {msg}")


def valid_password(password):
    if len(password) <= 8:
        return False
    
    has_upper = has_lower = has_digit = has_special = False
    
    for ch in password:
        if ch.isupper():
            has_upper = True
        elif ch.islower():
            has_lower = True
        elif ch.isdigit():
            has_digit = True
        else:
            has_special = True

    return has_upper and has_lower and has_digit and has_special

def create_account():
    db = load_db()
    acc_number = generate_acc_no(db)
    print("\n--- CREATE NEW ACCOUNT ---")
    print(f"Your account number will be: {acc_number}")
    
    name = input("Enter your name: ")
    
    while True:
        password = input("Set password: ")
        confirm_password = input("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match! Try again.")
            continue
        if not valid_password(password):
            print("Password must include:")
            print(" - 8 characters")
            print(" - Uppercase letter")
            print(" - Lowercase letter")
            print(" - Number")
            print(" - Special character\n")
            continue
        break
    
    while True:
        email = input("Enter your email: ")
        if valid_email(email):
            break
        print("Invalid email format! Please try again.")

    while True:
        aadhar = input("Enter Aadhaar number: ")
        if valid_aadhar(aadhar):
            break
        print("Aadhaar must be 12-digit numeric!")

    while True:
        pan = input("Enter PAN number: ")
        if valid_pan(pan):
            break
        print("Invalid PAN format! (Format: ABCDE1234F)")

    
    while True:
        try:
            balance = float(input("Enter opening balance: "))
            if balance < 0:
                print("Balance cannot be negative.")
                continue
            break
        except:
            print("Invalid amount! Please enter a number.")

    db["accounts"][acc_number] = {
        "name": name,
        "email_id": email,
        "password": password,
        "aadhaar_no": aadhar,
        "pan_no": pan,
        "balance": balance,
        "loan": {"amount": 0, "months": 0, "emi": 0, "remaining": 0},
        "transactions": []
    }
    get_total_bank_money(db)
    # db["bank_total"] += balance
    save_db(db)
    
    print(f"Account created successfully! Your account number is {acc_number}\n")
    return acc_number, password

def login():
    db=load_db()
    print("\n--- LOGIN ---")
    acc_number = input("Enter account number: ")
    password = input("Enter password: ")

    if acc_number in db["accounts"] and db["accounts"][acc_number]["password"] == password:
        user = db["accounts"][acc_number]
        print(f"\nLogin successful! Welcome {user['name']}")
        return acc_number, user
    else:
        print("Invalid account or password.")
        return None, None
    


def update_balance(acc_no,user):
    db=load_db()
    db["accounts"][acc_no]=user
    save_db(db)


def get_total_bank_money(db):
    total=0
    for acc in db["accounts"].values():
        total=total+acc["balance"]
    db["bank_total"] = total
    save_db(db)
    return total



def close_account(db,acc_no):
    db=load_db()
    confirm = input("Are you sure you want to close your account? (yes/no): ")

    if confirm.lower() != "yes":
        print("Account closure cancelled.")
        return False

    if acc_no in db["accounts"]:
        del db["accounts"][acc_no]
        save_db(db)
        print("Your account has been closed permanently.\n")
        return True
    else:
        print("Account not found!")
        return False


def transfer_amount(acc_no, user):
    db = load_db()
    print("\n----Transfer Money----")
    receiver_acc = input("Enter receiver account number: ")

    if receiver_acc not in db["accounts"]:
        print("Receiver account does not exist!")
        return

    if receiver_acc == acc_no:
        print("You cannot transfer to your own account.")
        return

    entered_pass = input("Enter your password to confirm: ")

    # Verify password
    if entered_pass != user["password"]:
        print("Incorrect password! Transfer cancelled.")
        return
    
    # Ask for transfer amount
    try:
        amt = float(input("Enter amount to transfer: "))
        if amt <= 0:
            print("Amount must be positive.")
            return

        if amt > user['balance']:
            print("Insufficient balance!")
            return
    except:
        print("Invalid amount!")
        return

    # Update balances
    user['balance'] -= amt
    db["accounts"][receiver_acc]["balance"] += amt

    update_balance(acc_no, user)
    save_db(db)

    add_transaction(user,
        f"Transferred ₹{amt} to {receiver_acc}"
    )
    add_transaction(db["accounts"][receiver_acc],
        f"Received ₹{amt} from {acc_no}"
    )
    save_db(db)

    print("Transfer successful!")


#take a loan
def take_loan(acc_no, user):
    db = load_db()

    print("\n--- TAKE LOAN ---")
    amount = float(input("Enter loan amount: "))
    months = int(input("Enter time period (months): "))

    bank_total = db.get("bank_total", 0)

    loan_limit = bank_total * 0.80

    # Check bank balance rule
    if amount > loan_limit:
        print("\nLoan Rejected!")
        print(f"Max loan allowed: ₹{loan_limit}")
        return

    # If bank has enough money → Approve loan
    interest = amount * 0.07
    total_payable = amount + interest
    emi = total_payable / months

    # Update user balance
    user["balance"] += amount

    # Store loan details in user account
    user["loan"] = {
        "amount": amount,
        "months": months,
        "emi": emi,
        "remaining": total_payable
    }

    # Bank money decreases (bank gives money)
    db["bank_total"] -= amount

    # Save updates
    db["accounts"][acc_no] = user  # Update user in db
    save_db(db)

    # Add transactions
    add_transaction(user, f"Loan taken: ₹{amount}")
    add_transaction(user, f"Loan interest added: ₹{interest}")
    add_transaction(user, f"EMI per month: ₹{emi}")

    print(f"\n✅ Loan Approved Successfully!")
    print(f"Loan Amount: ₹{amount}")
    print(f"Interest (7%): ₹{interest}")
    print(f"Total Payable: ₹{total_payable}")
    print(f"Monthly EMI: ₹{emi}")


#pay emi
def pay_emi(acc_no, user):
    db = load_db()
    loan = user["loan"]

    # ------------------------------
    # 1. CHECK IF USER HAS ACTIVE LOAN
    # ------------------------------
    if loan["amount"] == 0 and loan["remaining"] == 0:
        print("No active loan.")
        return

    loan["remaining"] = round(loan["remaining"], 2)
    print(f"\nRemaining Loan Amount: ₹{loan['remaining']:.2f}")

    # ------------------------------
    # 2. INPUT PAYMENT AMOUNT
    # ------------------------------
    try:
        amount = float(input("Enter the amount you want to pay: ₹"))
        amount = round(amount, 2)
    except:
        print("Invalid amount!")
        return

    if amount <= 0:
        print("Amount must be positive.")
        return
    if amount > user["balance"]:
        print("Insufficient balance!")
        return
    if amount > loan["remaining"]:
        print(f"You can only pay up to remaining loan: ₹{loan['remaining']:.2f}")
        return

    # ------------------------------
    # 3. DEDUCT FROM USER BALANCE
    # ------------------------------
    user["balance"] -= amount
    user["balance"] = round(user["balance"], 2)

    # ------------------------------
    # 4. REDUCE LOAN REMAINING
    # ------------------------------
    loan["remaining"] -= amount
    loan["remaining"] = round(loan["remaining"], 2)

    # ------------------------------
    # 5. REDUCE LOAN MONTHS (if paying full EMI or more)
    # ------------------------------
    if loan["emi"] > 0:
        months_paid = int(amount // loan["emi"])
        if months_paid > 0:
            loan["months"] -= months_paid
            if loan["months"] < 0:
                loan["months"] = 0

    # ------------------------------
    # 6. BANK GETS THE EMI AMOUNT
    # ------------------------------
    db["bank_total"] += amount

    # ------------------------------
    # 7. ADD TRANSACTION
    # ------------------------------
    add_transaction(user, f"Paid EMI: ₹{amount}")

    # ------------------------------
    # 8. CHECK IF LOAN FULLY PAID
    # ------------------------------
    if loan["remaining"] <= 0.01:
        print("\n🎉 Loan fully repaid!")

        user["loan"] = {
            "amount": 0,
            "months": 0,
            "emi": 0,
            "remaining": 0
        }
    else:
        print(
            f"Paid ₹{amount}. Remaining Loan: ₹{loan['remaining']:.2f}. "
            f"Months left: {loan['months']}"
        )

    # ------------------------------
    # 9. SAVE DATA
    # ------------------------------
    db["accounts"][acc_no] = user
    save_db(db)



# ---------------- ACCOUNT MENU ----------------
def account_menu(acc_no,user):
    db=load_db()    
    while True:
        print("\n--- ACCOUNT MENU ---")
        print("1. Check Balance")
        print("2. Add Money (Deposit)")
        print("3. Withdraw Money")
        print("4. Logout")
        print("5. Close Account")
        print("6. Transfer Amount")
        print("7. View All Transactions")
        print("8. Apply for loan")
        print("9. pay EMI")


        choice = input("Enter your choice: ")

        if choice == "1":
            print(f"Current balance: {user['balance']}")

        elif choice == "2":
            try:
                amt = float(input("Enter amount to deposit: "))
                if amt <= 0:
                    print("Amount must be positive.")
                    continue
                user['balance'] += amt
                update_balance(acc_no,user)
                add_transaction(user, f"Deposited ₹{amt}")
                print(f"Deposited {amt}. New balance: {user['balance']}")
            except:
                print("Invalid input.")

        elif choice == "3":
            try:
                amt = float(input("Enter amount to withdraw: "))
                if amt <= 0:
                    print("Amount must be positive.")
                    continue
                if amt > user['balance']:
                    print("Insufficient balance!")
                    continue
                user["balance"] -= amt
                bank_total = db.get("bank_total", 0)
                db["bank_total"] -= amt
                update_balance(acc_no,user)
                add_transaction(user, f"Withdrew ₹{amt}")
                print(f"Withdrawn {amt}. New balance: {user['balance']}")
            except:
                print("Invalid input.")

        elif choice == "4":
            print("Logged out successfully!\n")
            break
            
        elif choice == "5":
            db=load_db()
            if acc_no not in db["accounts"]:
                print("Account already closed!")
                break
            closed=close_account(db,acc_no)
            if closed:
                print("account closed successfully.")
                break

        elif choice == "6":
            transfer_amount(acc_no,user)

        elif choice == "7":
            print("\n--- ALL TRANSACTIONS ---")
            if user["transactions"]:
                for t in user["transactions"]:
                    print(t)
            else:
                print("No transactions yet.")

        elif choice == "8":
            take_loan(acc_no,user)

        elif choice == "9":
            pay_emi(acc_no,user)

        else:
            print("Invalid choice, try again!")
        

# ---------------- MAIN SYSTEM ----------------
while True:
    print("--WELCOME TO BANKING SYSTEM--")
    print("1. Login")
    print("2. register")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        acc_no,user = login()
        if user:
            account_menu(acc_no,user)            

    elif choice == "2":
        create_account()

    elif choice == "3":
        print("---Thank you for using the banking system.---")
        break

    else:
        print("Invalid choice, try again!")
