import json

with open('id_label.json', 'r') as f:
	dict_id_label = json.load(f)

print(dict_id_label)
