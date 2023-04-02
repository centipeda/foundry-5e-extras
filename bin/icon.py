#!/usr/bin/env python3

from collections import defaultdict
import json

icon_data = {
    "subclasses": defaultdict(dict)
}

with open("../data/meta.json", "r") as m:
    data = json.loads(m.read())

subclasses = data["results"]
for subclass in subclasses:
    name = subclass["text"]
    class_name,subclass_txt = name.split(": ")

    class_name = class_name.lower()
    subclass_name = subclass_txt.lower().replace(" ", "-")
    icon_path = subclass["img"]

    icon_data["subclasses"][class_name][subclass_name] = icon_path
    # print(f"{class_name},{subclass_name},{icon_path}")

print(json.dumps(icon_data, indent=4))
