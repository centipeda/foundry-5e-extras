#!/usr/bin/env python3
"""Process downloaded pages into database."""

import os
import random
import string
import json
import re
from typing import Dict, Any

from bs4 import BeautifulSoup

from formats import CLASSES_5E
from download import INDEX_OUTPUT_DIR, INDEX_FILENAME

FOUNDRY_ID_CHARS = string.ascii_letters + string.digits
DB_DIR = "data"
DB_FILE = "db.json"
LEVEL_REGEX = r"(1st|2nd|3rd|([456789]|1[0-9]|20)th) level"

generated = []

def _generate_foundry_id():
    return "".join(random.choice(FOUNDRY_ID_CHARS) for _ in range(16))

def generate_new_foundry_id():
    global generated
    f = _generate_foundry_id()
    while f in generated:
        f = _generate_foundry_id()
    generated.append(f)
    return f

def extract_subclass(db: Dict[str, Any], class_name: str, subclass: str, page: BeautifulSoup):
    print(f"extracting {subclass} {class_name}")

    content = page.find("div", {"id": "page-content"})
    parts = [BeautifulSoup(p, "html.parser") for p in content.decode_contents().split("<h3")]
    description_parts = parts.pop(0).find_all("p")
    description = ""
    source = ""
    for d in description_parts:
        if d.text.startswith("Source: "):
            source = d.text.split("Source: ").pop()
        elif d.text.startswith("Sources: "):
            source = d.text.split("Sources: ").pop()
        else:
            description = " ".join((description, d.text)).strip()
    print(f"source: {source}")
    print(f"desc: {description}")
    db["subclasses"][class_name][subclass] = {
        "id": generate_new_foundry_id(),
        "source": source,
        "description": description,
        "features": [],
    }

    features = []
    for part in parts:
        name = part.find("span").text
        rest = "".join(part.decode_contents().split("</span>")[1:])
        part = str(BeautifulSoup( rest.strip(), "html.parser"))
        level_matched = re.search(LEVEL_REGEX, part)
        if level_matched:
            level_str = level_matched.group(0)
            level = int(level_str[:-8])
        else:
            level_str = "1st level"
            level = 1
        foundry_id = generate_new_foundry_id()
        internal_foundry_id = generate_new_foundry_id()

        fullname = "-".join((
            class_name.lower(), 
            subclass.lower().replace(" ", "-"), 
            name.lower()
                .replace(":", "")
                .replace(" ", "-")
                .replace("'", "-")
        ))
        external_id = generate_new_foundry_id()
        internal_id = generate_new_foundry_id()

        db["features"][fullname] = {
            "name": name,
            "class": class_name.lower(),
            "subclass": subclass,
            "external_id": external_id,
            "level": level,
            "description": part,
            "source": source,
        }
        db["subclasses"][class_name][subclass]["features"].append({
            "title": name,
            "external_id": external_id,
            "internal_id": internal_id,
            "level": level,
        })

        print(f"{name}: {level_str} ({foundry_id})")
        features.append((name, foundry_id, internal_foundry_id, level, part))

    return db
    return description, features, source

def main():
    db = {
        "subclasses": dict((cl, {}) for cl in CLASSES_5E),
        "features": {},
        "spells": {},
    }

    print("retrieving index")
    index = json.loads(open(os.path.join(INDEX_OUTPUT_DIR, INDEX_FILENAME), "r").read())
    subclasses = []
    for class_ in CLASSES_5E:
        for subclass in index["subclasses"][class_]:
            subclasses.append((
                class_,
                subclass,
                index["subclasses"][class_][subclass]["file"]
            ))

    count = 0
    for class_, subclass, filename in subclasses:
        with open(filename, "r") as s:
            page_data = BeautifulSoup(s.read(), "html.parser")
        db = extract_subclass(db, class_, subclass, page_data)
        count += 1

    print(f"extracted {count} subclasses")

    print("opening db file")
    with open(os.path.join(DB_DIR, DB_FILE), 'w+') as dbfile:
        dbfile.write(json.dumps(db, indent=4))


if __name__ == "__main__":
    main()
