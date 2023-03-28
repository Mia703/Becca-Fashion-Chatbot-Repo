import csv

filename = 'test.csv'

with open(filename, 'r') as data:
	for line in csv.DictReader(data):
		print(line)


	print(data)