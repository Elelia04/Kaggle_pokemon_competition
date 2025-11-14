''''

from tqdm.notebook import tqdm
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from collections import Counter

def create_simple_features(data: list[dict]) -> pd.DataFrame:
    feature_list = []
    for battle in tqdm(data, desc="Extracting features"):
        features = {}
        
        #P1 Team Features 
        p1_team = battle.get('p1_team_details', [])
        if p1_team:
            features['p1_mean_hp'] = np.mean([p.get('base_hp', 0) for p in p1_team])
            features['p1_mean_spe'] = np.mean([p.get('base_spe', 0) for p in p1_team])
            features['p1_mean_atk'] = np.mean([p.get('base_atk', 0) for p in p1_team])
            features['p1_mean_def'] = np.mean([p.get('base_def', 0) for p in p1_team])
            

        #P2 Lead Features
        p2_lead = battle.get('p2_lead_details')
        if p2_lead:
            #P2's lead Pokémon's stats
            features['p2_lead_hp'] = p2_lead.get('base_hp', 0)
            features['p2_lead_spe'] = p2_lead.get('base_spe', 0)
            features['p2_lead_atk'] = p2_lead.get('base_atk', 0)
            features['p2_lead_def'] = p2_lead.get('base_def', 0)

        features['battle_id'] = battle.get('battle_id')
        if 'player_won' in battle:
            features['player_won'] = int(battle['player_won'])


        feature_list.append(features)
        
    return pd.DataFrame(feature_list).fillna(0)

#Types dataframe
official_types = {
   "bug", "dragon", "electric", "fighting", "fire",
    "flying", "ghost", "grass", "ground", "ice", "normal", "poison",
    "psychic", "rock", "water"
}

records = []
all_types = set()

for battle in train_data:
    type_counts = {t: 0 for t in official_types}
    
    for p in battle['p1_team_details']:
        types = set(p['types'])
        filtered_types = types.intersection(official_types)
        all_types.update(filtered_types)
        for t in filtered_types:
            type_counts[t] += 1
    

    records.append(type_counts)


type_df = pd.DataFrame(records)
display(type_df.head())


# Create feature DataFrames for both training and test sets
print("Processing training data...")
train_df = create_simple_features(train_data)

print("\nProcessing test data...")
test_data = []
with open(test_file_path, 'r') as f:
    for line in f:
        test_data.append(json.loads(line))
test_df = create_simple_features(test_data)

print("\nTraining features preview:")
display(train_df.head())

#===================================================================================

#Extracting all non-repeating pokémon names and types appearing in the dataset. 
dataset_types = defaultdict(set)

for battle in train_data:
    #P1 pokémons, 6
    for p in battle.get("p1_team_details", []):
        name = p.get("name", "").lower()
        for t in p.get("types", []):
            if t != "notype" and t:
                dataset_types[name].add(t.lower())

    #P2 lead pokémon
    lead = battle.get("p2_lead_details", {})
    name = lead.get("name", "").lower()
    for t in lead.get("types", []):
        if t != "notype" and t:
            dataset_types[name].add(t.lower())

    #P2 pokémons appeared in the battle_timeline
    for turn in battle.get("battle_timeline", []):
        p2_state = turn.get("p2_pokemon_state", {})
        name = p2_state.get("name", "").lower()
        if name:
            pass #no types rn

types_dict = {name: sorted(list(types)) for name, types in dataset_types.items()}

print("All pokèmon names and relative types:\n")
for name, types in sorted(types_dict.items()):
    print(f"{name}: {types}")

all_types = sorted({t for types in types_dict.values() for t in types})

print(f"\nTot number of found pokémon types: {len(all_types)}")
print("Types:", ", ".join(all_types))

#===================================================================================

#Distribution of pokémon types 
all_types = [t for types in types_dict.values() for t in types]
type_counts = Counter(all_types)

print("Types distribution:")
for t, c in type_counts.most_common():
    print(f"{t}: {c}")

plt.figure(figsize=(10,4))
plt.bar(type_counts.keys(), type_counts.values())
plt.title("Types distribution in the dataset")
plt.xticks(rotation=45)
plt.show()


#===================================================================================

#Distribution of pokémon names (P1 and P2)
from collections import Counter
import matplotlib.pyplot as plt

p1_pokes = []

for battle in train_data:
    for p in battle.get("p1_team_details", []):
        name = p.get("name", "").lower()
        if name:
            p1_pokes.append(name)

p1_counts = Counter(p1_pokes)

print("Order of most common P1 pokémons:")
for name, count in p1_counts.most_common(20):
    print(f"{name}: {count}")


#P2
p2_pokes = []
for battle in train_data:
    seen_in_battle = set()
    
    #lead poke
    lead = battle.get("p2_lead_details", {})
    if lead.get("name"):
        p2_pokes.append(lead["name"].lower())

    for turn in battle.get("battle_timeline", []):
        p2_state = turn.get("p2_pokemon_state", {})
        name = p2_state.get("name", "").lower()
        if name:
            seen_in_battle.add(name)

    p2_pokes.extend(list(seen_in_battle))
            
p2_counts = Counter(p2_pokes)

print("\nOrder of most common P2 pokémons:")
for name, count in p2_counts.most_common(20):
    print(f"{name}: {count}")

def plot_counts(counter, title, top=20):
    items = counter.most_common(top)
    labels, values = zip(*items)

    plt.figure(figsize=(10,4))
    plt.bar(labels, values)
    plt.xticks(rotation=45)
    plt.title(title)
    plt.show()

plot_counts(p1_counts, "Top Pokémon P1")
plot_counts(p2_counts, "Top Pokémon P2")

#===================================================================================

#Checking for all possible statuses in the dataset
statuses = set()

for battle in train_data:
    for turn in battle.get("battle_timeline", []):
        for side in ["p1_pokemon_state", "p2_pokemon_state"]:
            st = (turn.get(side) or {}).get("status")
            if st is not None:
                statuses.add(st.lower())

print("Status found in the dataset:", statuses)

#Calculating the status frequencies 
status_counter = Counter()

for battle in train_data:
    for turn in battle.get("battle_timeline", []):
        for side in ["p1_pokemon_state", "p2_pokemon_state"]:
            st = (turn.get(side) or {}).get("status")
            if st is not None:
                status_counter[st.lower()] += 1

print(status_counter)

'''
