# Python program to read
# json file

import json

# Opening JSON file
f1 = open('one.json')
# returns JSON object as a dictionary
data1 = json.load(f1)
print(data1)



# Opening JSON file
f2 = open('two.json')
# returns JSON object as a dictionary
data2 = json.load(f2)
print(f" {}  {data2}")


# Closing file
f1.close()
f2.close()
