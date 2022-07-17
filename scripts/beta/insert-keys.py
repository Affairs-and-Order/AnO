import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
import openpyxl

conn = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))

db = conn.cursor()

path = "./ano_betatesters.xlsx"
wb = openpyxl.load_workbook(path)
ws = wb['Sheet1']
idx = 1
for cell in ws['D']: # key
    key = cell.value
    if key is not None and key != "Key":
        # I know this is a very bad practice, but for 88 rows the performance is negligible.
        # Fix, if more keys required with one INSERT statement.
        db.execute("INSERT INTO keys (key) VALUES (%s)", (key,))
        print(f"{idx}. Inserted key - {key}")
        idx += 1

conn.commit()
conn.close()