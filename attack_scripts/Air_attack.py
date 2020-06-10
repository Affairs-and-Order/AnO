import random


nat1_fighters = Nat1
nat2_fighters = Nat2

#TODO: get nation names from DB, get amount of fighters and bombers from DB,add infra damage,make aircraft consume resources
#TODO: figure out how calculate bomber and fighter losses seperatly 


# print statements
def ground_attack(nat1_name, nat2_name, nat1_fighters, nat2_fighters,Nat1Bomb,Nat2Bomb):
nat1_roll_wins = 0
nat2_roll_wins = 0
for roll in range(0, 3):
	nat1_roll = random.randint(1, Nat1 + 5*Nat1Bomb)
	nat2_roll = random.randint(1, Nat2 + 5*Nat2Bomb)
	print(
		f"This is random output of aircraft going to dogfight for Nat1: {nat1_roll} out of {Nat1} Fighters {Nat1Bomb} Bombers.."
	)
	print(
		f"This is random output of aircraft going to dogfight for Nat2: {nat2_roll} out of {Nat2} fighters and {Nat2Bomb} Bombers.."
	)
	# difference between the two rolls
	difference = abs(nat1_roll - nat2_roll)

	if nat1_roll > nat2_roll:
		nat1_roll_wins += 1
		# subtract difference from the nations maximum if they rolled lower
		Nat2 -= difference
		#calulates bomber losses
		Bombloss1 = random.randint (1, Nat1Bomb // 5) * 5
		Nat1Bomb = Nat1Bomb - Bombloss / 5
		displayloss1 = Bombloss1 / 5
		Bombloss2 = random.randint (1, Nat2Bomb // 5) * 5
		Nat2Bomb = Nat2Bomb - Bombloss2 / 5
		displayloss2 = Bombloss2 / 5
		print(f"Nation 2 lost {displayloss2} Bombers")
		# gives a 6% casualty rate for the nation that rolled larger 
		six_percent_loss = int(Nat2 * 0.06)
		Nat1 -= six_percent_loss
		#ends battle if aircraft are destroyed
		if  Nat2 and Nat2Bomb <= 0:
			Nat2 = 0
			Nat2Bomb = 0
			break
			print("nation 1 won the battle")
	else:
		nat2_roll_wins += 1
		# subtract difference from the nations maximum if they rolled lower
		Nat1 -= difference
		# the twelve percent stored in new variable so it can be printed
		Bombloss1 = random.randint (1, Nat1Bomb // 5) * 5
		Nat1Bomb = Nat1Bomb - Bombloss / 5
		displayloss1 = Bombloss1 / 5
		Bombloss2 = random.randint (1, Nat2Bomb // 5) * 5
		Nat2Bomb = Nat2Bomb - Bombloss2 / 5
		displayloss2 = Bombloss2 / 5
		print(f"Nation 2 lost {displayloss2} Bombers")
		six_percent_loss = int(Nat1 * 0.06)
		Nat2 -= six_percent_loss
		
		print(f"Nation 1 lost {displayloss1} Bombers")
		#endsbattle if all are destroyed
		if  Nat1 and Nat1Bomb <= 0:
			Nat1 = 0
			Nat1Bomb = 0
			break
			print("nation 2 won the battle")

	print(f"This is the output after the battle: {difference}")
	print(f"This is the 6 percent value from the battle: {six_percent_loss}")
  
if nat1_roll_wins > nat2_roll_wins:
	print(f"{nat1_name} won the battle")
else:
	print(f"{Nat2_name} won the battle")
ground_attack("Danzig", "Konigsburg", 630, 380,4,10)

