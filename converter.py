file = 'upgrades1.py'
output = open('upgrades.py', "w")

with open(file) as f:
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

            full_cursor = variable + 'db' + fetching
            output.write(new_line)
            output.write(f'\n{full_cursor}')
        else:
            output.write(line)
        