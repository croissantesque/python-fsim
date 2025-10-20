import random
import math

drought_days_left = 0
turn = 1
day = 1
take_turn = None
current_mission = None
mission_time = 0

resources = {
    "money": 150,
    "available_plots": 5,
    "water": 20,
    "max_plots": 5,
    "wheat": 0, #IMPORTANT: HARVESTED WHEAT
    "corn": 0,
    "carrots": 0,
    "beans": 0,
    "eggs": 0,
    "pork": 0,
    "milk": 0
}

animal_info = {
    "chicken": {
        "feed_req": 2,
        "water_req": 3,
        "product_price": 30,
        "product_name" : "eggs",
        "purchase_price": 400,
        "double_chance": 0.5,

    },

    "pig": {
        "feed_req": 3,
        "water_req": 4,
        "product_price": 65,
        "product_name" : "pork",
        "purchase_price": 1200,
        "double_chance": 0.33,

    },

    "cow": {
        "feed_req": 4,
        "water_req": 5,
        "product_price": 125,
        "product_name" : "milk",
        "purchase_price": 2500,
        "double_chance": 0.25,

    }
}

animals_owned = {
    "chicken" : [],
    "pig": [],
    "cow": []
}
seeds = {
    "wheat": {
        "quantity": 0, 
        "water_req": 1,
        "growth_req": 50,
        "water_bonus": [10, 5],  # index 0 = first water, index 1 = second water
        "passive_per_turn": 1,
        "sell_price": 50,
        "double_chance": 0.17
    },
    "corn": {
        "quantity": 0,
        "water_req": 0,
        "growth_req": 100,
        "water_bonus": [0, 0],
        "passive_per_turn": 0.7,
        "sell_price": 85
    },
    "carrots": {
        "quantity": 0,
        "water_req": 1,
        "growth_req": 35,
        "water_bonus": [10, 6],
        "passive_per_turn": 0.8,
        "sell_price": 40
    },
    "beans": {
        "quantity": 0,
        "water_req": 1,
        "growth_req": 30,
        "water_bonus": [8,5],
        "passive_per_turn": 0.8,
        "sell_price": 14
    }
}

plots = {
    1: {"growing": None, "progress": 0, "watered": 0, "ready": False},
    2: {"growing": None, "progress": 0, "watered": 0, "ready": False},
    3: {"growing": None, "progress": 0, "watered": 0, "ready": False},
    4: {"growing": None, "progress": 0, "watered": 0, "ready": False},
    5: {"growing": None, "progress": 0, "watered": 0, "ready": False},
}

def sync_plots(resources, plots):
    while len(plots) < resources["max_plots"]:
        new_plot_id = len(plots) + 1
        plots[new_plot_id] = {"growing": None, "progress": 0, "watered": 0, "ready": False}
    calc_available_plots(plots, resources)

def calc_available_plots(plots, resources):
    empty = sum(1 for p in plots.values() if p["growing"] is None)
    resources["available_plots"] = empty

def grow_plant(plantType, plots, resources, seeds):
    if seeds[plantType]["quantity"] > 0 and resources["available_plots"] > 0:
        resources["available_plots"] -= 1
        seeds[plantType]["quantity"] -= 1
        for plot_number, plot_data in plots.items():
            if plot_data["growing"] is None:
                empty_plot = plot_number
                break
        plots[empty_plot]["growing"] = plantType
        print(f"You plant some {plantType} in plot {empty_plot}.")
        return True
    else: 
        if seeds[plantType]["quantity"] < 1: print(f"\nYou have no more {plantType} seeds! Enter the shop to buy more.\n"); return False
        else: print("You have no plots available! Enter the shop to buy more plots or wait til harvest is ready."); return False

def wait(turn, animal_info, animals_owned, target):
    print(f"You wait {target} turns.")
    turn_count = 0
    while turn_count < target:
        turn = use_turn(turn, animal_info, animals_owned, plots)
        turn_count += 1

    return turn

def examine_animals(animals_owned, animal_info):
    if sum(len(animal_list) for animal_list in animals_owned.values()) < 1: print("You don't own any animals!"); return
    print("Animals:\n")
    for animal_type, animal_list in animals_owned.items():
        for animal in animal_list:
            print(f"{animal['id']}: fed {animal['fed']}/{animal_info[animal_type]['feed_req']} beans today. Watered {animal['watered']}/{animal_info[animal_type]['water_req']} water today.")
            print(f"Ready for {animal_info[animal_type]['product_name']} to be collected") if animal['production_ready'] == True else print(f"No {animal_info[animal_type]['product_name']} for collection.")
            print(f"This animal is sick! {animal['sick_days_left']} days left.\n") if animal["sick"] == True else print("This animal is healthy.")
def feed_animals(turn, animals_owned, animal_info, resources, plots): 
    """ 
    feed all owned animals or as many as possible, skip over already fed.
    Uses 1 turn per 3 total beans fed (rounded up).
    """

    total_animals = sum(len(animal_list) for animal_list in animals_owned.values())
    if total_animals < 1: 
        print("You don't own any animals!")
        return turn
    
    fed_count = 0 

    for animal_type, animal_list in animals_owned.items():
        feed_req = animal_info[animal_type]["feed_req"]

        for animal in animal_list:
            current_fed = animal.get("fed", 0) 
            
            if current_fed < feed_req:
                
                # Use a while loop to feed the animal until its requirement is met
                while animal.get("fed", 0) < feed_req:
                    
                    if resources["beans"] > 0:
                        # Consume bean, increment fed_count and animal's fed status
                        animal["fed"] = animal.get("fed", 0) + 1
                        fed_count += 1
                        resources["beans"] -= 1
                        
                        print(f"Fed {animal['id']} (1 bean). Fed count: {animal['fed']}/{feed_req}.")
                        
                    else: # Ran out of beans
                        print(f"Ran out of beans! Could not fully feed {animal_type} {animal['id']}.")
                        break 
                
        # If resources ran out, no need to check the rest of the animals
        if resources["beans"] < 1:
            break
            
    # 3. Consume turns based on total actions
    if fed_count > 0:
        turns_used = math.ceil(fed_count / 2)
        print(f"Feeding finished. Fed a total of {fed_count} beans, used {turns_used} turns.")
        
        new_turn = turn 
        for _ in range(turns_used): 
            new_turn = use_turn(new_turn, animal_info, animals_owned, plots) 
        
        return new_turn # Return the final, updated turn number
        
    else: 
        print(f"All animals are fed or you had no beans.")
        return turn
    
def collect_produce(resources, animals_owned, animal_info):
    if sum(len(animal_list) for animal_list in animals_owned.values()) < 1: print("You don't own any animals!"); return 0
    collected = 0
    for animal_type, animal_list in animals_owned.items():
        for animal in animal_list:
            product = animal_info[animal_type]["product_name"]
            if animal["production_ready"] == True:
                if random.random() < animal_info[animal_type]["double_chance"]:
                    print(f"!!! Collected double {animal_info[animal_type]["product_name"]} from {animal['id']}!")
                    resources[product] += 2
                    collected += 1
                else: print(f"Collected 1 {product} from {animal['id']}"); resources[product] += 1; collected += 1
                animal["production_ready"] = False
            
            else: print(f"{animal['id']} is sick and did not produce any {product}") if animal["sick"] == True else print(f"{animal['id']}'s {animal_info[animal_type]['product_name']} have already been collected today.")
    if collected > 0:
        print("Finished collecting!")
        return math.ceil(collected/2)
    else: print("There was nothing to collect."); return 0


def water_animals(turn, animals_owned, animal_info, resources, plots): 
    """ 
    water all owned animals or as many as possible, skip over already fed.
    Uses 1 turn per 2 total water used (rounded up).
    """

    total_animals = sum(len(animal_list) for animal_list in animals_owned.values())
    if total_animals < 1: 
        print("You don't own any animals!")
        return turn
    
    watered_count = 0 

    for animal_type, animal_list in animals_owned.items():
        water_req = animal_info[animal_type]["water_req"]

        for animal in animal_list:
            current_watered = animal.get("watered", 0) 
            
            if current_watered < water_req:
                
                # Use a while loop to hydrate the animal until its requirement is met
                while animal.get("watered", 0) < water_req:
                    
                    if resources["water"] > 0:
                        # Consume water, increment count and animal's  status
                        animal["watered"] = animal.get("watered", 0) + 1
                        watered_count += 1
                        resources["water"] -= 1
                        
                        print(f"Watered {animal['id']} (1 water). Watered count: {animal['watered']}/{water_req}.")
                        
                    else: # Ran out of water
                        print(f"Ran out of water! Could not fully water {animal['id']}.")
                        break 
                
        # If resources ran out, no need to check the rest of the animals
        if resources["water"] < 1:
            break
            
    # 3. Consume turns based on total actions
    if watered_count > 0:
        turns_used = math.ceil(watered_count / 2)
        print(f"Watering finished. Used a total of {watered_count} water, taking up {turns_used} turns.")
        
        new_turn = turn 
        for _ in range(turns_used): 
            new_turn = use_turn(new_turn, animal_info, animals_owned, plots) 
        
        return new_turn # Return the final, updated turn number
        
    else: 
        print(f"All animals are watered or you had no water.")
        return turn
    
    



def use_turn(turn, animal_info, animals_owned, plots):
    global day
    turn += 1
    print(f"Turn {turn}")
    check_grown(plots, seeds)
    passive_grow(plots, seeds)

    if turn >= 21:
        turn = 1
        day += 1
        print(f"\n--- A new day begins... \n- Day {day}")
        day_reset(plots, resources, animals_owned, animal_info) 
        sync_plots(resources, plots) #safeguard
    return turn

def generate_mission(resources, plots, seeds):
    global current_mission
    global mission_time

    if current_mission == None:
        mission_chance = random.random()
        if mission_chance < 0.2:
            mission_crop = random.choice(["beans", "wheat", "corn", "carrots"])
            mission_quantity = random.randint(2, int(len(plots)))
            mission_reward = int(mission_quantity * seeds[mission_crop]["sell_price"] * random.uniform(1.4, 1.85))
            mission_time = random.randint(2,4)
            mission_type = "money"

            current_mission = {"crop": mission_crop, "quantity": mission_quantity, "reward": mission_reward, 'type': mission_type}
            print(f"\n--- Mission received! ---")        
        elif mission_chance < 0.35:
            mission_crop = random.choice(["wheat", "carrots"])
            mission_quantity = random.randint(2, 6)
            mission_reward = int(45 * mission_quantity * 1.1 / 1.5)
            mission_time = random.randint(2,4)
            mission_type = "water"

            current_mission = {"crop": mission_crop, "quantity": mission_quantity, "reward": mission_reward, "type": mission_type}
            print(f"\n--- Mission received! ---")
        
        else: current_mission = None
    else:
        mission_time -= 1
        if mission_time == 0:
            print("Your mission has expired.")
            current_mission = None
    if current_mission is not None:
        print(f"You have {mission_time} days left to deliver {current_mission['quantity']} {current_mission['crop']} to the shop for {current_mission['reward']} {current_mission['type']}!")
    
def water_plot(targets, plots, resources, seeds):
    """
    Water one or multiple plots.
    targets can be: a list of plot numbers, or ['all'].
    Returns how many turns were used.
    """
    if isinstance(targets, str):
        targets = [targets]

    # Determine which plots to water
    if len(targets) == 1 and targets[0] == "all":
        plot_indices = list(plots.keys())
    else:
        try:
            plot_indices = [int(x) for x in targets]
        except ValueError:
            print("Invalid plot number(s)!")
            return 0

    watered_count = 0
    watered_raw_count = 0

    for plot_index in plot_indices:
        if plot_index not in plots:
            print(f"Invalid plot number: {plot_index}")
            continue

        plot = plots[plot_index]
        if plot["growing"] is None:
            continue

        crop_name = plot["growing"]
        crop_info = seeds[crop_name]

        # Base water requirement (0 for Corn, 1 for others)
        base_water_req = crop_info["water_req"] 

        plots_owned = resources["max_plots"]
        
        # calculate extra factor: increases by 0.1 for every plot over 8.
        surcharge_factor = 1 + max(0, (plots_owned - 8) / 10) 
        
        # final water cost (ceil() rounds up, so 1.1 becomes 2). prevents water cost from becoming redundant over time
        water_cost = math.ceil(base_water_req * surcharge_factor) 
        
        if resources["water"] < water_cost:
            print(f"Not enough water! You need {water_cost} water to water plot {plot_index}.")
            break

        if plot["watered"] >= 2:
            continue

        if plot["progress"] >= crop_info["growth_req"]:
            continue

        watered_num = plot["watered"]
        bonus = crop_info["water_bonus"][watered_num]

        resources["water"] -= water_cost # Uses the calculated cost
        plot["progress"] += bonus
        plot["watered"] += 1
        
        if base_water_req > 0:
            watered_count += 1
        
        watered_raw_count += 1 #this is needed so we can count how much times water has been done compared to water used.
        #otherwise we'd be printing no plots watered even if we watered corn


        print(f"Watered plot {plot_index} ({crop_name}) +{bonus} growth. Water cost: {water_cost}. Remaining water: {resources['water']}")

    if watered_raw_count == 0:
        print("No valid plots were watered.")
        return 0

    # Cost 1 turn per 2 plots (rounded up)
    turns_used = math.ceil(watered_count / 1.5)
    return turns_used


def check_grown(plots, seeds):
    for plot_number, plot in plots.items():
        if plot["growing"] is None: continue
        if plot["ready"] is True: continue
        crop_name = plot["growing"]
        crop_info = seeds[crop_name]
        if plot["progress"] >= crop_info["growth_req"]:
            if crop_name in ["wheat", "corn"]: 
                form = "has"
            else: form = "have"

            print(f"The {crop_name} in plot {plot_number} {form} grown fully and are ready for harvest!")
            plots[plot_number]["ready"] = True


def buy_plot(resources, plots):
    cost = plot_cost(resources)
    print(f"Next plot costs: ${cost}")
    if resources["money"] < cost:
        print("You don't have enough money to buy a plot!")
        return False
    resources["money"] -= cost
    resources["max_plots"] += 1
    plots[resources["max_plots"]] = {"growing": None, "progress": 0, "watered": 0, "ready": False}
    print(f"Bought a new plot! You now have {resources['max_plots']} plots.")
    print(f"Money: {resources['money']}")
    calc_available_plots(plots, resources)
    return True


def harvest_plot(plots, resources, seeds, target_plot):
    previous_available = resources['available_plots']
    if target_plot == "all":
        harvest_count = 0
        for plot_number, plot in plots.items():
            if plot["ready"] == True:
                crop_name = plot["growing"]

                harvest_amount = 1
                if 'double_chance' in seeds[crop_name]:
                    if random.random() < seeds[crop_name]["double_chance"]:
                        harvest_amount = 2
                        print(f"!!! You harvest DOUBLE the {crop_name} from plot {plot_number} !!!")

                resources[crop_name] += harvest_amount
                plot["growing"] = None
                plot["watered"] = 0
                plot["ready"] = False
                plot["progress"] = 0
                print(f"Harvested {crop_name} from plot {plot_number}!")
                harvest_count += 1

        calc_available_plots(plots, resources)
        
        if resources['available_plots'] == previous_available: print("There is nothing to harvest!"); return 0
        else: print("Finished harvesting!"); return math.ceil(harvest_count/2)
                    
                
    if target_plot not in plots: print("You don't own this plot!"); return 0
    if plots[target_plot]["growing"] is None: print("There's nothing here to harvest!"); return 0
    if plots[target_plot]["ready"] is False: print(f"Not ready for harvest yet!"); return 0
    crop_name = plots[target_plot]["growing"]

    harvest_amount = 1

    if 'double_chance' in seeds[crop_name]:
        if random.random() < seeds[crop_name]["double_chance"]:
            harvest_amount = 2
            print(f"!!! You harvest double the {crop_name} from plot {target_plot} !!!")

    
        
    resources[crop_name] += harvest_amount

    plots[target_plot]["growing"] = None
    plots[target_plot]["progress"] = 0
    plots[target_plot]["watered"] = 0
    plots[target_plot]["ready"] = False
    resources["available_plots"] += 1
    print(f"Harvested {crop_name} from plot {target_plot}!")
    print_inventory(resources, seeds)
    return 1

def deliver_mission(resources):
    global current_mission
    if current_mission is not None:
            reward_type = current_mission['type']
            if resources[current_mission["crop"]] >= current_mission["quantity"]:
                resources[reward_type] += current_mission["reward"]
                resources[current_mission["crop"]] -= current_mission["quantity"]
                print(f"Mission Complete! You delivered {current_mission['quantity']} {current_mission['crop']} and earned {current_mission['reward']} {reward_type}!")
                current_mission = None
                return True
            else: print(f"You don't have the requirements: Deliver {current_mission['quantity']} {current_mission['crop']} for {current_mission['reward']} {reward_type}!"); return False
    else: print("You don't currently have a mission!"); return False


def plot_cost(resources):
    """
    Calculates the cost of buying the next plot.
    First x plots are cheap, then cost increases exponentially,
    but is reduced by the number of high-tier animals owned.
    """
    global animals_owned
    base_cost = 90  # cost for the 6th plot
    cheap_limit = 8  # first x plots are cheap
    extra_plots = max(0, resources["max_plots"] - cheap_limit)
    
    # CORRECTED: Sums the number of pig and cow objects owned
    animals_eligible = len(animals_owned["pig"]) + len(animals_owned["cow"]) 
    
    reduction = 1 + (0.1 * animals_eligible)
    cost = base_cost * (1.5 ** extra_plots) / reduction
    return int(cost)  # round down to nearest dollar


def shop(resources, seeds, plots, animal_info, animals_owned):
    global current_mission
    while True:
        print("\n--- Farm Shop ---")
        print("[1] Buy Seeds")
        print("[2] Sell Produce")
        print("[3] Buy Water")
        print("[4] Buy Plots")
        print("[5] Buy Animals")
        print("[0] Exit Shop")

        
        choice = input("Select an option:")

        if choice == "1":
            print("Seeds Available:")
            print(" [1]  $10 --- Beans")
            print(" [2]  $20 --- Carrots")
            print(" [3]  $30 --- Wheat")
            print(" [4]  $50 --- Corn")

            choice = input("Select a type and quantity: ")
            words = choice.split()
            if len(words) < 2:
                print("Invalid input. (format: <seed number> <quantity>)")
                continue
            if words[0] not in ["1", "2", "3", "4"]:
                print("That's not an available seed number!")
                continue

            try:
                quantity = int(words[1])
            except ValueError:
                print("That's not a valid quantity!")
                continue

            if quantity < 1:
                print("You must purchase at least one seed.")
                continue

            seed_map = {"1": "beans", "2": "carrots", "3": "wheat", "4": "corn"}
            price_map = {"1": 10, "2": 20, "3": 30, "4": 50}

            seed_name = seed_map[words[0]]
            price = price_map[words[0]]
            total_cost = price * quantity

            if resources["money"] < total_cost:
                print("You don't have enough money for that many seeds!")
                continue

            resources["money"] -= total_cost
            seeds[seed_name]["quantity"] += quantity
            print(f"Bought {quantity} {seed_name} seeds for ${total_cost}.")
            continue


        if choice == "2":

            print("Sell Produce:")
            print(" [1]  $14  --- Beans")
            print(" [2]  $35  --- Carrots")
            print(" [3]  $50  --- Wheat")
            print(" [4]  $85  --- Corn")
            print(" [5]  $25  --- Eggs")
            print(" [6]  $65  --- Pork")
            print(" [7]  $125 --- Milk")
            crop_map = {"1": "beans", "2": "carrots", "3": "wheat", "4": "corn", "5": "eggs", "6": "pork", "7": "milk"}
            price_map = {"1": 14, "2": 40, "3": 50, "4": 85, "5": 25, "6": 65, "7": 100}

            
            select = input("Select an option: " )

            if select not in crop_map:
                print("Invalid selection.")
                continue
            elif select in ["1", "2", "3", "4", "5", "6", "7"]: 
                crop_name = crop_map[select]

                if resources[crop_name] == 0: print(f"You don't have any {crop_name} to sell!"); continue

                else:
                    crop_price = price_map[select]
                    qut_input = input(f"You currently have {resources[crop_name]} {crop_name}. Select a quantity to sell:  ")
                    try: quantity = int(qut_input)
                    except ValueError: print("Invalid input."); continue
                    if quantity > resources[crop_name]: print("You don't have that many!"); continue
                    else:
                        
                        resources[crop_name] -= quantity
                        resources["money"] += crop_price * quantity
                        print(f"Sold {quantity} {crop_name}!")
                        continue


            

            
        if choice == "3":
            print("Water Packages:\n")
            print(" [1] Small Refill (10 Water) --- $15")
            print(" [2] Medium Refill (50 Water) --- $70")
            print(" [3] Large Refill (100 Water) --- $130")
            
            pick = input("Select a package: ")
            water_packages = {
                "1": (10, 15),
                "2": (50, 70),
                "3": (100, 130)
            }

            if pick in water_packages:
                water_amount, price = water_packages[pick]
                if resources["money"] < price:
                    print(f"You don't have enough money to buy this package!")
                else:
                    resources["water"] += water_amount
                    resources["money"] -= price
                    print(f"Bought package! Water Balance: {resources['water']}")
                    continue

            else: print("Invalid selection"); continue

        if choice == "4":
            cost = plot_cost(resources)  # calculate the price for the next plot
            print(f"Next plot costs: ${cost}")
            confirm = input("Do you want to buy this plot? (y/n): ").lower()
            if confirm == "y":
                if buy_plot(resources, plots):
                    print("Plot purchased successfully!")
                    continue
                else:
                    print("Purchase failed.")
                    continue
            else:
                print("Plot purchase canceled.")
                continue


        if choice == "5":
            purchase_map = {"1": "chicken", "2": "pig", "3": "cow"}
            price_map = {f"1": animal_info["chicken"]["purchase_price"], "2": animal_info["pig"]["purchase_price"], "3": animal_info["cow"]["purchase_price"]}
            print("Animals:")
            print(f" [1]  ${price_map['1']} --- Chicken")
            print(f" [2]  ${price_map['2']} --- Pig")
            print(f" [3]  ${price_map['3']} --- Cow")

            select = input("Select an animal: ")
            if select not in purchase_map:
                print("Invalid input!"); continue

                    # 1. Map the selection to the animal and price
            picked = select # Assuming select is the user's animal choice ("1", "2", or "3")
            animal_name = purchase_map[picked]
            animal_price = price_map[picked]

            # 2. Check Prerequisites (Material Cost)
            material_reqs = {} # Dictionary to store required materials for the transaction

            if animal_name == "chicken":
                material_name = "beans"
                material_req = 10
                if resources[material_name] < material_req:
                    print(f"To buy a Chicken, you need {material_req} {material_name} in your inventory.")
                    continue # Stop the purchase
                material_reqs[material_name] = material_req

            elif animal_name == "pig":
                material_name = "carrots"
                material_req = 25
                if resources[material_name] < material_req:
                    print(f"To buy a Pig, you need {material_req} {material_name} in your inventory.")
                    continue
                material_reqs[material_name] = material_req

            elif animal_name == "cow":
                material_name = "wheat"
                material_req = 40
                if resources[material_name] < material_req:
                    print(f"To buy a Cow, you need {material_req} {material_name} in your inventory.")
                    continue
                material_reqs[material_name] = material_req

            # 3. Check Money Cost
            if resources["money"] < animal_price:
                print(f"You don't have enough money to buy a {animal_name}! You need ${animal_price}.")
                continue

            # 4. Process the Purchase (Subtract Resources)
            resources["money"] -= animal_price
            print(f"Spent ${animal_price} on a {animal_name}.")

            # Subtract materials
            for name, quantity in material_reqs.items():
                resources[name] -= quantity
                print(f"Spent {quantity} {name.capitalize()}.")
                print(f"You bought a {animal_name}!")
            info = {
                "id": f"{animal_name}_{len(animals_owned[animal_name]) + 1}",
                "fed": 0,
                "watered": 0,
                "sick": False,
                "sick_days_left": 0,
                "production_ready": True

            }
            animals_owned[animal_name].append(info)

        if choice == "0":
            print("Leaving Shop. . . \n")
            break

        else: print("Invalid input."); continue

def print_seed_info():
    print("Seed Info:")
    print(" - Beans   : Quickest growth, extremely low profit. Essential for the expansion of your farm via animals..")
    print(" - Carrots : Fast growth, decent profit. A great place to start your farm!")
    print(" - Wheat   : Fast growth, slightly less profit. Brings with it a chance of double harvest.")
    print(" - Corn    : Slowest growth, better profit. Requires no water!")

def print_commands():
    print("Commands:")
    print(" - grow <plant>              : Plant a seed in an empty plot.")
    print(" - water <plot_number/s/all> : Water a specific plot (max 2/day).")
    print(" - harvest <plot/all>        : Harvest crops from a plot or all ready plots.")
    print(" - inventory                 : Show your seeds, harvested crops, water, plots and money.")
    print(" - shop                      : Buy seeds, water, or new plots.")
    print(" - plots                     : Show each plot, what's growing, progress and how many times it's been watered today.")
    print(" - feed                      : Feed all animals, or as many as possible.")
    print(" - collect                   : Collect your animals' produce.")
    print(" - wanimals                  : Water all your animals, or as many as possible.")
    print(" - wait <turns               : Wait x turns.")
    print(" - info                      : Display information on seeds and plants.")
    print(" - commands                  : List all commands, in case you need help!.")
    

def show_instructions():
    print("="*40)
    print("       WELCOME TO FSIM")
    print("="*40)
    print("\nObjective:")
    print(" - Plant seeds, water crops, and harvest to earn money.")
    print(" - Expand your farm with more plots and water as you grow.")
    print(" - Manage your resources wisely!\n")
    
    print_commands()
    
    print("Tips:")
    print(" - Watering is essential for plant growth - you can water up to twice a day, no more.")
    print(" - Spare beans are important......")
    print(" - Expand plots when you have money - but have a buffer! Tax increases with a bigger farm.")
    print(" - Don't ever forget to feed and water your animals!")
    print(" - Day resets every 20 turns: watered count resets.\n")
    print("="*40)
    print("Good luck, farmer!\n")

def examine_plots(plots, seeds):
    for plot_number, plot in plots.items():
        crop_name = plot["growing"]
        if crop_name is None:
            print(f"Plot {plot_number} is empty.")
        
        else:
            crop_info = seeds[crop_name]
            if plot['progress'] >= crop_info["growth_req"]:
                print(f"The {crop_name} in plot {plot_number} are ready for harvest!")
            else: print(f"Plot {plot_number}: currently growing {crop_name} // {int(plot['progress'])}/{crop_info['growth_req']} maturity // watered {plot['watered']} times today")

def random_event(plots, resources, seeds):
    event_chance = random.random()

    if event_chance < 0.05:
        # Drought
        global drought_days_left
        drought_days_left = random.randint(3,5)
        lost_water = random.randint(5,15)
        resources['water'] = max(0, resources['water'] - lost_water)
        print(f"\n--- Unlucky! A drought hits. You lose {lost_water} water. Drought days left: {drought_days_left} ---")

    elif event_chance < 0.13:
        # Rain
        print("\n--- Lucky! It rained overnight. All plots are watered once, and you gain rainwater! ---")
        for plot in plots.values():
            if plot['growing'] is not None:
                crop_name = plot['growing']
                crop_info = seeds[crop_name]
                plot["watered"] += 1
        resources["water"] += random.randint(10,40)

    elif event_chance < 0.22:
        # Pest attack
        affected_plot = random.choice(list(plots.keys()))
        if plots[affected_plot]['growing'] is not None and plots[affected_plot]['progress'] > 0:
            lost_progress = min(plots[affected_plot]['progress'], random.randint(10,50))
            plots[affected_plot]['progress'] = max(0, plots[affected_plot]['progress'] - lost_progress)
            plots[affected_plot]["ready"] = False
            print(f"\n--- Unlucky! Pests hit plot {affected_plot} and destroy {int(lost_progress)} growth points! ---")

    elif event_chance < 0.30:
        # Bonus seeds
        bonus_seed = random.choice(list(seeds.keys()))
        quantity = random.randint(2,4)
        free_money = random.randint(20,50)
        resources['money'] += free_money
        seeds[bonus_seed]['quantity'] += quantity
        print(f"\n--- Lucky! You find a bonus: {quantity} {bonus_seed} seeds and ${free_money}! ---")

    elif event_chance < 0.40:
        loss_resource = random.choice(["wheat", "corn", "carrots", "beans", "eggs"])
        if resources[loss_resource] > 0:
            percent_loss = random.uniform(0.2, 0.4)
            amount_loss = math.ceil(resources[loss_resource] * percent_loss)
            resources[loss_resource] = max(0, resources[loss_resource] - amount_loss)
            print(f" --- Unlucky! Strong winds damage your storage! You lost {amount_loss} {loss_resource}!")
        else:
            money_loss = random.randint(20,40)
            resources["money"] = max(0, resources["money"] - money_loss)
            print(f" --- Unlucky! A sudden repair fee costs you ${money_loss}!")
    elif event_chance < 0.47:
        # Loss scales with the size of the farm (max_plots) to keep it relevant
        money_loss = random.randint(20, 50) + (resources["max_plots"] * 5)
        money_loss = min(resources['money'], money_loss) # Don't lose more money than you have

        resources['money'] -= money_loss
        print(f"\n--- Unlucky! Thieves and bandits stole ${money_loss} in the night!")
    else:
        # No event
        pass


def print_inventory(resources, seeds):
    print("\n\nInventory: ")
    print(f"  Money: {resources['money']}")
    print(f"  Water: {resources['water']}")
    print(f"  Plots owned: {resources['max_plots']}")
    print(f"  Available plots: {resources['available_plots']}")
    print(f"  Seeds: \n    {seeds['wheat']['quantity']} wheat\n    {seeds['beans']['quantity']} beans\n    {seeds['corn']['quantity']} corn\n    {seeds['carrots']['quantity']} carrots\n")
    print(f"  Harvested Crops: \n    {resources['wheat']} wheat\n    {resources['beans']} beans\n    {resources['corn']} corn \n    {resources['carrots']} carrots")
    print(f"  Animal Products: \n    {resources['eggs']} eggs\n    {resources['pork']} pork\n    {resources['milk']} milk")

def passive_grow(plots, seeds):
    """
    Passive growth scales with how many times the plot has been watered *today*.
    - watered == 0 : passive growth heavily penalised
    - watered == 1 : normal passive
    - watered == 2 : increase, but not so much that it's worth if not urgent
    """
    # multipliers can be tuned 
    multipliers = {0: 0.5, 1: 1.0, 2: 1.3}
    global drought_days_left
    drought_penalty = 0.65 if drought_days_left > 0 else 1.0
    for plot in plots.values():
        if plot["growing"] is not None:
            crop_name = plot["growing"]
            crop_info = seeds[crop_name]
            if plot["progress"] < crop_info["growth_req"]:
                base_passive = crop_info.get("passive_per_turn", 0)
                watered_times = plot.get("watered", 0)
                # cap watered times to 2 in case of unexpected values
                watered_times = 2 if watered_times > 2 else watered_times
                multiplier = multipliers.get(watered_times)
                if crop_name == "corn": plot["progress"] += base_passive * drought_penalty * 1 #corn doesnt need watering so doesnt slow without watering
                else: plot["progress"] += base_passive * multiplier * drought_penalty
                
            elif plot["progress"] > crop_info["growth_req"]:
                plot["ready"] = True


def day_reset(plots, resources, animals_owned, animal_info):
    global drought_days_left
    global day
    for plot in plots.values():
        plot["watered"] = 0
    if drought_days_left > 0:
        drought_days_left -= 1
        print(f" --- Days of drought left: {drought_days_left} ---")
        lost_water = random.randint(3,10)
        resources["water"] = max(0, resources["water"] - lost_water)
        print(f"{lost_water} water dried up today.")

    base_tax = 5
    day_tax = min(40, int(0.5 * day)) # increases by 50 cents a day so player eventually gets capped and forced to upgrade (i hope)
    plot_count = resources["max_plots"]
    

    plot_tax_multiplier = 1.15
    
    # Tax per plot increases after 5 plots (the base )
    plot_tax = int(plot_count * (plot_tax_multiplier ** max(0, plot_count - 5)))

    tax = int(base_tax + day_tax + plot_tax)
    resources["money"] -= tax
    print(f"\n --- Daily upkeep of ${tax} has been deducted from your balance. --- ")


    for animal_type, animal_list in animals_owned.items():
        for animal in animal_list:
            if animal["sick"] == True:
                animal["sick_days_left"] -= 1
                if animal["sick_days_left"] == 0:
                    animal["sick"] = False
                    print(f"Your {animal_type} has recovered from its sickness and will now continue to produce {animal_info[animal_type]["product_name"]}")
            animal["production_ready"] = True
            if animal["fed"] < animal_info[animal_type]["feed_req"]:
                animal["sick"] = True
                animal["sick_days_left"] += random.randint(1, 3)
                print(f"You didn't feed your {animal_type} yesterday! It's sick and will not produce {animal_info[animal_type]["product_name"]} for another {animal["sick_days_left"]} days.")

            if animal["watered"] < animal_info[animal_type]["water_req"]:
                animal["sick"] = True
                animal["sick_days_left"] += random.randint(1, 3)
                print(f"You didn't water your {animal_type} yesterday! It's sick and will not produce {animal_info[animal_type]["product_name"]} for another {animal["sick_days_left"]} days.")
            
            animal["fed"] = 0
            animal["watered"] = 0

            if animal["sick"] == True: print(f"Your {animal_type} is sick for another {animal["sick_days_left"]} days."); animal["production_ready"] = False
            if random.random() < 0.05 and animal["sick"] == False:
                animal["sick"] = True
                animal["sick_days_left"] = random.randint(2,4)
                animal["production_ready"] = False
                print(f" --- Unlucky! Your {animal_type} has grown sick!\n It won't produce {animal_info[animal_type]["product_name"]} for another {animal["sick_days_left"]} days.")


    for animal_type, animal_list in animals_owned.items():    
        survivors = []
        for animal in animal_list:
            if animal["sick"] == True and random.random() < 0.15:
                print(f" --- {animal['id']} has died of sickness...")
                continue
            survivors.append(animal)
        animals_owned[animal_type] = survivors

        for i, animal in enumerate(animals_owned[animal_type], start=1):
            animal["id"] = f"{animal_type}_{i}"


    

    if resources["money"] < 0:
        print("\n !!!! GAME OVER !!!")
        print("You ran out of money to run your farm!")
        print("haha noob git gud")
        exit()
    random_event(plots, resources, seeds)
    generate_mission(resources, plots, seeds)




show_instructions()
print_inventory(resources, seeds)
sync_plots(resources, plots) #safeguard


while True:

    take_turn = False
    r_input = input( "Enter a command: ")
    words = r_input.split()
    if len(words) < 1:
        print("Invalid input.")
        continue
    if len(words) < 2:
        if not words[0] in ["inventory", "deliver", "i", "s", "shop", "plots", "p", "info", "animals", "commands", "wanimals", "feed", "collect"]:
            if words[0] == "grow":
                print("Invalid - you must specify a plant type!")
            elif words[0] == "water":
                print("Invalid - you must specify a plot to water!")
            elif words[0] == "harvest":
                print("Invalid - you must specify a plot to harvest from!")
            if words[0] == "wait":
                print("Invalid - you must specify an amount of turns to wait!")
            else:
                print("Invalid command.")
            continue
    command = words[0]
    if len(words) >= 2: target = words[1]
    if command not in ["g", "w", "i", "h", "deliver", "grow", "water", "animals", "inventory", "collect", "harvest", "s", "shop", "plots", "p", "commands", "info", "wait", "wanimals", "feed"]:
        print("Unknown command!\n")
        continue
    if command in ["grow", "g"]:
        if target not in ["wheat", "corn", "carrots", "beans"]:
            print(f"Unknown plant type: {target}")
            continue
        else: take_turn = grow_plant(target, plots, resources, seeds)
    if command == "animals":
        examine_animals(animals_owned, animal_info)
        take_turn = False
        
    if command == "wait":
        try:
            target = int(target)
        except ValueError:
            print("Invalid - turns waited must be a number.")
            continue
        turn = wait(turn, animal_info, animals_owned, target)

    if command in ["water", "w"]:
        targets = words[1:]
        if not targets:
            print("Usage: w <plot numbers> or w all")
            continue

        turns_used = water_plot(targets, plots, resources, seeds)
        if turns_used > 0:
            for _ in range(turns_used):
                turn = use_turn(turn, animal_info, animals_owned, plots)
    if command == "collect":
        for i in range(collect_produce(resources, animals_owned, animal_info)):
            turn = use_turn(turn, animal_info, animals_owned,plots)
        take_turn = False
    if command == "feed":
        turn = feed_animals(turn, animals_owned, animal_info, resources, plots)
    
    if command == "wanimals":
        turn = water_animals(turn, animals_owned, animal_info, resources, plots)

    if command in ["harvest", "h"]:
        if target == "all":
            for i in range(harvest_plot(plots, resources, seeds, target)):
                turn = use_turn(turn, animal_info, animals_owned, plots)
            take_turn = False
        else: 
            try:
                target_plot = int(target)
                take_turn = harvest_plot(plots, resources, seeds, target_plot)
            except ValueError:
                print("Invalid plot number! Must be a number.")
                continue
    
    

        
    if command in ["shop", "s"]:
        shop(resources,seeds,plots, animal_info, animals_owned)
        take_turn = False

    if command in ["inventory", "i"]:
        print_inventory(resources, seeds)
        take_turn = False
    
    if command in ["plots", "p"]:
        examine_plots(plots, seeds)
        take_turn = False

    if command == "info":
        print_seed_info()
        take_turn = False
    
    if command == "deliver":
        take_turn = deliver_mission(resources)
    
    if command == "commands":
        print_commands()
        take_turn = False

    if take_turn == True:

        turn = use_turn(turn, animal_info, animals_owned, plots)
