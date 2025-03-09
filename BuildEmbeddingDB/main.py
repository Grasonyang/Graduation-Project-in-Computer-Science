import csv
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_directory, 'data/test.csv')

with open(file_path, 'r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    data = list(reader)
print(data[1][0])