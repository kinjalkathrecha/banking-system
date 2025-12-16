import json
import re
from datetime import datetime,timedelta
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
    if not 8 <= len(password) <= 12:
        return False

    has_upper = has_lower = has_digit = has_special = False
    special_chars = "@#$%^&*"

    for ch in password:
        if ch.isupper():
            has_upper = True
        elif ch.islower():
            has_lower = True
        elif ch.isdigit():
            has_digit = True
        elif ch in special_chars:
            has_special = True
        else:
            pass

    return has_upper and has_lower and has_digit and has_special

def update_password(acc_no, user):
    db = load_db()

    print("\n--- UPDATE PASSWORD ---")
    current_password = input("Enter current password: ")
    if current_password != user["password"]:
        print("Incorrect password!")
        return

    while True:
        new_password = input("Enter new password: ")
        if new_password == user["password"]:
            print("New password cannot be the same as the old password!")
            continue
        if not valid_password(new_password):
            print("Password must include:\n - 8–12 characters\n - Uppercase letter\n - Lowercase letter\n - Number\n - Special character")
            continue

        confirm_password = input("Confirm new password: ")

        if new_password != confirm_password:
            print("Passwords do not match! Try again.")
            continue

        break

    user["password"] = new_password
    db["accounts"][acc_no] = user
    save_db(db)
    print("Password updated successfully!")


def user_details(acc_no, user):
    db = load_db()
    print("\n--- USER DETAILS ---")
    print(f"Name       : {user['name']}")
    print(f"Email      : {user['email_id']}")
    print(f"Aadhaar    : {user['aadhaar_no']}")
    print(f"PAN        : {user['pan_no']}")
   


def create_account():
    db = load_db()
    acc_number = generate_acc_no(db)
    print("\n--- CREATE NEW ACCOUNT ---")
    
    name = input("Enter your name: ")
    
    while True:
    
        password = input("Set password: ")
        if not valid_password(password):
            print("Password must include:")
            print(" - 8–12 characters")
            print(" - Uppercase letter")
            print(" - Lowercase letter")
            print(" - Number")
            print(" - Special character\n")
            continue

        confirm_password = input("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match!\n")
            continue

    
        while True:
            email = input("Enter your email: ")
            if valid_email(email):
                break
            print("Invalid email format! Please try again.\n")

   
        while True:
            aadhar = input("Enter Aadhaar number: ")
            if valid_aadhar(aadhar):
                break
            print("Aadhaar must be 12-digit numeric!\n")

   
        while True:
            pan = input("Enter PAN number: ")
            if valid_pan(pan):
                break
            print("Invalid PAN format! (ABCDE1234F)\n")

   
        try:
            balance = float(input("Enter opening balance: "))
            if balance < 0:
                print("Balance cannot be negative.\n")
                continue
        except:
            print("Invalid amount!\n")
            continue

        break   


    db["accounts"][acc_number] = {
        "name": name,
        "email_id": email,
        "password": password,
        "aadhaar_no": aadhar,
        "pan_no": pan,
        "balance": balance,
        "status": "ACTIVE",
        "t_pin": None, 
        "loan": {"amount": 0, "months": 0, "emi": 0, "remaining": 0, "status":None},
        "transactions": []
    }
    get_total_bank_money(db)
    save_db(db)
    
    print(f"Account created successfully! Your account number is {acc_number}\n")
    return acc_number, password

def login():
    db = load_db()
    print("\n--- LOGIN ---")

    acc_number = input("Enter account number: ")
    password = input("Enter password: ")

    if acc_number not in db["accounts"]:
        print("Invalid account number.")
        return None, None

    user = db["accounts"][acc_number]

    if user["status"] == "CLOSED":
        print("This account is CLOSED. Please contact bank support.")
        return None, None

    if user["password"] != password:
        print("Invalid password.")
        return None, None

    print(f"\nLogin successful! Welcome {user['name']}")
    return acc_number, user

    


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



def close_account(acc_no):
    db = load_db()
    user = db["accounts"].get(acc_no)

    if not user:
        print("Account not found.")
        return False

    if user["status"] == "CLOSED":
        print("Account already closed.")
        return False

    if user["balance"] != 0:
        print("Account balance must be zero.")
        return False

    if user["loan"]["remaining"] > 0:
        print("Please clear loan before closing account.")
        return False

    confirm = input("Are you sure you want to close your account? (yes/no): ")
    if confirm.lower() != "yes":
        print("Account closure cancelled.")
        return False

    user["status"] = "CLOSED"
    add_transaction(user, "Account closed by user")

    db["accounts"][acc_no] = user
    save_db(db)

    print("Account closed successfully.")
    return True

def generate_t_pin(acc_no, user):
    db = load_db()

    if user["t_pin"] is not None:
        print("Transaction PIN already exists.")
        return

    while True:
        pin = input("Set 6-digit Transaction PIN: ")
        if pin.isdigit() and len(pin) == 6:
            break
        print("PIN must be exactly 6 digits.")

    user["t_pin"] = pin
    db["accounts"][acc_no] = user
    save_db(db)

    print("Transaction PIN generated successfully.")

def update_t_pin(acc_no, user):
    db = load_db()

    print("\n--- UPDATE TRANSACTION PIN ---")
    if user["t_pin"] is None:
        print("You do not have a transaction PIN. Generating new one...")
        current_pin = None
    else:
        current_pin = input("Enter current Transaction PIN: ")
        if current_pin != user["t_pin"]:
            print("Incorrect current PIN!")
            return

    while True:
        new_pin = input("Enter new 6-digit Transaction PIN: ")
        if new_pin.isdigit() and len(new_pin) == 6:
            if current_pin and new_pin == current_pin:
                print("New PIN cannot be same as old PIN! Try again.")
                continue
            confirm_pin = input("Confirm new PIN: ")
            if new_pin == confirm_pin:
                break
            else:
                print("PINs do not match! Try again.")
        else:
            print("PIN must be exactly 6 digits.")

    user["t_pin"] = new_pin
    db["accounts"][acc_no] = user
    save_db(db)
    print("Transaction PIN updated successfully!")


def transfer_amount(acc_no, user):
    db = load_db()
    print("\n----Transfer Money----")
    receiver_acc = input("Enter receiver account number: ")

    if receiver_acc not in db["accounts"]:
        print("Receiver account does not exist!")
        return
    if db["accounts"][receiver_acc]["status"] == "CLOSED":
        print("Receiver account is closed. Transfer not allowed.")
        return
    if user["status"] != "ACTIVE":
        print("Your account is not active.")
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

    #verify transaction PIN
    if user["t_pin"] is None:
        print("Transaction PIN not generated.")
        return
    
        

    entered_pin = input("Enter Transaction PIN: ")

    if entered_pin != user["t_pin"]:
        print("Invalid Transaction PIN! Transfer failed ")
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

    # Check if already has active or pending loan
    if user["loan"].get("status") in ["PENDING", "APPROVED"]:
        print("You already have an active or pending loan.")
        return

    # Save as PENDING (no approval now)
    user["loan"] = {
        "amount": amount,
        "months": months,
        "emi": 0,
        "remaining": 0,
        "status": "PENDING",
        "applied_at": datetime.now().isoformat()
    }

    db["accounts"][acc_no] = user
    save_db(db)

    print("\n Loan request submitted successfully!")
    print(" Loan is under review.")
    print(" Please check status after 24 hours.")



def auto_process_loan(acc_no, user):
    db = load_db()
    loan = user["loan"]

    if loan.get("status") != "PENDING":
        return

    applied_time = datetime.fromisoformat(loan["applied_at"])
    now = datetime.now()

    bank_total = db.get("bank_total", 0)
    loan_limit = bank_total * 0.80
    amount = loan["amount"]
    months = loan["months"]

    if now - applied_time >= timedelta(hours=24) and amount <= loan_limit:
        interest = amount * 0.07
        total_payable = amount + interest
        emi = total_payable / months

        user["balance"] += amount
        db["bank_total"] -= amount

        user["loan"] = {
            "amount": amount,
            "months": months,
            "emi": round(emi, 2),
            "remaining": round(total_payable, 2),
            "status": "APPROVED",
            "approved_at": now.isoformat()
        }

        add_transaction(user, f"Loan approved: ₹{amount}")
        add_transaction(user, f"EMI per month: ₹{emi}")

    elif now - applied_time >= timedelta(hours=48):
        user["loan"]["status"] = "REJECTED"
        user["loan"]["rejected_at"] = now.isoformat()
        add_transaction(user, "Loan rejected after review")

    db["accounts"][acc_no] = user
    save_db(db)


#pay emi
def pay_emi(acc_no, user):
    db = load_db()
    loan = user["loan"]

    # NO ACTIVE LOAN CHECK
    if loan.get("amount", 0) == 0 or loan.get("remaining", 0) == 0:
        print("No active loan.")
        return

    # PENDING / REJECTED CHECK
    if loan.get("status") == "PENDING":
        print("Loan is still under review. EMI not allowed.")
        return

    if loan.get("status") == "REJECTED":
        print("Loan was rejected. EMI not applicable.")
        return

    loan["remaining"] = round(loan["remaining"], 2)
    print(f"\nRemaining Loan Amount: ₹{loan['remaining']:.2f}")
    print(f"Monthly EMI: ₹{loan['emi']:.2f}")

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
        print(f"You can only pay up to ₹{loan['remaining']:.2f}")
        return

    # DEDUCT USER BALANCE
    user["balance"] = round(user["balance"] - amount, 2)

    # REDUCE LOAN
    loan["remaining"] = round(loan["remaining"] - amount, 2)

    # BANK MONEY INCREASES
    db["bank_total"] = round(db.get("bank_total", 0) + amount, 2)

    # MONTH REDUCTION LOGIC
    if amount >= loan["emi"]:
        loan["months"] -= 1
        if loan["months"] < 0:
            loan["months"] = 0

    # TRANSACTION
    add_transaction(user, f"Paid EMI: ₹{amount}")

    # LOAN FULLY PAID
    if loan["remaining"] <= 0:
        user["loan"] = {
            "amount": 0,
            "months": 0,
            "emi": 0,
            "remaining": 0,
            "status": "CLOSED"
        }
        print("\n Loan fully repaid!")
    else:
        print(
            f"Paid ₹{amount}. Remaining Loan: ₹{loan['remaining']:.2f}. "
            f"Months left: {loan['months']}"
        )

    # SAVE DATA
    db["accounts"][acc_no] = user
    save_db(db)




# ---------------- ACCOUNT MENU ----------------
def account_menu(acc_no,user):
    
    while True:
        auto_process_loan(acc_no,user)
        if user["status"] == "CLOSED":
            print("This account is CLOSED. No operations allowed.")
            break
        db=load_db()    
   
        print("\n--- ACCOUNT MENU ---")
        print("1. Check Balance")
        print("2. Add Money (Deposit)")
        print("3. Withdraw Money")
        print("4. Logout")
        print("5. Close Account")
        print("6. generate transaction PIN")
        print("7. Transfer Amount")
        print("8. View All Transactions")
        print("9. Apply for loan")
        print("10. pay EMI")
        print("11. update transaction PIN")
        print("12. Update Password")
        print("13. View user Details")

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
            closed = close_account(acc_no)
            if closed:
                user["status"] = "CLOSED"
                print("Account closed. Logging out...")
                break
        
        elif choice == "6":
            generate_t_pin(acc_no,user)
        
        elif choice == "7":
            transfer_amount(acc_no,user)

        elif choice == "8":
            print("\n--- ALL TRANSACTIONS ---")
            if user["transactions"]:
                for t in user["transactions"]:
                    print(t)
            else:
                print("No transactions yet.")

        elif choice == "9":
            take_loan(acc_no,user)

        elif choice == "10":
            pay_emi(acc_no,user)

        elif choice == "11":
            update_t_pin(acc_no, user)

        elif choice == "12":
            update_password(acc_no, user)

        elif choice == "13":
            user_details(acc_no, user)

        else:
            print("Invalid choice, try again!")
        

# ---------------- MAIN SYSTEM ----------------
while True:
    print("\n--WELCOME TO BANKING SYSTEM--")
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


