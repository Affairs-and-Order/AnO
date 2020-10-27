import os

file = 'tests.py'
output = open('converted.py', "w")

files = ["app.py", "coalitions.py", "countries.py", "formula.py",
"helpers.py", "intelligence.py", "login.py", "market.py", "military.py",
"province.py", "signup.py", "testing.py", "testroutes.py", "units.py",
"upgrades.py", "wars.py"]

new_files = []

for filename in files:
    substr = ".py"
    inserttxt = "1"

    idx = filename.index(substr)
    new_filename = filename[:idx] + inserttxt + filename[idx:]
    os.rename(filename, new_filename)
    new_files.append(new_filename)

all_files = zip(new_files, files)

for new_file, old_file in all_files:
    output = open(old_file, "w")
    with open(new_file) as f:
        for line in f.readlines():
            if 'import sqlite3' in line:
                new_line = line.replace('import sqlite3', 'import psycopg2')
                output.write(new_line)
            elif "connection = sqlite3.connect('affo/aao.db')" in line:
                new_line = line.replace("connection = sqlite3.connect('affo/aao.db')",
"""
connection = psycopg2.connect(
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD"),
    host=os.getenv("PG_HOST"),
    port=os.getenv("PG_PORT"))
""")
                output.write(new_line)
            elif 'connection = sqlite3.connect("affo/aao.db")' in line:
                new_line = line.replace('connection = sqlite3.connect("affo/aao.db")',
"""
    connection = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))
""")
                output.write(new_line)

            elif '?' in line and 'db.execute' in line:
                new_line = line.replace('?', '%s')
                if '.fetch' in line:
                    fetching = '.fetch' + line.split(".fetch", 1)[1]
                    new_line = new_line.replace(fetching, "")
                if '=' in line:
                    variable = line.partition("db.execute(")[0]
                    new_line = new_line.replace(variable, "")

                try:
                    full_cursor = variable + 'db' + fetching
                except: 
                    full_cursor = variable + 'db'

                output.write(new_line)
                output.write(f'\n{full_cursor}')
            else:
                output.write(line)