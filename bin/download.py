#!/usr/bin/env python3
"""Download and index all relevant pages."""

import time
from typing import List
from collections import defaultdict
import json
import sys
import requests
import os
from bs4 import BeautifulSoup

from formats import CLASSES_5E

# include archived Unearthed Arcana
INCLUDE_UA = False
DL_OUTPUT_DIR = "downloads/"
INDEX_OUTPUT_DIR = "data/"
BASE_URL = "https://dnd5e.wikidot.com"

MAIN_FILENAME = "index.html"
INDEX_FILENAME = "index.json"

EXCLUDE_PAGES = [
    "/",
    "/random-site.php",
    "/main:about",
    "/system:join",
    "/help:_home",
    "/help:first-time-user",
    "/help:quick-reference",
    "/help:creating-pages",
    "/help:editing-pages",
    "/help:navigation-bars",
    "/help:using-modules",
    "/help:templates",
    "/help:css-themes",
    "/_admin",
    "/nav:top",
    "/nav:side",
    "/css:_home",
    "/system:recent-changes",
    "/system:list-all-pages",
    "/help:_home",
    "/help:first-time-user",
    "/main:about",
    "/main:contact",
    "/legal:_home",
    "/forum:start",
    "/system:members",
    "/warlock:eldritch-invocations",
    "/cleric:beauty-hb",
    "/artificer:infusions",
]

def collect_urls(download_index=False, dl_dir=DL_OUTPUT_DIR, index_dir=INDEX_OUTPUT_DIR):
    index_filename = os.path.join(DL_OUTPUT_DIR, MAIN_FILENAME)

    if download_index:
        print(download_index)
        print("downloading index")
        r = requests.get(BASE_URL)
        if not r.ok:
            sys.exit()
        with open(index_filename, 'x') as f:
            f.write(r.text)
    
    main_file = open(index_filename)
    soup = BeautifulSoup(main_file, 'html.parser')
    print(soup.title)
    data_paths: List[str] = []
    for anchor in soup.find_all('a'):
        href = anchor.get('href')
        if not href:
            continue
        if href in EXCLUDE_PAGES:
            continue
        if not INCLUDE_UA and href.endswith("ua"):
            continue
        if not href.startswith("/"):
            continue
        if href.count(":") > 1:
            continue
        data_paths.append(href.split("#",1).pop(0))
    
    with open(os.path.join(INDEX_OUTPUT_DIR, INDEX_FILENAME), 'w') as f:
        count = 0
        index = {
            "subclasses": defaultdict(dict)
        }
        for class_ in CLASSES_5E:
            for path in data_paths:
                if path.startswith(f"/{class_}:"):
                    subclass = path.split(":").pop()
                    filename = os.path.join(
                        DL_OUTPUT_DIR, 
                        f"{path.lstrip('/').replace(':', '_').replace('-', '_')}.html",
                    )
                    print(f"indexing {class_} {subclass}")
                    count += 1
                    index["subclasses"][class_][subclass] = {
                        "url": path,
                        "file": filename
                    }
        print(f"indexed {count} subclasses")
        f.write(json.dumps(index, indent=4))

    main_file.close()

    return index

def download_pages(index, delay=2.0):
    for class_ in CLASSES_5E:
        for subclass in index["subclasses"][class_]:
            info = index["subclasses"][class_][subclass]
            url = f"{BASE_URL}{info['url']}"
            print(f"downloading {class_}: {subclass}...", end="")
            r = requests.get(url)
            if not r.ok:
                print(" FAIL")
                continue
            print(" OK")
            with open(info["file"], "w+") as f:
                f.write(r.text)
            time.sleep(delay)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--download":
        index = collect_urls(download_index=True)
        print("downloading...")
        download_pages(index)
    else:
        index = collect_urls(download_index=False)

if __name__ == "__main__":
    main()
