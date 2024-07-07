import csv
import json

file = open('class3_3_11_2024.csv', 'r')
table = csv.reader(file)
header = next(table)

class_label_map = {'CN': 0, 'MCI': 1, 'AD': 2}
dict_id_label = {}

for row in table:
    dict_id_label[row[0]] = class_label_map[row[2]]
    
with open('id_label.json', 'w') as json_file:
    json.dump(dict_id_label, json_file)
