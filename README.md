# 🏦 Banking System (Python + JSON)

A **console-based Banking Management System** built using **Python**, with a **JSON file as a database**.
This project simulates real-world banking operations such as account creation, login, transactions, loan processing, EMI payments, and security features.

---

## 🚀 Features

### 👤 Account Management

* Create new bank account
* Secure login & logout
* View user details
* Close account (only if balance & loan are cleared)

### 🔐 Security

* Strong password validation

  * 8–12 characters
  * Uppercase, lowercase, digit, special character
* Transaction PIN (6-digit)

  * Generate PIN
  * Update PIN (cannot reuse old PIN)
* Password update (cannot reuse old password)

### 💰 Banking Operations

* Check balance
* Deposit money
* Withdraw money
* Transfer money to another account
* View complete transaction history

### 🏦 Loan Management

* Apply for loan
* Loan approval **after 24 hours** (auto-processing)
* Loan rejection **after 48 hours** if conditions fail
* 7% interest rate
* EMI calculation & payment
* Bank maintains **20% reserve rule**

### 📊 Bank Logic

* Tracks total bank money
* Updates bank balance on loan approval & EMI payment

---

## 🛠️ Technologies Used

* **Python 3**
* **JSON** (as database)
* `datetime` module
* `re` (Regular Expressions)

---

## 👨‍💻 Author

**Kinjal Kathrecha**
Python Developer | Backend Enthusiast

---

## ⭐ Note

This project is built for **learning purposes** and demonstrates real-world banking logic without external databases.

If you like this project, feel free to ⭐ star the repository!
