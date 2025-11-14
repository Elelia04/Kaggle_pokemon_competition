'''
from tqdm.notebook import tqdm
import numpy as np

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
'''
