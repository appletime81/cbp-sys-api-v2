import json


a = {
    "A": None
}


# convert to json
b = json.dumps(a)

# save to file
with open("test002.json", "w") as f:
    f.write(b)