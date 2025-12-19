json_path = "stress_data.json"
dict_path = "C:\Users\simon.saffayeh\Documents\MFA\pretrained_models\dictionary\russian_mfa_stressed.dict"

with open(json_path, "r", encoding="utf-8") as f:
    characters = []
    for line in f:
        for char in line:
            if char not in characters:
                characters.append(char)
    print(characters)

chracter_map = {"a":"a1"}

with open(dict_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

