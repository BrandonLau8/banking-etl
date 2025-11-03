import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from decimal import Decimal


class Transaction:
    account_id: str
    txn_date: str
    post_date: str
    description: str
    amount: float
    category: str
    category2: str
    txn_type: str
    notes: str

    def __init__(self, account_id, txn_date, post_date, description, amount, category, txn_type):
        self.account_id = account_id
        self.txn_date = txn_date
        self.post_date = post_date
        self.description = description
        self.amount = amount
        self.category = category
        self.txn_type = txn_type

#load ENV files
load_dotenv()
path = os.getenv("BANK_FILE")
dbUser = os.getenv("POSTGRES_USER")
dbName = os.getenv("POSTGRES_DB")
dbPassword = os.getenv("POSTGRES_PASSWORD")
dbHost = os.getenv("POSTGRES_HOST")
dbPort = os.getenv("POSTGRES_PORT")

#Read CSV file
data = pd.read_csv(path)

#Get Account ID
directory = os.path.dirname(path)
account_id = os.path.basename(directory)
print(account_id)

#Create df
df = pd.DataFrame(data)
# print(df.head(10))

#Iterate through each row of df
transactions = []
n_Rows = len(df)
for n in range(n_Rows):
    row = df.iloc[n]

    #Iterate through each column of selected row

    
    if account_id in ['Chase4659', 'Chase6589']:
        #Transaction Date
        txn_date_str = row.iloc[0]
        
        #Post Date
        post_date_str = row.iloc[1]

        #Description and Category
        description = row.iloc[2]
        category = row.iloc[3]

        #Amount
        amount_float = row.iloc[5]

    elif account_id == 'Chase9072':
        #Transaction Date
        txn_date_str = row.iloc[0]

        #Post Date
        post_date_str = txn_date_str

        #Description and Category
        description = row.iloc[1]
        category = None

        #Amount
        amount_float = row.iloc[2]
       
    else:
        exit()
    
    txn_date_obj = datetime.strptime(txn_date_str, "%m/%d/%Y").date() #turns to YYYY-MM-DD
    post_date_obj = datetime.strptime(post_date_str, "%m/%d/%Y").date()
    amount_str = str(amount_float)
    amount_dec = Decimal(amount_str)

    #Categorize Amount
    if amount_dec < 0:
        txn_type = 'Expense'
    else:
        txn_type = 'Income'

    #List of Transactions
    transactions.append(Transaction(
        account_id= account_id,
        txn_date=txn_date_obj,
        post_date=post_date_obj,
        description=description,
        amount=amount_dec,
        category=category,
        txn_type=txn_type
    ))

#Connect to existing database
conn = psycopg2.connect(
    dbname = dbName,
    user= dbUser,
    password = dbPassword,
    host = dbHost,
    port = dbPort
    
)

#Open a cursor to perform database operations
cur = conn.cursor()

#Pass data to DB
def executeQuery():
    for transaction in transactions:
        cur.execute("INSERT INTO transactions (account_id, txn_date, post_date, description, amount, category, txn_type) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;", 
                    (transaction.account_id,
                    transaction.txn_date,
                    transaction.post_date,
                    transaction.description,
                    transaction.amount,
                    transaction.category,
                    transaction.txn_type
                    )
                    )

#Make changes to DB persistant 
try:
    executeQuery()
    conn.commit()
    print("Success!")
except Exception as e:
    conn.rollback()
    print("Something went wrong:", e)

#Close communication with DB
cur.close()
conn.close()
