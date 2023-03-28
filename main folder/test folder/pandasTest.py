import pandas as pd
from typing import Dict, Any, List

# convert the csv file to a Pandas DataFrame
df = pd.read_csv('test.csv')

# .to_string() = converts to string; prints the entire csv file
# print(df) = prints the first 5 rows and the last 5 rows if the file is too large
print("-------- Print DF ------------")
print(df.to_string())

print("--------- Print Row -----------")
print(df.loc[1].to_string())

print("--------- Print Name -----------")
print(df.loc[1]["Name"])
print('From index blah blah ' + str(df.loc[1]["Name"]))

print("-------- Print Description ------------")
print(df.loc[1]["Description"])

print("--------- Search -----------")
keyword = 'C'
print(df.loc[df["Name"] == keyword])
print("--------------------")
print(df.loc[df["Name"] == keyword]["Description"])
print("--------------------")
print(df.loc[df["Name"] == keyword]["Description"].to_string())