import random
Nat1 = 50  # get from database for now lets call it 50
Nat2 = 350  # get from database for now lets call it 60
Nat1Bomb = 66
Nat2Bomb = 6
#TODO: get nation names from DB, get amount of fighters and bombers from DB,add infra damage,make aircraft consume resources
#TODO: figure out how calculate bomber and fighter losses seperatly 
random_roll_nat1 = random.randint(1, nat1 + 5*nat1bomb)
random_roll_nat2 = random.randint(1, nat2 + 5*nat2bomb)

# print statements

nat1_roll_wins = 0
nat2_roll_wins = 0
for roll in range(0, 3):
	nat1_roll = random.randint(1, Nat1)
	nat2_roll = random.randint(1, Nat2)
	print(
		f"This is random output of aircraft going to dogfight for Nat1: {nat1_roll} out of {Nat1} aircraft.."
	)
	print(
		f"This is random output of aircraft going to dogfight for Nat2: {nat2_roll} out of {Nat2} aircraft.."
	)
	# difference between the two rolls
	difference = abs(nat1_roll - nat2_roll)

	if nat1_roll > nat2_roll:
		nat1_roll_wins += 1
		# subtract difference from the nations maximum if they rolled lower
		Nat2 -= difference
		# gives a 6% casualty rate for the nation that rolled larger 
		six_percent_loss = int(Nat2 * 0.06)
		Nat1 -= six_percent_loss
	else:
		nat2_roll_wins += 1
		# subtract difference from the nations maximum if they rolled lower
		Nat1 -= difference
		# the twelve percent stored in new variable so it can be printed
		six_percent_loss = int(Nat1 * 0.06)
		Nat2 -= six_percent_loss

	print(f"This is the output after the battle: {difference}")
	print(f"This is the 6 percent value from the battle: {six_percent_loss}")

if nat1_roll_wins > nat2_roll_wins:
	print("Nation 1 won the battle")
else:
	print("Nation 2 won the battle")
