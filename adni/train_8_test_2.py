import csv
import json
import random

with open('id_label.json', 'r') as f:
	dict_id_label = json.load(f)

cn_set = set()
mci_set = set()
ad_set = set()

for key, value in dict_id_label.items():
	if value == 0:
		cn_set.add(key)
	elif value == 1:
		mci_set.add(key)
	elif value == 2:
		ad_set.add(key)

cn_num = len(cn_set)
mci_num = len(mci_set)
ad_num = len(ad_set)

cn_train_num = int(cn_num * 0.8)
cn_test_num = cn_num - cn_train_num

mci_train_num = int(mci_num * 0.8)
mci_test_num = mci_num - mci_train_num

ad_train_num = int(ad_num * 0.8)
ad_test_num = ad_num - ad_train_num

cn_train = set(random.sample(cn_set, cn_train_num))
cn_test = cn_set - cn_train

mci_train = set(random.sample(mci_set, mci_train_num))
mci_test = mci_set - mci_train

ad_train = set(random.sample(ad_set, ad_train_num))
ad_test = ad_set - ad_train

with open('train.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    for key in cn_train:
        writer.writerow((key, dict_id_label[key]))
    for key in mci_train:
        writer.writerow((key, dict_id_label[key]))
    for key in ad_train:
        writer.writerow((key, dict_id_label[key]))

with open('test.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    for key in cn_test:
        writer.writerow((key, dict_id_label[key]))
    for key in mci_test:
        writer.writerow((key, dict_id_label[key]))
    for key in ad_test:
        writer.writerow((key, dict_id_label[key]))
