"""Generic formats for Foundry 5e items."""

CLASSES_5E = [
    "ranger",
    "sorcerer",
    "druid",
    "fighter",
    "barbarian",
    "monk",
    "warlock",
    "wizard",
    "paladin",
    "rogue",
    "cleric",
    "artificer",
    "bard",
]

EXPORTER_NAME = "extras-importer"

SUBCLASS_BASE = {
    "name": "",
    "type": "subclass",
    "img": "",
    "system": {
        "description": {
            "value": "",
            "chat": "",
            "unidentified": ""
        },
        "source": "",
        "identifier": "",
        "classIdentifier": "",
        "advancement": [],
        "spellcasting": {
            "progression": "none",
            "ability": ""
        }
    },
    "effects": [],
    "folder": None,
    "sort": 0,
    "ownership": {
        "default": 0
    },
    "flags": {},
    "_id": "",
    "_stats": {
        "systemId": "dnd5e",
        "systemVersion": "2.1.0",
        "coreVersion": "10.291",
        "createdTime": 0,
        "modifiedTime": 0,
        "lastModifiedBy": EXPORTER_NAME
    }
}

FEATURE_BASE = {
  "_id": "",
  "name": "",
  "ownership": {
    "default": 0
  },
  "type": "feat",
  "system": {
    "description": {
      "value": "",
      "chat": "",
      "unidentified": ""
    },
    "source": "",
    "activation": {
      "type": "",
      "cost": None,
      "condition": ""
    },
    "duration": {
      "value": "",
      "units": ""
    },
    "cover": None,
    "target": {
      "value": None,
      "width": None,
      "units": "",
      "type": "self"
    },
    "range": {
      "value": 0,
      "long": 0,
      "units": "ft"
    },
    "uses": {
      "value": None,
      "max": "",
      "per": None,
      "recovery": ""
    },
    "consume": {
      "type": "",
      "target": None,
      "amount": None
    },
    "ability": "",
    "actionType": "",
    "attackBonus": "",
    "chatFlavor": "",
    "critical": {
      "threshold": None,
      "damage": ""
    },
    "damage": {
      "parts": [],
      "versatile": ""
    },
    "formula": "",
    "save": {
      "ability": "",
      "dc": None,
      "scaling": "spell"
    },
    "type": {
      "value": "class",
      "subtype": ""
    },
    "requirements": "",
    "recharge": {
      "value": None,
      "charged": False
    }
  },
  "flags": {},
  "img": "",
  "effects": [],
  "folder": None,
  "sort": 0,
  "_stats": {
    "systemId": "dnd5e",
    "systemVersion": "2.1.0",
    "coreVersion": "10.291",
    "createdTime": 0,
    "modifiedTime": 0,
    "lastModifiedBy": EXPORTER_NAME
  }
}

SUBCLASS_FEATURE_BASE = {
    "_id": "",
    "type": "ItemGrant",
    "configuration": {
        "items": [],
        "optional": False,
        "spell": {
            "ability": "",
            "preparation": "",
            "uses": {
                "max": "",
                "per": ""
            }
        }
    },
    "value": {},
    "level": 1,
    "title": ""
}
