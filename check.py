import re
import json

from pprint import pprint

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
# endPlace = documents["endPlace"]

# get commander list
history = documents["history"]
matches = re.findall(r"<li><a href=\"https://www\.fold3\.com/memorial/.+?/.*?\">(.+?)</a> \((.*?)\)</li>", history)
commanders = [{
    "name": match[0],
    "info": match[1]
} for match in matches]

output = {
    "startDate": startDate,
    "endDate": endDate,
    "commanders": commanders,
    "companies": companies,
    "battles": battles
}

# save to json file
with open("output.json", "w") as f:
    json.dump(output, f, indent=4)