acc_file="acc.txt"

def valid_password(password):
    if len(password) < 8:
        return False
    
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    
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
    print("\n--- CREATE NEW ACCOUNT ---")
    name = input("Enter your name: ")
    acc_number = input("Set account number: ")

    while True:
        password = input("Set password: ")
        if valid_password(password):
            break
        else:
            print("Password must include:")
            print(" - 8 characters")
            print(" - Uppercase letter")
            print(" - Lowercase letter")
            print(" - Number")
            print(" - Special character\n")

    balance = input("Enter opening balance: ")

    with open(acc_file, "a") as f:
        f.write(f"{acc_number},{name},{password},{balance}\n")

    print("Account created successfully!\n")
    return acc_number, password


def login():
    print("\n--- LOGIN ---")
    acc_number = input("Enter account number: ")
    password = input("Enter password: ")

    
    with open(acc_file, "r") as f:
        for line in f:
            saved_acc, saved_name, saved_pass, saved_balance = line.strip().split(",")

            if acc_number == saved_acc and password == saved_pass:
                print(f"\nLogin successful! Welcome {saved_name}")
                return {
                        "acc_no": saved_acc,
                        "name": saved_name,
                        "balance": float(saved_balance),
                        "password": saved_pass
                    }
    

    print("Login failed! Account not found or wrong password.\n")
    return False

def update_balance(user):
    lines = []
    with open(acc_file, "r") as f:
        for line in f:
            saved_acc, saved_name, saved_pass, saved_balance = line.strip().split(",")
            if saved_acc == user['acc_no']:
                saved_balance = str(user['balance'])  # update balance
            lines.append(f"{saved_acc},{saved_name},{saved_pass},{saved_balance}\n")
    with open(acc_file, "w") as f:
        f.writelines(lines)

def close_account(user):
    confirm = input("Are you sure you want to close your account? (yes/no): ")

    if confirm.lower() != "yes":
        print("Account closure cancelled.")
        return

    lines = []
    with open(acc_file, "r") as f:
        for line in f:
            saved_acc, saved_name, saved_pass, saved_balance = line.strip().split(",")
            # keep all accounts except current one
            if saved_acc != user['acc_no']:
                lines.append(line)

    # rewrite file without this account
    with open(acc_file, "w") as f:
        f.writelines(lines)

    print("Your account has been closed permanently.\n")

def transfer_account(acc_no):
    try:
        with open(acc_file,"r") as f:
            for line in f:
                saved_acc,saved_name,saved_pass,saved_balance = line.strip().split(',')
                if saved_acc == acc_no:
                    return{
                        "acc_no":saved_acc,
                        "name":saved_name,
                        "password":saved_pass,
                        "balance":float(saved_balance)
                    }
        return None
    except FileNotFoundError:
        return None        



def transfer_amount(user):
    print("\n----Transfer Money----")
    receiver_acc=input("Enter receiver account number:")

    if receiver_acc == user['acc_no']:
        print("you can't transfer money to your own account")
        return
    
    receiver=transfer_account(receiver_acc)

    if receiver is None:
        print("receiver account does not exist.")
        return

    try:
        amt=float(input("enter amount to transfer:"))
        if amt<=0:
            print("amount must be positive.")
            return
        
        if amt>user['balance']:
            print("Insufficient balance!")
            return
    
    except:
        print("invalid amount!")
        return

    #update
    user['balance']-=amt

    #update receiver balance
    receiver['balance']+=amt

    #update in file
    lines=[]
    with open(acc_file,"r") as f:
        for line in f:
            saved_acc,saved_name,saved_pass,saved_balance = line.strip().split(',')

            if saved_acc == user['acc_no']:
                lines.append(f"{user['acc_no']},{user['name']},{user['password']},{user['balance']}\n")

            elif saved_acc == receiver['acc_no']:
                lines.append(f"{receiver['acc_no']},{receiver['name']},{receiver['password']},{receiver['balance']}\n")

            else:
                lines.append(line)

    with open(acc_file,"w") as f:
        f.writelines(lines)

    print(f"successfully transferred {amt} to {receiver['name']} {receiver['acc_no']}")



def account_menu(user):
    while True:
        print("\n--- ACCOUNT MENU ---")
        print("1. Check Balance")
        print("2. Add Money (Deposit)")
        print("3. Withdraw Money")
        print("4. Logout")
        print("5. close account")
        print("6. Transfer amount")

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
                update_balance(user)
                print(f"Deposited {amt}. New balance: {user['balance']}")
            except:
                print("Invalid input. Enter a number.")
        elif choice == "3":
            try:
                amt = float(input("Enter amount to withdraw: "))
                if amt <= 0:
                    print("Amount must be positive.")
                    continue
                if amt > user['balance']:
                    print("Insufficient balance!")
                    continue
                user['balance'] -= amt
                update_balance(user)
                print(f"Withdrawn {amt}. New balance: {user['balance']}")
            except:
                print("Invalid input. Enter a number.")
        elif choice == "4":
            print("Logged out successfully!\n")
            break
            
        elif choice == "5":
            close_account(user)
            break

        elif choice == "6":
            transfer_amount(user)

        else:
            print("Invalid choice, try again!")
    
while True:
    print("--welcome to banking system--")
    print("1.login")
    print("2.exit")

    choice=input("enter your choice:")
    if choice=="1":
        user=login()
        if user:
            account_menu(user)            
            break
        else:
            print("You don't have an account. Please create one.")
            create_account()
            

    elif choice=="2":
        print("---thank you for using a banking system.---")
        break

    else:
        print("Invalid choice, try again!")

