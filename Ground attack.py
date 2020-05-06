import random

Nat1 = 2000 # get from database for now lets call it 2000
Nat2 = 1000 # get from database for now lets call it 1000
#TODO: get nation names from DB, get amount of soldiers from DB,add tanks to script,add infra damage
random_roll_nat1 = random.randint(1,Nat1)
random_roll_nat2 = random.randint(1,Nat1)

# print statements

nat1_roll_wins = 0
nat2_roll_wins = 0
for roll in range(0,3):
    nat1_roll = random.randint(1,Nat1)
    nat2_roll = random.randint(1,Nat2)
    print(f"This is random output of soldiers going to war for Nat1: {nat1_roll} out of {Nat1} soldiers..")
    print(f"This is random output of soldiers going to war for Nat2: {nat2_roll} out of {Nat2} soldiers..")
    # difference between the two rolls
    difference = abs(nat1_roll - nat2_roll)
    
    if nat1_roll > nat2_roll:
        nat1_roll_wins += 1
        # subtract difference from the nations maximum if they rolled lower
        Nat2 -= difference
        # gives a 12% casualty rate for the nation that rolled larger 
        twelve_percent_loss = int(Nat2*0.12)
        Nat1 -= twelve_percent_loss
    else:
        nat2_roll_wins += 1 
        # subtract difference from the nations maximum if they rolled lower
        Nat1 -= difference
        # the twelve percent stored in new variable so it can be printed
        twelve_percent_loss = int(Nat1*0.12)
        Nat2 -= twelve_percent_loss
        
    print(f"This is the output after the battle: {difference}")
    print(f"This is the 12 perecent value from the battle: {twelve_percent_loss}")
    
    
    
    
if nat1_roll_wins > nat2_roll_wins:
    print("Nation 1 won the battle")
else:
    print("Nation 2 won the battle")
