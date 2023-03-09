import re
import json

# read regiment.html
with open("regiment.html", "r") as f:
    html = f.read()

# send data in html webpage received
match = re.search(r"\"F3_COMPONENT_DATA\":\s*({(?:.*)})", html)
if match is None:
    raise Exception("no match")
data = json.loads(match.group(1))

regimentContent = data["regimentContent"]

documents = regimentContent["document"]

companies = documents["companies"]
battles = documents["battles"]

# muster in
startDate = documents["startDate"] 

# muster out
endDate = documents["endDate"]
endPlace = documents["endPlace"]

# get commander list
history = documents["history"]
matches = re.findall(r"<li><a href=\"https://www\.fold3\.com/memorial/.+?/.*?\">(.+?)</a> \((.*?)\)</li>", history)
for match in matches:
    print(match)

# save to json file
with open("regiment.json", "w") as f:
    json.dump(documents, f, indent=4)