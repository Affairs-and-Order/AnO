[![DeepSource](https://static.deepsource.io/deepsource-badge-light-mini.svg)](https://deepsource.io/gh/delivey/AnO/?ref=repository-badge)
# Affairs-and-Order

Affairs & order is a nation simulation game, where you can make your own nation, build a military and industry, and declare war.

# Repo installation.

1. Install Git and add Git to PATH. https://stackoverflow.com/questions/26620312/installing-git-in-path-with-github-client-for-windows
2. Type `git clone https://github.com/delivey/AnO.git` in the folder you want the repo to be cloned in.

# Basic install

## Flask

1. Install Python (Preferrably 3.8) https://www.python.org/downloads/release/python-380/.
2. Run `pip install -r requirements.txt`, this will install all the modules needed for this repo.
3. Type `flask run` in this repo's folder on your own PC.
4. Navigate to `http://127.0.0.1:5000/` or the url flask gave you in your browser. The website should run

# More advanced (not necessary for development)

# PostgresQL (no need for now)

### Windows
1. Get the `.exe` installer from here: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads. Download version 12.3
2. Run the installer, leave the default port and other default settings, set your password as `ano`
3. Run the `postgres_setup.py` file in AnO/affo to create your database instance.

# RabbitMQ

### Arch

1. Install rabbitmq by typing `pacman -S rabbitmq`
2. Follow this guide: https://docs.celeryproject.org/en/stable/getting-started/brokers/rabbitmq.html and name your username, password and vhost `ano`
3. Run rabbitmq by typing: `sudo rabbitmq-server`

### Debian

1. Follow this guide to install RabbitMQ: https://www.vultr.com/docs/how-to-install-rabbitmq-on-ubuntu-16-04-47 and name your username, password and vhost `ano`
2. Stop the rabbitmqctl service for naming usernames, vhosts, etc by typing: `sudo rabbitmqctl stop`
3. Run the RabbitMQ broker by typing: `sudo rabbitmq-server`

# Celery

#### IMPORTANT NOTE: open all your terminals using `sudo -i`, this will give root access to celery.
1. Navigate into the `AnO` folder.
2. Run the beat pool by running: `celery -A app.celery beat --loglevel=INFO` in the terminal.
3. Run *1* worker by running: `celery -A app.celery worker --loglevel=INFO` in another terminal window.
4. For `celery` to work, RabbitMQ must be running.

Affairs and Order
Now crystal free!


Many of the things here are not what we have decided upon. They are ideas


Affairs and Order
General Stuff
Why it’s different from PnW / Don / NG:
What shall we call said world:
How should we split the revenue? What amount:
Coalitions
Resources:
Raw resources:
Processed resources:
Uses for resources:
Provinces
Cities:
Land
Categories:
City infrastructure:
Electricity:
Retail:
Projects
Land infrastructure:
Raw Industry
Military:
Processing:
Laws
Economics:
Punishment:
War policy:
Public Works Projects
Continents
War
Land
Soldiers
Tanks
Artillery
Air
Flying fortress
Bomber jets
Water
Destroyers
Cruisers
Submarines
Attacking mechanics

General Stuff

VC stuff we discussed that’s worthwhile implementing

Limit daily bank withdrawal amount

market offers fee to stop 

Unique IDs for coalitions to be required to send bank transactions and treaties

Can purchase insurance to stop offshores

Auto trading

Nukes able to destroy public works

Specialization of resource production. Increase of certain resource production for production buildings in that country.

Lots of public works

When you beat enemy you can occupy their provinces for some time

They can give up the provinces for a cost


Coalitions can create blocs, blocs can declare war on other blocs

Minigame that increases country happiness - capped at max happiness 

In game sue for peace feature



Countries: 


New:

Unable to be attacked until they attack or they are in the bottom 25% of all countries influence

MINIGAMES
Sumo wrestling - feed your warrior rations to upgrade them, fight other peoples sumos


What shall we call said world:

Terra



How should we split the revenue? What amount:

If the game makes revenue it will be split according to work done by each person.


Coalitions

Coalition typed: trade war eco bank




Eco:



War:

+15% defensive war bonus vs coalitions you haven’t declared war on
While at war you may only trade within your own coalition 
+8% bonus vs declared on coalition

Bank:



Resources:


Raw resources:

Bauxite
Rations
Uranium 
Iron
Coal
Oil
Lead
Copper
Lumber

Processed resources:

Components - aluminium + steel
Steel-  Coal + Iron
Aluminum - Bauxite
Gasoline - oil
Ammunition - lead
Consumer Goods - copper

If your people have rations: Rations increases consumer spending by 300%
If your military has ammunition: Ammunition increases military power (for every unit) by 1.5x


Provinces

Provinces start with 1 city slot and 1 land slot.

Each province costs 50k rn. To change that, please edit this document -- t0dd








Cities:





More cities can be purchased at an increasing cost for every time. Each city provides another 3 infrastructure slots and +1% overall consumer spending in the province.


Land
Population - increases tax income
Happiness - affects population ( -100% - 100%)
Pollution - decreases population (0% - 100%)
Productivity - affects resource production ( 0% - 100%)
Consumer Spending - affects tax income  ( -100% - 100%)







Categories:
City infrastructure:



Electricity:

Coal burner + 4 energy + 30 POLLUTION- $40K / HOUR

Oil burner + 3 energy + 25 POLLUTION -$60K / HOUR

Solar field + 3 energy -$150K / HOUR

Hydro Dam + 6 energy- $250K / HOUR

Nuclear Reactor +12 energy -$1.2M / HOUR

NOTE: 1 energy = 1 infrastructure slot (that isn’t electricity) powered. Talk with carson if this is unclear


Retail:

(requires city slots)

Gas Station +4 consumer goods -$20K / HOUR MAX 4

General Store +9 consumer goods -$35K / HOUR MAX 4

Farmers Market +15 consumer goods -$110K / HOUR MAX 4

Mall +22 consumer goods -$300K / HOUR MAX 4


Bank +30 consumer goods -$800K / HOUR MAX 4




Public Works


City Park +3% happiness -$20K / HOUR MAX 4

Hospital +8% happiness -$60K / HOUR MAX 4

Library + 5% happiness +5% productivity -$90K / HOUR MAX 2

University + 12% productivity -$150K / HOUR MAX 2


Skytrain + 15% productivity -$210K / HOUR MAX 2



types:
Land infrastructure:
Industry


(requires land slots)

(4 produable resources per nation)

Rations ALWAYS: Farm + 30 food / HOUR PER / 1 land slot -3K /HOUR

4 other continent specific resources

Pumpjacks - oil +25 oil -$10K / HOUR

Coal mine - Coal oil +25 Coal -$10K / HOUR


Bauxite mine Bauxite +25 Bauxite -$8K / HOUR

Copper mine Copper +25 Copper -$8K / HOUR

Uranium mine Uranium +25 Uranium -$18K / HOUR

Lead mine Lead +25 Lead -$12K / HOUR

Iron mine Iron +25 Iron -$12K / HOUR



Military:


(requires land slots)

Army Base - allows you to recruit land units -$25K / HOUR

Harbour - allows you to recruit water units -$35K / HOUR

Aerodrome - allows recruit of air units -$55K / HOUR

Administrative building - allows recruitment of spies -$60K / HOUR

Silo - allows production of missiles and nukes when researched -$120K / HOUR





Processing:

(requires land slots)


Components factory - produces components  converts 40 oil into 5 components/ HOUR -$220K / HOUR

Steel Mill - converts 35 coal and iron into 15 steel / HOUR -$180K / HOUR

Ammunition Factory - converts 10 copper and 20 lead into 10 ammunition / HOUR -$140K / HOUR

Aluminum refinery - converts 15 bauxite into 12 aluminum/ HOUR -$150K / HOUR


//not enough space
Warehouse - produces consumer goods

Oil processor - converts 20 oil into 8 gasoline / HOUR -$160K / HOUR









Infrastructure






Every turn (1 hour) the infrastructure produces a set amount of resources, or if it’s a processing infrastructure, it converts raw resources into processed.

Each infrastructure has an upkeep (money) the upkeep cost should disway players from building processing plants / nuclear power early on as you would need lots of processing plants and lots of infrastructure to be profitable (see below)

The more of one type of infrastructure you have in the province gives a 2% production speed increase. This applies to RETAIL, INDUSTRY, and PROCESSING.





War policy:






Public Projects

2 project slots every province you own
7 day project timer
15-20 total projects
More branching off projects, 3 or 4 tiers 

Propaganda Center:

Loose 10% less morale in war, at anupkeep cost of 150,000 a day

Homeless Shelters: Happiness + 15%

nuclear testing facility: Allows development and deployment of nuclear bombs and advanced nuclear power plants to be built

Missile Launch Base: Allows the development and and deployment short range missiles (they can only hit nations in the continent they are on)

Intercontinental Missile Launch Base:Allows the deployment and development of long range missiles (they can hit any nation regardless of continent)

Mercenary Market:allows the buying and selling of military units
Continents 


valenge +58% boost in oil production and +80% boost in food 
Description:Valenge is a continent in the north west with very mountainous terrain but a extremely fertile shoreline 

Kaltenot -80% production in oil -75% production in coal -100% food production 
Description:Kaltenot is a cold glacier at the bottom of the world with small oil and coal deposits under the ice

Aquilauru +67% production in gold -60% production of copper 
-70% production of food
Description: Aquilauru is a gold rich continent in the north of the world with small deposits of copper on the landmass but it is generally cold making unfit for food production

Easting +40% uranium production +26% bauxite production -20% in silicon production -80% food production
Description:Easting is a continent in the middle of the world its has large uranium and bauxite deposits with some small silicon deposits its mainly filled with deserts meaning its not very fertile

Fertorien -70% lead production -60% iron production +20% thorium production +120% food production 
Description: Fertorien is a continent in the far east it has extremely fertile fields and large thorium deposits and some small lead and iron deposits 

Bosfront -20% plutonium production 
+44% iron production +13% copper production -78% food production 
Description: Bosfront is a continent in the northeast it has some plutonium deposits in its valleys and large amounts of copper and iron in its mountains 

Helrursus +6% silicon production -15% gold production -73% lead production -30% food production 
Description:Helrursus is a continent in the southeast just south of Bosfront it has a decent amount of silicon and gold with some small amounts of lead and fertile land

If a resource isnt on a continent it cant be produced there except water that stays at base production 


War
multiply all your unit powers together, with bonuses if a counter is found
multiply all enemy defending units together, with bonuses if a counter is found

if your score is higher by 3x, annihilation, 
if your score is higher by 2x, definite victory
if your score is higher, close victory, 
if your score is lower, close defeat, 0 damage, 
if your score is lower by 2x, massive defeat, 0 damage

6 Types of control gained from annihilation (resource, field, city, depth, blockade, air):
soldiers: resource control
tanks: field control and city control
artillery: field control
destroyers: naval blockade
cruisers: naval blockade  
submarines: depth control
bombers: field control
apaches: city control
fighter jets: air control
    
Counters:
soldiers beat artillery
tanks beat soldiers
artillery beat tanks
destroyers beat submarines
cruisers beat destroyers
submarines beat cruisers
bombers beat soldiers, tanks, destroyers, cruisers, submarines
apaches beat soldiers, tanks, bombers, fighter jets
fighter jets beat bombers

Bonuses gained from control
Resource control: soldiers can now loot enemy munitions (minimum between 1 per 100 soldiers vs Random 10-90% of their total munitions)
field control: soldiers gain 2x power
City control: 2x morale damage
Depth control: missile defenses go from 50% to 20% and nuke defenses go from  35% to 10%
 Blockade: enemy can no longer trade
 Air control: enemy bomber power reduced by 60%


WAR POLICIES:
  "empire builder"--> winning gives no loot 2x reparation tax
 "pirate" --> winning gives 2x more loot no reparation tax
 "tactical" --> winning gives 1x loot 1x reparation tax
 "pacifist" --> winning gives no loot no reparation tax, lowers project timer by 5 days, boosts your economy by 10%
 "guerilla": --> winning gives 1x loot no reparation tax, losing makes you lose 40% less loot, and you resist 60% of imposed reparation tax. 

WAR TYPES
“raze" --> no loot, no reparation tax, destroy 10x more buildings, destroys money/res
“sustained" --> 1x loot, 1x infra destruction, 1x building destroy
“loot" --> 2x loot, 0.1x infra destruction, buildings cannot be destroyed

War selection and process:

Wars may last no longer than 3 days

If you do not attack for 1.5 days the war will end automatically.

Wars should not be shorter than 1.5 days no matter how much stronger one nation is over another.

You may only send your units into one offensive battle at a time (you can split your army and send certain units to other attacks) but all defensive battles

You may only attack other players who have -10% of your influence and +100%



Attacking players may select a category, then a unit. To win a war you must take the down to 0 morale (from 100%)

Actions: You perform actions once you have 200 supplies. Supplies can stack up until the war ends. You produce 100 every turn (2,400 / day). The more supplies you have, the more affective your attack will be.
(Attacking with soldiers and 400 supplies will be as powerful as attacking twice with soldiers and 200 supplies each time) (2 attacks at 200 supplies = as strong as 1 attack at 400 supplies)

Once you have the necessary 200 supplies you can attack with either your army, air force, navy, or special units. Once you have selected a category, you can choose one of the 3 units in the category to attack with. 
Special exceptions: Spies cost 0 supplies, ICBMs cost 500, and Nukes cost 1,000 supplies.

Extra actions: 

You can fortify from enemy advancements. Fortifying costs 200 supplies and gives defensive troops in that province 30% more effectiveness against soldiers, tanks, and apaches. Fortification ends with an attack using any soldiers, tanks, artillery, or apaches. 


Provinces all have 100 morale in each individual war. Attacking defensive war brings down morale. When morale reaches 0 the province will riot and you have a 15% chance to loose any infrastructure in that province. If they do riot, the number of infrastructure lost is 3/10.

If you loose the war you are entitled to pay a days worth of income and ½ of resources on hand. You may go in debt if you do not have the money to pay out. The days worth of revenue is subtracted BEFORE the resources on hand.

Categories:

Land, air, water - mixed in is high damage, normal, and high attack speed

High damage strong vs area of effect
Normal good against high damage
Area of effect powerful when fighting normal

Special

Spies:

COST $25,000 50 rations

In war spies can perform operations to gather intelligence, maybe attack morale
When in peacetime, spies only are able to gather intelligence about a rival nation.


ICBMs:

COST $4,000,000 350 steel

Amazing at taking out infrastructure (2x)

Nukes:

COST $12,000,000 800 uranium 600 steel


Very powerful against enemy economy

Land

Soldiers
Base power 1
Consumes 1 munitions per 5000 soldiers to fight
May give the option to fight without munitions at 10% effectiveness
COST $200 2 rations


Counter artillery, apaches, obtain resource control

Tanks
Base power 40
Consumes 1 munitions and 2 gasoline per 100 tanks to fight
COST $8,000 5 steel, 5 components


Counter soldiers, obtain field control and city control

Artillery
Base power 80
Consumes 5 munitions and 1 gasoline per 100 artillery to fight
COST $16,000 12 steel, 3 components


Counter tanks, obtain field control

Air
Bombers
Base power 100
Consumes 4 munitions and 10 gasoline per 100 bombers to fight
COST $25,000 20 aluminium 5 steel 6 components
Counters soldiers, tanks, destroyers, submarines, obtains field control
Maybe can destroy supplies (if this is needed for the game to be enjoyed)
Fighter jets
Base power 100
COST $35,000 12 aluminium 3 components


Counter bombers, obtain air superiority



Apaches

Base power 100
COST $32,000 8 aluminium 2 steel 4 components

Counter tanks, bombers, fighter jets, obtains city control


Water


Destroyers

Base power 100
COST $30,000 30 steel 7 components


Counters submarines, obtains naval blockade

Cruisers

Base power 200
COST $55,000 60 steel 12 components


Counters destroyers, fighter jets, apaches, obtains naval blockade

Submarines

Base power 100
COST $45,000 20 steel 8 components


Counters cruisers, obtains depth control

Control bonuses:
Resource control: soldiers can now loot enemy munitions (minimum between 1 per 100 soldiers and 50% of their total munitions)
Field control: soldiers gain 50% bonus power
City control: +40% + 1 flat morale damage per attack
Depth control: Enemy iron dome effectiveness reduced from 50% to 20%, and vital defense system reduced from 35% to 10%.
Naval blockade: enemy can no longer trade, or transfer
Air superiority: enemy bomber power reduced by 70%

Attacking mechanics

When you win / loose you get a gif

War fatigue: after declaring a war you cannot declare a war again for some time
This is to stop a player from constantly bombarding a player 

Attacking pits your units against the enemy units you choose (no civilian / economy damage) when you win the war you then inflict civilian and eco damage.

The more of a type of military building you have the cheaper ($) by % recruiting that military type will be



“Annihilating” the opponent entitles you to 25% of their income for the next 3 days

Cities have 100 “health” per war. When they reach 0% they riot and you loose => 10% of your total infrastructure slots (only loose the actual infrastructure buildings)

Coalitions


New coalitions:

Unable to be attacked until a coalition attacks. Downsides (no war, -35% economic output, no propaganda) must also be in the bottom 25%


Propaganda:


Allows you to share recruitment messages to the find coalition page (link through coalitions) good for acquiring members


Diplomacy:




Declaration of war:



Types:

(Able to change every 30 days)

Trading coalition 


0% tariff costs 


Economic coalition


+10% tax production


Military coalition


+12% military cap


Coalition levels


Levels increase based on alliance influence


Start at 1

2:

-1% military upkeep

3:

+2.5% resource production

4:





supplies are kinda a rename of military action points


Asynchronized 
Attacker clicks attack when they have a 2000 supplies, smallest attack 200 supplies for a soldier attack. Every hour, gain 50 supplies -> one day is 1200 supplies. Takes 1 day and 16 hours to build up 2000 supplies. 
In comparison, a PnW maximum soldier + tank ground attack takes 6 hours.

Attacker attacks with just soldiers, costing 200 supplies, showing results. Then they have 1000 supplies left to keep attacking with 100% counters?

Optional: (Wars never show what units defending country defended with.)
Must rely on spies to see defending units

War fatigue - can’t attack the same person for 2 weeks
Stops players from beating down opponents over and over
All users can choose a default defense pickable in the war menu as soon as the account is made (after tutorial)

A country losing a war gets a peace timer. Further losses from wars that were already ongoing resets the peace timer.

You may only declare on -1 0 or +1 provinces from your own number

(I have 6 provinces, I can delacre on people with 5, 6, and 7 provinces)


Picks 3 units
3 attack units



3 defense units

User can choose this in /war maybe
If they don’t choose it randomly chooses 3

20k soldiers
1k tanks
1 planes
50 ships


Vs 



Lets say a country makes ONLY 5 factories, 5 hangars, 5 carrier docks
+50% bonus
15 tank
0
0
15 bomber
0
0
15 carrier
0
0

Starting out counters to be 400% bonus damage against the counter

Another country makes
5 soldier
5 tank
5 artillery
5 bomber
5 fighter
5 apaches
2 submarines
2 cruisers
2 destroyers

3 specials:
Spies
Missiles
nukes
5 5 5 +bonus% = $1M
2 2 2 = $1M



Communication between back end and war management menu

Page 1:
Goes to a page where each 3 units choose what type of unit to attack with (12 options, 9 war and 3 special)
War
9 check boxes

Special operations
3 check boxes 

Continue button

Page 2:
Goes to a page where you choose how many to send of each of your 3 units, or 1 special

Page 3:
Goes to a page where you target what all your units attack (12 options: 9 war units, 3 specials,) (targeting 3)

Page 4:
Whoever lost fewer value in units is the winner. Based on the degree, morale changes. If a country loses by having their morale pushed to 0, the other country sets a tax on them for a week based on how high the winning country’s morale was. Every 1 morale the winner had left after victory imposes a 0.2% tax on the losing nation. Ex. A 100 vs 0 morale victory imposes a 20% tax on the losing nation. Every next victory on the same losing nation taxes by weighted share. Ex: 1 victory: (80, 20). 2 victors: (80, 20, 20). 3 victors: (80, 20, 20, 20) etc. The tax lasts for 1 day, 2 days if your nation type is “merciless conqueror”.


Variables being send to the back end:
Which (must be 3) attack options were chosen, or which 1 special option was chosen


Variables to send to the front:

Default defensive units





Spying
There is a spyinfo table set up. Whenever a nation spies on an enemy nation, an entry with all the true false values of whether a certain res/unit is revealed. 

The /intelligence.html page will have a table showing all the known information for every spying done in the last week. 

Every day at midnight the spy tables more than 1 week old will be deleted from the table. 

When the user goes to an enemy nation and clicks “SPY” they can choose how many spies to use, and much money the spies are given to work with. Then a roll is done for each resource and enemy unit information that can be revealed. The roll is:
rand * your_spies * preparation VS rand * enemy_spies * alertness

If the left side rolls higher than the right side, you successfully reveal the resource/unit in question for 1 week. 
If the right side rolls higher, you fail, and that resource/unit amount remains unknown to you.
If the right side rolls over 2x higher than you, you fail, AND the enemy nation receives a notification: “Your nation found 1 enemy spy(s). You did not manage to capture them and they escaped.” 
If the right side rolls over 10x higher than you, you fail AND 1 of your spies die AND the enemy nation receives a notification: “Your nation captured and executed 1 enemy spy(s).”

Rand is a random number between 0 and 1.
Your spies is your spies.
Preparation is the amount of money given to each of your spies. Up to 5 levels. 100% per level (so is an integer between 1-5).
Alertness is set by the enemy nation’s DEFCON status.

DEFCON LEVEL and (cost PER spy)
Alertness in equation
1 ($100,000 per day)
16x power
2 ($10,000 per day)
8x power
3 ($1,000 per day)
4x power
4 ($100 per day)
2x power
5 (free)
1x power

Preparation level

Preparation mission cost
Preparation in equation
Whole new identity ($300,000 per mission)
16x power
Virtual reality walkthroughs ($30,000 per mission)
8x power
Cool spy gadgets ($3,000 per mission)
4x power
Learn enemy language and culture ($300 per mission)
2x power
Ask nicely for government secrets ($30 per mission)
1x power

You can hire 2 spies per day (costs $30,000 each), unless you have the spy headquarters project, then it’s 3.
Where does this show up in the game? You can set DEFCON level in /intelligence. You can see offensive spy mission results (for 1 week) in /intelligence. You can also see revealed units in the wartarget page (redundant but helpful).

