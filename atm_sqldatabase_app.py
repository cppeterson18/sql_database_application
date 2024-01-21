"""
Christian Peterson
ATM Application
SQL DATABASE PROJECT
[June/July 2023]
"""

import pymysql


def connection(name):
    # Connects to the MySQL database
    username = input("Enter Username: ")
    psword = input("Enter Password: ")
    
    try:
        connection = pymysql.connect(
            host = "localhost",
            user = username,
            password = psword,
            database = name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
    
    connection.close()
    return username, psword, name



def create_acct(sql_username, sql_password, db_name):    
    # ESTABLISH CONNECTION TO DATABASE
    try:
        cn_obj = pymysql.connect(
            host = "localhost",
            user = sql_username,
            password = sql_password,
            database = db_name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
        
    # NOT REGISTERED - Person inputs Name (F, L) and Pin; added to dB
    print()
    print("=============================================")
    print("=============================================")
    print("===The following 3 fields are required for Beantown Bank===")
    f_name = input("\nCREATE: Enter your first name:\n")
    l_name = input("CREATE: Enter your last name:\n")
    pin = int(input("CREATE: Create your 4-digit PIN code:\n"))
    print("\nChoose an account type: [Checking], [Savings]")
    acct_type = input("Specify the type of account that you are opening (OMIT THE []):\n")
    balance = float(input("\nCREATE: How much money would you like to \
                          insert into this account?                 \
                          This is your starting balance:\n"))
    print("=============================================")
    print("=============================================")
    
    # Call the first account creation procedure to open fields in the customer
    # and account tables (establish a relationship between both entities)
    cursor = cn_obj.cursor()
    cursor.callproc("open_first_acct", (f_name, l_name, pin, acct_type, balance))
    
    cursor.close()
    # DISREGARD - these comments are only here b/c of the Final Report reference
    # [BROKEN] TRIGGER SHOULD BE CALLED HERE (trigger_after_customer_insert), 
    # DOESN'T WORK --> DO NOT CREATE THE TRIGGER IN THE MYSQL FILE
    
    # AFTER THIS NEW ACCOUNT IS INSERTED, IT'S CUSTOMER_ID IS RETURNED TO THE USER
    cursor2 = cn_obj.cursor()
    get_lastid = "select LAST_INSERT_ID()"
    cursor2.execute(get_lastid)
    
    for row in cursor2.fetchall():
        print("\n===IMPORTANT===\n")
        print("YOUR CUSTOMER ID IS: ", row["LAST_INSERT_ID()"])
    cursor2.close()
    
    
    print("\n===YOU MUST WRITE DOWN YOUR CUSTOMER ID FOR FUTURE REFERENCE===\n")
    print("===YOUR CUSTOMER ID IS NEEDED FOR EVERY OPERATION===")
    print("The following fields have been added.")
    success = 1
    
    cn_obj.commit()
    cn_obj.close()
    return success
    


def check_pin(sql_username, sql_password, db_name, cust_id, inputted_pin):
    # ESTABLISH CONNECTION TO DATABASE
    try:
        connection = pymysql.connect(
            host = "localhost",
            user = sql_username,
            password = sql_password,
            database = db_name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
        
    # Ensures that the correct PIN has been inputted
    # Returns a number corresponding to if the PIN is correct or not
    cursor = connection.cursor()
    query = "select pin_num from customer where customer_id=%s"
    cursor.execute(query, (cust_id))
    
    #status = 0
    for val in cursor.fetchall():
        actual_pin = val["pin_num"]
    
        if actual_pin == inputted_pin:
            status = True
            
        elif actual_pin != inputted_pin:
            status = False
    
    connection.close()
    return status



def new_acct(sql_username, sql_password, db_name):
    # ESTABLISH CONNECTION TO DATABASE
    try:
        cn_obj = pymysql.connect(
            host = "localhost",
            user = sql_username,
            password = sql_password,
            database = db_name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
    
    # TO CREATE A NEW ADDITIONAL ACCOUNT, FOR ONE SPECIFIC USER 
    print()
    print("=============================================")
    print("=============================================")
    print("===OPEN ANOTHER, NEW ACCOUNT===")
    print()
    print("Are you sure that you want to open another, new account in your name?")
    print("\nIf not, please interrupt the command line from running")
    input("===PRESS ENTER TO CONTINUE===")
    print("=============================================")
    print("=============================================")
    
    
    # need to get the customer's corresponding accounts using their 
    # customer_id to get their acct_num(s)
    spec_custID = int(input("Enter your CUSTOMER ID: "))
    cursor = cn_obj.cursor()
    query = ("select customer_id, account_num, account_type from customer_acctinfo_relationship join account_information using (account_num) where customer_id=%s")
    cursor.execute(query, (spec_custID))
    
    for row in cursor.fetchall():
        print("\n=============================================")
        print("===THESE ARE YOUR CURRENT ACCOUNTS===")
        print("---------------------------------------------------------------------------------------------------------------")
        print("CUSTOMER ID:", row["customer_id"], "ACCOUNT NUMBER:", row["account_num"], "ACCOUNT TYPE: ", row["account_type"])
        print("---------------------------------------------------------------------------------------------------------------")
        
    cursor.close()
    
    
    # CREATE NEW ACCOUNT HERE
    print()
    print("=============================================")
    print("The following 3 fields are required for Beantown Bank")
    print("=============================================")
    print("\nChoose an account type: [Checking], [Savings]")
    acct_type = input("Specify the type of account that you are opening (OMIT THE [], type exactly as it's written above):\n")
    balance = float(input("CREATE ANOTHER ACCOUNT: How much money would you like to \
                          insert into this account?                 \
                          This is your starting balance:\n"))
    print("=============================================")

    
    # Call the first account creation procedure to open fields in the customer
    # and account tables (establish a relationship between both entities)
    cursor = cn_obj.cursor()
    cursor.callproc("add_acct", (spec_custID, acct_type, balance))
    cursor.close()
    
    print("\n=============================================")
    end_msg = print("===You've officially opened a new account===\n")
    # print("===Begin a NEW session to perform ANOTHER operation===")
    print("=============================================")
    print("=============================================")
    
    cn_obj.close()
    return None




def withdrawal(sql_username, sql_password, db_name):
    # ESTABLISH CONNECTION TO DATABASE
    try:
        cn_obj = pymysql.connect(
            host = "localhost",
            user = sql_username,
            password = sql_password,
            database = db_name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
        
    # TAKE OUT A WITHDRAWAL, CHANGE THE ACCT_BALANCE (DONE IN MYSQL)
    # AND RETURN THE NEW ACCOUNT BALANCE TO THE USER
    print()
    print("=============================================")
    print("=============================================")
    print("===CASH WITHDRAWAL OPERATION===")
    print()
    print("Are you sure that you want to make a withdrawal?")
    print("If not, please interrupt the command line from running")
    input("===PRESS ENTER TO CONTINUE===")
    print("=============================================")
    print("=============================================")
    
    # first allow user to view all of their accounts, so they can select one
    # to withdraw money from
    print("\nCustomer ID needed to access account(s) information")
    cust_id = int(input("Enter your CUSTOMER ID: "))
    cursor = cn_obj.cursor()
    query = ("select customer_id, account_num, account_type from customer_acctinfo_relationship join account_information using (account_num) where customer_id=%s")
    cursor.execute(query, (cust_id))
    
    for row in cursor.fetchall():
        print("---------------------------------------------------------------------------------------------------------------")
        print("CUSTOMER ID: ", row["customer_id"], "ACCOUNT NUMBER: ", row["account_num"], "ACCOUNT TYPE: ", row["account_type"])
        print("---------------------------------------------------------------------------------------------------------------")
    cursor.close()
    
    
    # user needs to select the account they want to withdraw money from
    # then carry out the operation
    print()
    print("===Please specify which account you want to access to withdraw money from===")
    acct_num = int(input("\nInput the account's specific ACCOUNT NUMBER (integer): "))
    amt_money = float(input("\nInput the amount of money you are withdrawing (*can be a decimal*): "))
    
    cursor2 = cn_obj.cursor()
    cursor2.callproc("withdrawal_calc", (acct_num, amt_money))
    cursor2.close()
    
    # update other corresponding tables in the design/schema
    cursor3 = cn_obj.cursor()
    cursor3.callproc("after_withdrawal_update", (acct_num, amt_money))
    cursor3.close()
    
    
    print("\n=============================================")
    end_msg = print("===You've withdrawn money from your account===\n")
    # print("===Begin a NEW session to perform ANOTHER operation===")
    print("=============================================")
    
    cn_obj.commit()
    cn_obj.close()
    return None



def deposit(sql_username, sql_password, db_name):
    # ESTABLISH CONNECTION TO DATABASE
    try:
        cn_obj = pymysql.connect(
            host = "localhost",
            user = sql_username,
            password = sql_password,
            database = db_name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
        
    # TAKE IN A DEPOSIT, CHANGE THE ACCT_BALANCE (DONE IN MYSQL)
    # AND RETURN THE NEW ACCOUNT BALANCE TO THE USER
    print()
    print("=============================================")
    print("=============================================")
    print("===CASH/CHECK DEPOSIT OPERATION===")
    print()
    print("Are you sure that you want to make a deposit?")
    print("If not, please interrupt the command line from running")
    input("===PRESS ENTER TO CONTINUE===")
    print("=============================================")
    print("=============================================")
    
    
    # first allow user to view all of their accounts, so they can select one
    # to deposit money into
    print("\nCustomer ID needed to access account(s) information")
    cust_id = int(input("Enter your CUSTOMER ID: "))
    cursor = cn_obj.cursor()
    query = ("select customer_id, account_num, account_type from customer_acctinfo_relationship join account_information using (account_num) where customer_id=%s")
    cursor.execute(query, (cust_id))
    
    for row in cursor.fetchall():
        print("---------------------------------------------------------------------------------------------------------------")
        print("CUSTOMER ID: ", row["customer_id"], "ACCOUNT NUMBER: ", row["account_num"], "ACCOUNT TYPE: ", row["account_type"])
        print("---------------------------------------------------------------------------------------------------------------")
    cursor.close()
    
    
    # user needs to select the account they want to deposit money into
    # then make the deposit
    print("\n===Please specify which account you want to access to make a deposit===")
    acct_num = int(input("\nInput the account's specific ACCOUNT NUMBER (integer): "))
    amt_money = float(input("\nInput the amount of money you are depositing (*by cash or check, can be a decimal*): "))
    
    cursor2 = cn_obj.cursor()
    cursor2.callproc("deposit_calc", (acct_num, amt_money))
    cursor2.close()
    
    # update other corresponding tables in the design/schema
    cursor3 = cn_obj.cursor()
    cursor3.callproc("after_deposit_update", (acct_num, amt_money))
    cursor3.close()
    
    
    print("\n=============================================")
    end_msg = print("===You've deposited money into your account===\n")
    # print("===Begin a NEW session to perform ANOTHER operation===")
    print("=============================================")
    
    cn_obj.commit()
    cn_obj.close()
    return None



def balance_inq(sql_username, sql_password, db_name):
    # ESTABLISH CONNECTION TO DATABASE
    try:
        cn_obj = pymysql.connect(
            host = "localhost",
            user = sql_username,
            password = sql_password,
            database = db_name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
        
    # RETURN THE PRESENT ACCOUNT BALANCE TO THE USER
    print()
    print("=============================================")
    print("=============================================")
    print("===BALANCE INQUIRY OPERATION===")
    print()
    print("Are you sure that you want to view your account balance?")
    print("If not, please interrupt the command line from running")
    input("===PRESS ENTER TO CONTINUE===")
    print("=============================================")
    print("=============================================")
    
    # use customer_id to find the corresponding balance and return it to user
    # first allow user to view all of their accounts, so they can select one
    print("\nCustomer ID needed to access account balance information")
    cust_id = int(input("Enter your CUSTOMER ID: "))
    print()
    cursor = cn_obj.cursor()
    query = ("select customer_id, account_num, account_type from customer_acctinfo_relationship join account_information using (account_num) where customer_id=%s")
    cursor.execute(query, (cust_id))
    
    for row in cursor.fetchall():
        print("---------------------------------------------------------------------------------------------------------------")
        print("CUSTOMER ID: ", row["customer_id"], "ACCOUNT NUMBER: ", row["account_num"], "ACCOUNT TYPE: ", row["account_type"])
        print("---------------------------------------------------------------------------------------------------------------")
    cursor.close()
    
    
    # decide which account's balance to view
    print("\n===Please specify which account you want to access to view the corresponding balance===")
    acct_num = int(input("\nInput the account's specific ACCOUNT NUMBER (integer): "))
    
    cursor2 = cn_obj.cursor()
    query = "select get_acctBalance(%s)"
    cursor2.execute(query, (acct_num))
    
    for row in cursor2.fetchall():
        print("ACCOUNT BALANCE: ", row)
    cursor2.close()
    
    print("\n=============================================")
    print("===You have successfully viewed an account's balance===")
    #end_msg = print("===Begin a NEW session to perform ANOTHER operation===")
    print("=============================================")
    
    cn_obj.commit()
    cn_obj.close()
    return None



def delete_acct(sql_username, sql_password, db_name):
    # ESTABLISH CONNECTION TO DATABASE
    try:
        cn_obj = pymysql.connect(
            host = "localhost",
            user = sql_username,
            password = sql_password,
            database = db_name,
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True)
    
    except pymysql.Error as error:
        code, msg = error.args
        print("Cannot Connect to Database - ", code, msg)
        
    # TO DELETE (ONLY) ONE ACCOUNT OWNED BY ONE USER
    print()
    print("=============================================")
    print("=============================================")
    print("===ACCOUNT DELETION OPERATION===")
    print()
    print("Are you sure that you want to delete your account?")
    print("If not, please interrupt the command line from running")
    input("===PRESS ENTER TO CONTINUE===")
    print("=============================================")
    print("=============================================")
    
    
    # need to get the customer's corresponding accounts using their 
    # customer_id to get their acct_num(s)
    spec_custID = int(input("Enter your CUSTOMER ID: "))
    print()
    cursor = cn_obj.cursor()
    query = ("select customer_id, account_num, account_type from customer_acctinfo_relationship join account_information using (account_num) where customer_id=%s")
    cursor.execute(query, (spec_custID))
    
    for row in cursor.fetchall():
        print("---------------------------------------------------------------------------------------------------------------")
        print("CUSTOMER ID:", row["customer_id"], "ACCOUNT NUMBER:", row["account_num"], "ACCOUNT TYPE: ", row["account_type"])
        print("---------------------------------------------------------------------------------------------------------------")
    cursor.close()
    
    
    # decide which account to delete
    print("\n===Please specify which account you want to delete===")
    acct_num = int(input("\nInput the account's specific ACCOUNT NUMBER (integer): "))
    
    cursor2 = cn_obj.cursor()
    #cursor2.callproc("del_acct", (acct_num)) --> DOESN'T WORK, WEIRD ERROR
    # THEREFORE, USED DIFFERENT METHOD BELOW (HARDCODED)
    acct_info = """delete from account_information 
                   where account_num=%s
                """
    cursor2.execute(acct_info, (acct_num))
    cursor2.close()
    
    print("\n=============================================")
    end_msg = print("===You've successfully closed one of your accounts===\n")
    # print("===Begin a NEW session to perform ANOTHER operation===")
    print("=============================================")
    
    cn_obj.commit()
    cn_obj.close()
    return None



def main(): 
    
    # ========================================================================
    # Begin with master login to access DB, also contains the connection obj
    sql_username, sql_password, db_name = connection("atm_db")
    # ========================================================================
    
    
    # ========================================================================
    # Determine if person already is registered in bank
    register_status = int(input("Are you registered at Beantown Bank? \
                            TYPE: [YES = 1] [NO = 0]: "))
    # ========================================================================
    
    
    # ========================================================================
    # NOT REGISTERED - Person inputs Name (F, L) and Pin; added to dB
    while register_status == 0:
        register_status = create_acct(sql_username, sql_password, db_name)
    
        if register_status == 1:
            break
    # ========================================================================
    
    
    # ========================================================================
    # REGISTERED - Check for acct info (PIN) to access account 
    print()
    c_id = int(input("Enter your Customer ID: "))
    pin_check = int(input("Please enter your 4-digit PIN code: "))
    pcheck_status = check_pin(sql_username, sql_password, db_name, c_id, pin_check)
    
    while pcheck_status == False:
        print("\n===Access Denied: Your PIN is incorrect===")
        print("===PLEASE TRY AGAIN===")
        c_id = int(input("Enter your Customer ID: "))
        pin_check = int(input("Please enter your 4-digit PIN code: "))
        pcheck_status = check_pin(sql_username, sql_password, db_name, c_id, pin_check)
        
        if pcheck_status == True:
            print("\n===Access Granted: Your PIN is correct===")
            break
    # ========================================================================
    
    
    # ========================================================================
    while True:
        input("====PRESS ENTER TO CONTINUE====\n")
        # Allow access - prompt user for which operation they'd like to complete
        print()
        print("=============================================")
        print("=============================================")
        print("===Welcome to Beantown Bank's ATM Service!===")
        print("=============================================")
        print("=============================================")
        print()
        print("You are allowed to make the following 5 selections.")
        # print()
        # print("Please select 1 option. You'll need to sign in again")
        # print("- if you'd like to make another selection.")
        print("=============================================")
        print("=============================================")
        print()
        print("Choose 1 of the 5 operations: ")
        operations = ["[1. Open a New Account]", "[2. Cash Withdrawal]", "[3. Deposit]", "[4. Balance Inquiry]", "[5. Delete/Close Account]", "[6. Exit User Session]"]
        for i in range(len(operations)):
            print(operations[i])
        index = int(input("Choose an operation. Input the corresponding number:\n"))
        

        # OPEN NEW ACCOUNT OPERATION
        if index == 1:
            new_acct(sql_username, sql_password, db_name)
        
        # CASH WITHDRAWAL OPERATION
        if index == 2:
            withdrawal(sql_username, sql_password, db_name)    
            
        # DEPOSIT OPERATION
        if index == 3:
            deposit(sql_username, sql_password, db_name)
            
        # BALANCE INQUIRY (VIEW ACCOUNT BALANCE) OPERATION
        if index == 4:
            balance_inq(sql_username, sql_password, db_name)    
            
        # DELETE ACCOUNT OPERATION
        if index == 5:
            delete_acct(sql_username, sql_password, db_name)
        
        # END USER SESSION
        if index == 6:
            break
        # ========================================================================
        
main()
    