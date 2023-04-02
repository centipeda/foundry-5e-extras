#!/usr/bin/env python3

import sys
import os
import copy
import json
import time

from extract import DB_DIR, DB_FILE
from formats import *

ICON_FILE = "icons.json"
CLASSFEATURES_DIR = "classfeatures-extra"
SUBCLASSES_DIR = "subclasses-extra"
CLASSES_DIR = "classes-extra"
SPELLS_DIR = "spells-extra"
SPELLS_LEVEL_DIR = {
    0: "cantrip",
    1: "level-1",
    2: "level-2",
    3: "level-3",
    4: "level-4",
    5: "level-5",
    6: "level-6",
    7: "level-7",
    8: "level-8",
    9: "level-9",
}
COMPENDIUM_REF_BASE = f"Compendium.dnd5e.{CLASSFEATURES_DIR}."

ARTIFICER_PATH = {
    "data/artificer"
}
ARTIFICER_FILES = {
    "artificer.json": "classes-extra/artificer.json",
}

COST_UNITS = {
    "action": "action",
    "round": "round",
    "bonus action": "bonus",
    "minute": "minute",
    "hour": "hour",
    "reaction": "reaction",
}
DURATION_UNITS = {
    "instantaneous": "inst",
    "round": "round",
    "minute": "minute",
    "hour": "hour",
    "day": "day",
    "indefinite": "",
    "special": "",
}
RANGE_UNITS = {
    "feet": "ft",
    "sight": "",
}
MAGIC_SCHOOL = {
    "conjuration": "con",
    "necromancy": "nec",
    "evocation": "evo",
    "abjuration": "abj",
    "transmutation": "tra",
    "divination": "div",
    "enchantment": "enc",
    "illusion": "ill",
    "graviturgy": "evo",
}

def usage(status=0):
    print(f"usage: {sys.argv[0]} compendium_dir")
    sys.exit(status)

def export_feature(export_path, fullname, data):
    feature = copy.deepcopy(FEATURE_BASE)
    feature["_id"] = data["external_id"]
    feature["name"] = ": ".join((data["subclass"].replace("-", " ").title(), data["name"]))
    feature["_stats"]["createdTime"] = time.time()
    feature["_stats"]["modifiedTime"] = time.time()
    feature["system"]["description"]["value"] = data["description"]
    feature["system"]["source"] = data["source"]

    path = os.path.join(export_path, f"{fullname}.json")
    print(f"Exporting to {path}...")
    with open(path, 'w+') as o:
        o.write(json.dumps(feature, indent=4))

def export_subclass(export_path, class_name, subclass_name, data, icon_data):
    subclass = copy.deepcopy(SUBCLASS_BASE)
    subclass["_id"] = data["id"]
    subclass["_stats"]["createdTime"] = time.time()
    subclass["_stats"]["modifiedTime"] = time.time()
    subclass["name"] = f'{class_name.title()}: {subclass_name.replace("-", " ").title()}'
    subclass["system"]["identifier"] = subclass_name
    subclass["system"]["classIdentifier"] = class_name
    subclass["system"]["description"]["value"] = f"<p>{data['description']}</p>"
    subclass["system"]["source"] = data["source"]
    subclass["img"] = icon_data[class_name][subclass_name]

    for feature_data in data["features"]:
        feature = copy.deepcopy(SUBCLASS_FEATURE_BASE)
        feature["title"] = feature_data["title"]
        feature["_id"] = feature_data["internal_id"]
        feature["configuration"]["items"] = [
            COMPENDIUM_REF_BASE + feature_data["external_id"]
        ]
        feature["level"] = feature_data["level"]
        subclass["system"]["advancement"].append(feature)

    path = os.path.join(export_path, f"{class_name}-{subclass_name}.json")
    print(f"Exporting to {path}...")

    with open(path, 'w+') as o:
        o.write(json.dumps(subclass, indent=4))
    
def export_spell(export_path, name, data):
    print(data)
    spell = copy.deepcopy(SPELL_BASE)
    spell["name"] = data["name"]
    spell["_id"] = data["id"]
    spell["system"]["school"] = MAGIC_SCHOOL[data["school"]]
    spell["system"]["level"] = data["level"]
    spell["system"]["description"]["value"] = data["description"]
    spell["system"]["source"] = data["source"]
    spell["system"]["activation"] = {
        "type": COST_UNITS[data["cast_time"]["unit"]],
        "value": data["cast_time"]["value"],
        "condition": data["cast_time"]["condition"],
    }
    spell["system"]["duration"] = {
        "units": DURATION_UNITS[data["duration"]["unit"]],
        "value": str(data["duration"]["value"]),
    }
    spell["system"]["range"] = {
        "units": data["range"]["unit"],
        "value": data["range"]["value"]
    }
    spell["system"]["components"] = {
        "vocal": data["components"]["verbal"],
        "somatic": data["components"]["somatic"],
        "material": data["components"]["material"],
        "ritual": data["ritual"],
        "concentration": data["duration"]["concentration"],
    }
    spell["_stats"]["createdTime"] = time.time()
    spell["_stats"]["modifiedTime"] = time.time()

    path = os.path.join(
        export_path,
        SPELLS_LEVEL_DIR[data["level"]],
        f"{name}.json"
    )
    print(f"Exporting to {path}...")
    with open(path, 'w+') as s:
        s.write(json.dumps(spell, indent=4))

def main():
    if len(sys.argv) < 2:
        usage(-1)

    compendium_dir = sys.argv[1]
    if not os.path.exists(compendium_dir):
        print("compendium_dir does not exist")
        usage(1)
    print(f"exporting to: {compendium_dir}")
    classdir = os.path.join(compendium_dir, CLASSES_DIR)
    subclassdir = os.path.join(compendium_dir, SUBCLASSES_DIR)
    featdir = os.path.join(compendium_dir, CLASSFEATURES_DIR)
    spelldir = os.path.join(compendium_dir, SPELLS_DIR)
    os.makedirs(classdir, exist_ok=True)
    os.makedirs(subclassdir, exist_ok=True)
    os.makedirs(featdir, exist_ok=True)
    
    print("opening database...")
    with open(os.path.join(DB_DIR, DB_FILE), "r") as dbfile:
        db = json.loads(dbfile.read())
    print("opening icon database...")
    with open(os.path.join(DB_DIR, ICON_FILE), "r") as iconfile:
        icon_data = json.loads(iconfile.read())
    
    # export subclasses
    for class_ in CLASSES_5E:
        for name,data in db["subclasses"][class_].items():
            export_subclass(subclassdir, class_, name, data, icon_data["subclasses"])

    # export features
    for feature_name, feature_data in db["features"].items():
        export_feature(featdir, feature_name, feature_data)
    
    # export spells
    for spell,spell_data in db["spells"].items():
        export_spell(spelldir, spell, spell_data)

    # export artificer

if __name__ == "__main__":
    main()
