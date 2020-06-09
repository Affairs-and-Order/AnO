import random
import sqlite3


def ground_attack(nat1_name, nat2_name, nat1_soldiers, nat2_soldiers):
    
    #TODO: get nation names from DB, get amount of soldiers from DB,add tanks to script,add infra damage
    random_roll_nat1 = random.randint(1, nat1_soldiers)
    random_roll_nat2 = random.randint(1, nat1_soldiers)

    # print statements

    Nat1 = nat1_soldiers
    Nat2 = nat2_soldiers

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
            print(f"This is the Nation 2's casualties after the battle: {difference}")
            print(f"This is the is Nation 1's casualties from the battle: {twelve_percent_loss}")
        else:
            nat2_roll_wins += 1 
            # subtract difference from the nations maximum if they rolled lower
            Nat1 -= difference
            # the twelve percent stored in new variable so it can be printed
            twelve_percent_loss = int(Nat1*0.12)
            Nat2 -= twelve_percent_loss  
            print(f"This is the Nation 1's casualties after the battle: {difference}")
            print(f"This is the is Nation 2's casualties from the battle: {twelve_percent_loss}")
        
        
    
        
    if nat1_roll_wins > nat2_roll_wins:
        print("Nation 1 won the battle")
    else:
        print("Nation 2 won the battle")

ground_attack("Blackadder", "CLRFL", 1500, 1500)

