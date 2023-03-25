#!/usr/bin/env python3

import sys
import pprint
import sqlite3
import os
import copy
import json
import time

from extract import DB_DIR, DB_FILE
from formats import *

CLASSFEATURES_DIR = "classfeatures-extra"
SUBCLASSES_DIR = "subclasses-extra"
CLASSES_DIR = "classes-extra"
DIRS = [
    CLASSES_DIR,
    SUBCLASSES_DIR,
    CLASSFEATURES_DIR,
]
COMPENDIUM_REF_BASE = f"Compendium.dnd5e.{CLASSFEATURES_DIR}."

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

def export_subclass(export_path, class_name, subclass_name, data):
    subclass = copy.deepcopy(SUBCLASS_BASE)
    subclass["_id"] = data["id"]
    subclass["_stats"]["createdTime"] = time.time()
    subclass["_stats"]["modifiedTime"] = time.time()
    subclass["name"] = f'{class_name.title()}: {subclass_name.replace("-", " ").title()}'
    subclass["system"]["identifier"] = subclass_name
    subclass["system"]["classIdentifier"] = class_name
    subclass["system"]["description"]["value"] = f"<p>{data['description']}</p>"
    subclass["system"]["source"] = data["source"]

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
    os.makedirs(classdir, exist_ok=True)
    os.makedirs(subclassdir, exist_ok=True)
    os.makedirs(featdir, exist_ok=True)
    
    print("opening database...")
    with open(os.path.join(DB_DIR, DB_FILE), "r") as dbfile:
        db = json.loads(dbfile.read())
    
    # export classes

    # export subclasses
    for class_ in CLASSES_5E:
        for name,data in db["subclasses"][class_].items():
            export_subclass(subclassdir, class_, name, data)

    # export features
    for feature_name, feature_data in db["features"].items():
        export_feature(featdir, feature_name, feature_data)

if __name__ == "__main__":
    main()
