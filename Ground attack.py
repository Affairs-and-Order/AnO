import random
#gets amount of soldiers in a given nation 
#will be upated once DB is setup
Nat1 = int(input("amount"))
Nat2 = int(input("amount"))
#rolls a random number between one and the amount 
#will be changed so num cant be less than 30% of amount
random_roll_nat1 = random.randint(1, Nat1)
random_roll_nat2 = random.randint(1, Nat2)
#compares roll and subracts differance from the smaller one
goto_war = abs(random_roll_nat1 - random_roll_nat2)
#subtracts 12% of smaller amount from larger one
percent_subtract = (goto_war * 1.12) - goto_war
print(f"This is Nat1 input: {Nat1}")
print(f"This is Nat2 input: {Nat2}")
print(f"This is random output of soldiers going to war for Nat1: {random_roll_nat1} out of {Nat1} soldiers..")
print(f"This is random output of soldiers going to war for Nat2: {random_roll_nat2} out of {Nat2} soldiers..")
print(f"This is the output after the battle: {goto_war}")
print(f"This is the 12 perecent value from the battle: {percent_subtract}")
