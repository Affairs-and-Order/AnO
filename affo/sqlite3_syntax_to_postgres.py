# SIMPLE TESTING SCRIPT I WROTE
# DO NOT USE FOR NOW
file = 'testing_syntax.py'

total_queries = 0 # Works fine, can use

output = open(f"{file}_tested.py", "w")
with open(file) as f:
    for line in f.readlines():
        if 'db.execute' in line:
            total_queries += 1
            line = line.replace('(?)', "%s'")
            line = line.replace('?', "%s'")
            output.write(line)
        else:
            output.write(line)