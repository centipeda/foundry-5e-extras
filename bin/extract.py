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
from download import INDEX_OUTPUT_DIR, INDEX_FILENAME, SPELL_INDEX_FILENAME, SPELL_DL_OUTPUT_DIR

FOUNDRY_ID_CHARS = string.ascii_letters + string.digits
DB_DIR = "data"
DB_FILE = "db.json"
LEVEL_REGEX = r"(1st|2nd|3rd|([456789]|1[0-9]|20)th) level"
MATERIAL_REGEX = r"M \((.*)\)"
RANGE_REGEX = r"Self \(([0-9]+)-(foot|mile)[ -](.+)\)"
RANGE_SHAPE_REGEX = r"([0-9]+)-(foot|mile)[ -](.+)"
SPELL_LISTS_REGEX = r"Spell [Ll]ists. (.*)"

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

def extract_spell(db, spell, page: BeautifulSoup):
    data = {
        "id": generate_new_foundry_id()
    }

    content = page.find("div", {"id": "page-content"})
    ps = content.find_all(["p", "table"])

    data["name"] = page.find("title").text.split(" - ").pop(0)
    data["source"] = ps.pop(0).text.split(": ").pop()
    meta = ps.pop(0)
    if "cantrip" in meta.text:
        school = meta.text.split().pop(0).lower()
        data["school"] = school
        data["level"] = 0
        data["ritual"] = False
    else:
        info = meta.text.split()
        data["level"] = int(info[0][0])
        data["school"] = info[1].lower()
        if len(info) == 3:
            data["ritual"] = True
        else:
            data["ritual"] = False
    act,dist,comp,dur = [ 
        m.split("</strong> ").pop()
        for m in ps.pop(0).decode_contents().split("<br/>") 
    ]
    comps = comp.split(", ", 2)
    for c in comps:
        material = re.match(MATERIAL_REGEX, c)
        if material:
            has_material = True
            ingr_material = material.group(1)
            break
    else:
        has_material = False
        ingr_material = ""
    data["components"] = {
        "verbal": ("V" in comps),
        "somatic": ("S" in comps),
        "material": has_material,
        "material_type": ingr_material,
    }

    value,unit = act.split(" ", 1)
    if "which you take when" in unit:
        unit,condition = unit.split(", which you take when ")
    elif "taken when" in unit:
        unit,condition = unit.split(", taken when ")
    else:
        condition = ""
    if " or " in unit:
        unit = unit.split(" or ").pop(0)
    data["cast_time"] = {
        "value": int(value),
        "unit": unit.lower().removesuffix("s"),
        "condition": condition.lower()
    }

    if dist.startswith("Self"):
        dist_match = re.match(RANGE_REGEX, dist)
        if dist == "Self":
            data["range"] = {
                "unit": "self",
                "value": 0,
                "shape": "",
            }
        elif dist_match:
            data["range"] = {
                "unit": dist_match.group(2),
                "value": int(dist_match.group(1).replace(",","")),
                "shape": dist_match.group(3),
            }
    elif re.match(RANGE_SHAPE_REGEX, dist):
        m = re.match(RANGE_SHAPE_REGEX, dist)
        data["range"] = {
            "unit": m.group(2),
            "value": int(m.group(1).replace(",","")),
            "shape": m.group(3).lower(),
        }
    elif "Sight" in dist:
        data["range"] = {
            "unit": "sight",
            "value": 0,
            "shape": "",
        }
    elif "Touch" in dist:
        data["range"] = {
            "unit": "touch",
            "value": 0,
            "shape": "",
        }
    elif dist.endswith("feet"):
        value,_ = dist.split(" ", 1)
        data["range"] = {
            "unit": "feet",
            "value": int(value.replace(",","")),
            "shape": "",
        }
    elif dist.endswith("mile"):
        value,_ = dist.split(" ", 1)
        data["range"] = {
            "unit": "mile",
            "value": int(value.replace(",","")),
            "shape": "",
        }
    elif dist.endswith("ft"):
        data["range"] = {
            "unit": "feet",
            "value": int(dist[:-2].replace(",",""))
        }
    else:
        data["range"] = {
            "unit": dist.lower(),
            "value": 0,
        }

    if "Instantaneous" in dur:
        data["duration"] = {
            "concentration": False,
            "unit": "instantaneous",
            "value": 0,
        }
    elif dur.startswith("Until dispelled"):
        data["duration"] = {
            "concentration": False,
            "unit": "indefinite",
            "value": 0,
        }
    elif dur.startswith("Special"):
        data["duration"] = {
            "concentration": False,
            "unit": "special",
            "value": 0,
        }
    else:
        has_conc = dur.startswith("Concentration")
        value,unit = dur.\
            removeprefix("Concentration, up to ").\
            removeprefix("Concentration, Up to ").\
            removeprefix("Up to ").\
            split(" ", 1)
        data["duration"] = {
            "concentration": has_conc,
            "unit": unit.removesuffix("s"),
            "value": int(value),
        }

    for i,p in enumerate(ps):
        if "spell lists." in p.text.lower():
            data["spell_lists"] = []
            for spell_list in re.match(SPELL_LISTS_REGEX, p.text).group(1).split(", "):
                spell_list = spell_list.lower().removesuffix(" (optional)")
                data["spell_lists"].append(spell_list)
            ps.pop(i)
            break

    data["description"] = "".join(str(p) for p in ps)

    db["spells"][spell] = data

    # print(data)
    return db

def main():
    db = {
        "subclasses": dict((cl, {}) for cl in CLASSES_5E),
        "features": {},
        "spells": {},
    }

    print("retrieving subclass index")
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

    print()

    print("retrieving spell index")
    s_count = 0
    s_index = json.loads(open(os.path.join(INDEX_OUTPUT_DIR, SPELL_INDEX_FILENAME), "r").read())
    for spell in s_index["spells"]:
        with open(s_index["spells"][spell]["file"], "r") as p:
            print(f"extracting {spell}...")
            page_data = BeautifulSoup(p.read(), "html.parser")
        db = extract_spell(db, spell, page_data)
        s_count += 1
    print(f"extracted {s_count} spells")

    print("opening db file")
    with open(os.path.join(DB_DIR, DB_FILE), 'w+') as dbfile:
        dbfile.write(json.dumps(db, indent=4))


if __name__ == "__main__":
    main()
