#!/usr/bin/env python3

import os
import time
import json
import copy

from extract import generate_new_foundry_id
from export import COMPENDIUM_REF_BASE, CLASSFEATURES_DIR, CLASSES_DIR
from formats import SUBCLASS_FEATURE_BASE, FEATURE_BASE, EXPORTER_NAME

ARTIFICER_OUTPUT_DIR = "dnd5e-extras/packs/src"

FEATURE_DATA = {
    "magical-tinkering": {
        "name": "Magical Tinkering",
        "id": "VkRQ7glQvTWWiO01",
        "icon": "icons/commodities/tech/cog-brass.webp",
        "level": 1,
        "description": "<p>At 1st level, you've learned how to invest a spark of magic into mundane objects. To use this ability, you must have thieves' tools or artisan's tools in hand. You then touch a Tiny nonmagical object as an action and give it one of the following magical properties of your choice:</p><ul><li>The object sheds bright light in a 5-foot radius and dim light for an additional 5 feet.</li></ul><ul><li>Whenever tapped by a creature, the object emits a recorded message that can be heard up to 10 feet away. You utter the message when you bestow this property on the object, and the recording can be no more than 6 seconds long.</li></ul><ul><li>The object continuously emits your choice of an odor or a nonverbal sound (wind, waves, chirping, or the like). The chosen phenomenon is perceivable up to 10 feet away.</li></ul><ul><li>A static visual effect appears on one of the object's surfaces. This effect can be a picture, up to 25 words of text, lines and shapes, or a mixture of these elements, as you like.</li></ul><p>The chosen property lasts indefinitely. As an action, you can touch the object and end the property early.</p><p>You can bestow magic on multiple objects, touching one object each time you use this feature, though a single object can only bear one property at a time. The maximum number of objects you can affect with this feature at one time is equal to your Intelligence modifier (minimum of one object). If you try to exceed your maximum, the oldest property immediately ends, and then the new property applies.</p>",
    },
    "infuse-item":{ 
        "name": "Infuse Item",
        "id": "VkRQ7glQvTWWiO02",
        "icon": "icons/magic/symbols/runes-etched-steel-blade.webp",
        "level": 2,
        "description": """
<p>When you gain this feature, pick four @Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO12]{Artificer Infusions}</a> to learn. You learn additional infusions of your choice when you reach certain levels in this class, as shown in the Infusions Known column of the Artificer table.</p>
<p>Whenever you gain a level in this class, you can replace one of the artificer infusions you learned with a new one.</p>
<h5><span>Infusing an Item</span></h5>
<p>Whenever you finish a long rest, you can touch a nonmagical object and imbue it with one of your artificer infusions, turning it into a magic item. An infusion works on only certain kinds of objects, as specified in the infusion's description. If the item requires attunement, you can attune yourself to it the instant you infuse the item. If you decide to attune to the item later, you must do so using the normal process for attunement (see the attunement rules in the <em>Dungeon Master's Guide</em>).</p>
<p>Your infusion remains in an item indefinitely, but when you die, the infusion vanishes after a number of days equal to your Intelligence modifier (minimum of 1 day). The infusion also vanishes if you replace your knowledge of the infusion.</p>
<p>You can infuse more than one nonmagical object at the end of a long rest; the maximum number of objects appears in the Infused Items column of the Artificer table. You must touch each of the objects, and each of your infusions can be in only one object at a time. Moreover, no object can bear more than one of your infusions at a time. If you try to exceed your maximum number of infusions, the oldest infusion ends, and then the new infusion applies.</p>
<p>If an infusion ends on an item that contains other things, like a bag of holding, its contents harmlessly appear in and around its space.</p>""",
    },
    "right-tool": { 
        "name": "The Right Tool for the Job",
        "id": "VkRQ7glQvTWWiO03",
        "icon": "icons/tools/hand/hammer-and-nail.webp",
        "level": 3,
        "description": "<p>At 3rd level, you've learned how to produce exactly the tool you need: with thieves' tools or artisan's tools in hand, you can magically create one set of artisan's tools in an unoccupied space within 5 feet of you. This creation requires 1 hour of uninterrupted work, which can coincide with a short or long rest. Though the product of magic, the tools are nonmagical, and they vanish when you use this feature again.</p>",
    },
    "tool-expertise": { 
        "name": "Tool Expertise",
        "id": "VkRQ7glQvTWWiO04",
        "icon": "icons/tools/smithing/tongs-steel-grey.webp",
        "level": 6,
        "description": "<p>At 6th level, your proficiency bonus is now doubled for any ability check you make that uses your proficiency with a tool.</p>",
    },
    "flash-genius": { 
        "name": "Flash of Genius",
        "id": "VkRQ7glQvTWWiO05",
        "icon": "icons/magic/perception/eye-ringed-green.webp",
        "level": 7,
        "description": "<p>At 7th level, you've gained the ability to come up with solutions under pressure. When you or another creature you can see within 30 feet of you makes an ability check or a saving throw, you can use your reaction to add your Intelligence modifier to the roll.</p>",
    },
    "magic-item-adept": { 
        "name": "Magic Item Adept",
        "id": "VkRQ7glQvTWWiO06",
        "icon": "icons/equipment/head/goggles-leather-blue.webp",
        "level": 10,
        "description": "<p>When you reach 10th level, you achieve a profound understanding of how to use and make magic items:</p> <ul> <li>You can attune to up to four magic items at once.</li> </ul> <ul> <li>If you craft a magic item with a rarity of common or uncommon, it takes you a quarter of the normal time, and it costs you half as much of the usual gold.</li> </ul>",
    },
    "spell-storing-item": { 
        "name": "Spell-Storing Item",
        "id": "VkRQ7glQvTWWiO07",
        "icon": "icons/commodities/treasure/glass-cube-teal.webp",
        "level": 11,
        "description": "<p>At 11th level, you can now store a spell in an object. Whenever you finish a long rest, you can touch one simple or martial weapon or one item that you can use as a spellcasting focus, and you store a spell in it, choosing a 1st- or 2nd-level spell from the artificer spell list that requires 1 action to cast (you needn't have it prepared).</p><p>While holding the object, a creature can take an action to produce the spell's effect from it, using your spellcasting ability modifier. If the spell requires concentration, the creature must concentrate. The spell stays in the object until it's been used a number of times equal to twice your Intelligence modifier (minimum of twice) or until you use this feature again to store a spell in an object.</p>",
    },
    "magic-item-savant": { 
        "name": "Magic Item Savant",
        "id": "VkRQ7glQvTWWiO08",
        "icon": "icons/commodities/treasure/puzzle-box-glowing-blue.webp",
        "level": 14,
        "description": "<p>At 14th level, your skill with magic items deepens more:</p> <ul> <li>You can attune to up to five magic items at once.</li> </ul> <ul> <li>You ignore all class, race, spell and level requirements on attuning to or using a magic item.</li> </ul>",
    },
    "magic-item-master": { 
        "name": "Magic Item Master",
        "id": "VkRQ7glQvTWWiO09",
        "icon": "icons/commodities/tech/tube-chamber-lightning.webp",
        "level": 18,
        "description": "<p>Starting at 18th level, you can attune up to six magic items at once.</p>",
    },
    "soul-of-artifice": { 
        "name": "Soul of Artifice",
        "id": "VkRQ7glQvTWWiO10",
        "icon": "icons/magic/control/silhouette-hold-beam-blue.webp",
        "level": 20,
        "description": "<p>At 20th level, you develop a mystical connection to your magic items, which you can draw on for protection:</p> <ul> <li>You gain a +1 bonus to all saving throws per magic item you are currently attuned to.</li> </ul> <ul> <li>If you're reduced to 0 hit points but not killed out-right, you can use your reaction to end one of your artificer infusions, causing you to drop to 1 hit point instead of 0.</li> </ul>",
    },
    "artificer-spellcasting":  {
        "name": "Spellcasting",
        "id": "VkRQ7glQvTWWiO11",
        "icon": "icons/svg/item-bag.svg",
        "level": 1,
        "description": "",
    },
    "artificer-infusions":  {
        "name": "Artificer Infusions",
        "id": "VkRQ7glQvTWWiO12",
        "icon": "icons/commodities/tech/sensor-brown.webp",
        "level": 1,
        "description": """
<h1>List of Artificer Infusions</h1>
<h3><span>Arcane Propulsion Armor</span></h3>
<p><strong><em>Prerequisite: 14th-level artificer</em></strong><br>
<strong><em>Item: A suit of armor (requires attunement)</em></strong></p>
<p>The wearer of this armor gains these benefits:</p>
<ul>
<li>The wearer's walking speed increases by 5 feet.</li>
</ul>
<ul>
<li>The armor includes gauntlets, each of which is a magic melee weapon that can be wielded only when the hand is holding nothing. The wearer is proficient with the gauntlets, and each one deals 1d8 force damage on a hit and has the thrown property, with a normal range of 20 feet and a long range of 60 feet. When thrown, the gauntlet detaches and flies at the attack's target, then immediately returns to the wearer and reattaches.</li>
</ul>
<ul>
<li>The armor can't be removed against the wearer's will.</li>
</ul>
<ul>
<li>If the wearer is missing any limbs, the armor replaces those limbs - hands, arms, feet, legs, or similar appendages. The replacements function identically to the body parts they replace.</li>
</ul>
<h3><span>Armor of Magical Strength</span></h3>
<p><strong><em>Item: A suit of armor (requires attunement)</em></strong></p>
<p>This armor has 6 charges. The wearer can expend the armor's charges in the following ways:</p>
<ul>
<li>When the wearer makes a Strength check or a Strength saving throw, it can expend 1 charge to add a bonus to the roll equal to its Intelligence modifier.</li>
</ul>
<ul>
<li>If the creature would be knocked prone, it can use its reaction to expend 1 charge to avoid being knocked prone.</li>
</ul>
<p>The armor regains 1d6 expended charges daily at dawn.</p>
<h3><span>Armor of Tools (UA)</span></h3>
<p><strong><em>Item: A suit of armor</em></strong></p>
<p>As an action, a creature wearing this infused armor can integrate into it artisan’s tools or thieves’ tools. The tools remain integrated in the armor for 8 hours or until the wearer removes the tools as an action. The armor can have only one tool integrated at a time. The wearer can add its Intelligence modifier to any ability checks it makes with the integrated tool. The wearer must have a hand free to use the tool.</p>
<h3><span>Boots of the Winding Path</span></h3>
<p><strong><em>Prerequisite: 6th-level artificer</em></strong><br>
<strong><em>Item: A pair of boots (requires attunement)</em></strong></p>
<p>While wearing these boots, a creature can teleport up to 15 feet as a bonus action to an unoccupied space the creature can see. The creature must have occupied that space at some point during the current turn.</p>
<h3><span>Enhanced Arcane Focus</span></h3>
<p><strong><em>Item: A rod, staff or wand (requires attunement)</em></strong></p>
<p>While holding this item, a creature gains +1 bonus to spell attack rolls. In addition, the creature ignores half cover when making a spell attack.</p>
<p>The bonus increases to +2 when you reach 10th level in this class.</p>
<h3><span>Enhanced Defense</span></h3>
<p><strong><em>Item: A suit of armor or a shield</em></strong></p>
<p>A creature gains a +1 bonus to Armor Class while wearing (armor) or wielding (shield) the infused item.</p>
<p>The bonus increases to +2 when you reach 10th level in this class.</p>
<h3><span>Enhanced Weapon</span></h3>
<p><strong><em>Item: A simple or martial weapon</em></strong></p>
<p>This magic weapon grants a +1 bonus to attack and damage rolls made with it.</p>
<p>The bonus increases to +2 when you reach 10th level in this class.</p>
<h3><span>Helm of Awareness</span></h3>
<p><strong><em>Prerequisite: 10th-level artificer</em></strong><br>
<strong><em>Item: A helmet (requires attunement)</em></strong></p>
<p>While wearing this helmet, a creature has advantage on initiative rolls. In addition, the wearer can’t be surprised, provided it isn’t incapacitated.</p>
<h3><span>Homunculus Servant</span></h3>
<p><strong><em>Item: A gem or crystal worth at least 100 gp</em></strong></p>
<p>You learn intricate methods for magically creating a special homunculus that serves you. The item you infuse serves as the creature's heart, around which the creature's body instantly forms.</p>
<p>You determine the homunculus's appearance. Some artificers prefer mechanical-looking birds, whereas some like winged vials or miniature, animate cauldrons.</p>
<p>The homunculus is friendly to you and your companions, and it obeys your commands. See this creature's game statistics in the Homunculus Servant stat block, which uses your proficiency bonus (PB) in several places.</p>
<p>In combat, the homunculus shares your initiative count, but it takes its turn immediately after yours. It can move and use its reaction on its own, but the only action it takes on its turn is the Dodge action, unless you take a bonus action on your turn to command it to take another action. That action can be one in its stat block or some other action. If you are incapacitated, the homunculus can take any action of its choice, not just Dodge.</p>
<p>The homunculus regains 2d6 hit points if the mending spell is cast on it. If you or the homunculus dies, it vanishes, leaving its heart in its space.</p>
<table class="wiki-content-table">
<tbody><tr>
<th colspan="6">Homunculus Servant</th>
</tr>
<tr>
<td colspan="6"><em>Tiny construct</em></td>
</tr>
<tr>
<td colspan="6"><strong>Armor Class:</strong> 13 (natural armor)</td>
</tr>
<tr>
<td colspan="6"><strong>Hit Points:</strong> 1 + your Intelligence modifier + your artificer level (the homunculus has a number of Hit Dice [d4s] equal to your artificer level)</td>
</tr>
<tr>
<td colspan="6"><strong>Speed:</strong> 20 ft., fly 30 ft.</td>
</tr>
<tr>
<th>STR</th>
<th>DEX</th>
<th>CON</th>
<th>INT</th>
<th>WIS</th>
<th>CHA</th>
</tr>
<tr>
<td>4 (-3)</td>
<td>15 (+2)</td>
<td>12 (+1)</td>
<td>10 (+0)</td>
<td>10 (+0)</td>
<td>7 (−2)</td>
</tr>
<tr>
<td colspan="6"><strong>Saving Throws:</strong> Dex +2 plus PB</td>
</tr>
<tr>
<td colspan="6"><strong>Skills:</strong> Perception +0 plus PB x 2, Stealth +2 plus PB</td>
</tr>
<tr>
<td colspan="6"><strong>Damage Immunities:</strong> poison</td>
</tr>
<tr>
<td colspan="6"><strong>Condition Immunities:</strong> exhaustion, poisoned</td>
</tr>
<tr>
<td colspan="6"><strong>Senses:</strong> darkvision 60 ft., passive Perception 10 + (PB x 2)</td>
</tr>
<tr>
<td colspan="6"><strong>Languages:</strong> understands the languages you speak</td>
</tr>
<tr>
<td colspan="6"><strong>Challenge:</strong> —</td>
</tr>
<tr>
<td colspan="6"><strong>Proficiency Bonus (PB):</strong> equals your bonus</td>
</tr>
<tr>
<td colspan="6"><strong><em>Evasion.</em></strong> If the homunculus is subjected to an effect that allows it to make a Dexterity saving throw to take only half damage, it instead takes no damage if it succeeds on the saving throw, and only half damage if it fails. It can't use this trait if it's incapacitated.</td>
</tr>
<tr>
<th colspan="6">Actions</th>
</tr>
<tr>
<td colspan="6"><strong><em>Force Strike.</em></strong> <em>Ranged Weapon Attack:</em> your spell attack modifier to hit, range 30 ft., one target you can see. <em>Hit:</em> 1d4 + PB force damage.</td>
</tr>
<tr>
<th colspan="6">Reactions</th>
</tr>
<tr>
<td colspan="6"><strong><em>Channel Magic.</em></strong> The homunculus delivers a spell you cast that has a range of touch. The homunculus must be within 120 feet of you.</td>
</tr>
</tbody></table>
<h3><span>Mind Sharpener</span></h3>
<p><strong><em>Item: A suit of armor or robes</em></strong></p>
<p>The infused item can send a jolt to the wearer to refocus their mind. The item has 4 charges. When the wearer fails a Constitution saving throw to maintain concentration on a spell, the wearer can use its reaction to expend 1 of the item's charges to succeed instead. The item regains 1d4 expended charges daily at dawn.</p>
<h3><span>Radiant Weapon</span></h3>
<p><strong><em>Prerequisite: 6th-level artificer</em></strong><br>
<strong><em>Item: A simple or martial weapon (requires attunement)</em></strong></p>
<p>This magic weapon grants a +1 bonus to attack and damage rolls made with it. While holding it, the wielder can take a bonus action to cause it to shed bright light in a 30-foot radius and dim light for an additional 30 feet. The wielder can extinguish the light as a bonus action.</p>
<p>The weapon has 4 charges. As a reaction immediately after being hit by an attack, the wielder can expend 1 charge and cause the attacker to be blinded until the end of the attacker's next turn, unless the attacker succeeds on a Constitution saving throw against your spell save DC. The weapon regains 1d4 expended charges daily at dawn.</p>
<h3><span>Repeating Shot</span></h3>
<p><strong><em>Item: A simple or martial weapon with the ammunition property (requires attunement)</em></strong></p>
<p>This magic weapon grants a +1 bonus to attack and damage rolls made with it when it's used to make a ranged attack, and it ignores the loading property if it has it.</p>
<p>If you load no ammunition in the weapon, it produces its own, automatically creating one piece of magic ammunition when you make a ranged attack with it. The ammunition created by the weapon vanishes the instant after it hits or misses a target.</p>
<h3><span>Replicate Magic Item</span></h3>
<p>Using this infusion, you replicate a particular magic item. You can learn this infusion multiple times; each time you do so, choose a magic item that you can make with it, picking from the Replicable Items tables. A table's title tells you the level you must be in the class to choose an item from the table. Alternatively, you can choose the magic item from among the common magic items in the game, not including potions or scrolls.</p>
<p>In the tables, an item's entry tells you whether the item requires attunement. See the item's description in the <em>Dungeon Master's Guide</em> for more information about it, including the type of object required for its making.</p>
<p>If you have <em>Xanathar's Guide to Everything</em>, you can choose from among the common magic items in that book when you pick a magic item you can replicate with this infusion.</p>
<table class="wiki-content-table">
<tbody><tr>
<th colspan="2">Replicable Magic Items (2nd-Level Artificer)</th>
</tr>
<tr>
<th>Magic Item</th>
<th>Attunement</th>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:alchemy-jug">Alchemy Jug</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:bag-of-holding">Bag of Holding</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:cap-of-water-breathing">Cap of Water Breathing</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:goggles-of-night">Goggles of Night</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:rope-of-climbing">Rope of Climbing</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:sending-stones">Sending Stones</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:wand-of-magic-detection">Wand of Magic Detection</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:wand-of-secrets">Wand of Secrets</a></td>
<td>No</td>
</tr>
</tbody></table>
<table class="wiki-content-table">
<tbody><tr>
<th colspan="2">Replicable Magic Items (6th-Level Artificer)</th>
</tr>
<tr>
<th>Magic Item</th>
<th>Attunement</th>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:boots-of-elvenkind">Boots of Elvenkind</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:cloak-of-elvenkind">Cloak of Elvenkind</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:cloak-of-the-manta-ray">Cloak of the Manta Ray</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:eyes-of-charming">Eyes of Charming</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:gloves-of-thievery">Gloves of Thievery</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:lantern-of-revealing">Lantern of Revealing</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:pipes-of-haunting">Pipes of Haunting</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:ring-of-water-walking">Ring of Water Walking</a></td>
<td>No</td>
</tr>
</tbody></table>
<table class="wiki-content-table">
<tbody><tr>
<th colspan="2">Replicable Magic Items (10th-level artificer)</th>
</tr>
<tr>
<th>Magic Item</th>
<th>Attunement</th>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:boots-of-striding-and-springing">Boots of Striding and Springing</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:boots-of-the-winterlands">Boots of the Winterlands</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:bracers-of-archery">Bracers of Archery</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:brooch-of-shielding">Brooch of Shielding</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:cloak-of-protection">Cloak of Protection</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:eyes-of-the-eagle">Eyes of the Eagle</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:gauntlets-of-ogre-power">Gauntlets of Ogre Power</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:gloves-of-missile-snaring">Gloves of Missile Snaring</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:gloves-of-swimming-and-climbing">Gloves of Swimming and Climbing</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:hat-of-disguise">Hat of Disguise</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:headband-of-intellect">Headband of Intellect</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:helm-of-telepathy">Helm of Telepathy</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:medallion-of-thoughts">Medallion of Thoughts</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:necklace-of-adaptation">Necklace of Adaptation</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:periapt-of-wound-closure">Periapt of Wound Closure</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:pipes-of-the-sewers">Pipes of the Sewers</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:quiver-of-ehlonna">Quiver of Ehlonna</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:ring-of-jumping">Ring of Jumping</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:ring-of-mind-shielding">Ring of Mind Shielding</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:slippers-of-spider-climbing">Slippers of Spider Climbing</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:ventilating-lungs">Ventilating Lungs (Eberron: Rising from the Last War)</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:winged-boots">Winged Boots</a></td>
<td>Yes</td>
</tr>
</tbody></table>
<table class="wiki-content-table">
<tbody><tr>
<th colspan="2">Replicable Magic Items (14th-level artificer)</th>
</tr>
<tr>
<th>Magic Item</th>
<th>Attunement</th>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:amulet-of-health">Amulet of Health</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:arcane-propulsion-arm">Arcane Propulsion Arm (Eberron: Rising from the Last War)</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:belt-of-giant-strength">Belt of Hill Giant Strength</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:boots-of-levitation">Boots of Levitation</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:boots-of-speed">Boots of Speed</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:bracers-of-defense">Bracers of Defense</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:cloak-of-the-bat">Cloak of the Bat</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:dimensional-shackles">Dimensional Shackles</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:gem-of-seeing">Gem of Seeing</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:horn-of-blasting">Horn of Blasting</a></td>
<td>No</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:ring-of-free-action">Ring of Free Action</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:ring-of-protection">Ring of Protection</a></td>
<td>Yes</td>
</tr>
<tr>
<td><a href="http://dnd5e.wikidot.com/wondrous-items:ring-of-the-ram">Ring of the Ram</a></td>
<td>Yes</td>
</tr>
</tbody></table>
<h3><span>Repulsion Shield</span></h3>
<p><strong><em>Prerequisite: 6th-level artificer</em></strong><br>
<strong><em>Item: A shield (requires attunement)</em></strong></p>
<p>A creature gains a +1 bonus to Armor Class while wielding this shield.</p>
<p>The shield has 4 charges. While holding it, the wielder can use a reaction immediately after being hit by a melee attack to expend 1 of the shield's charges and push the attacker up to 15 feet away. The shield regains 1d4 expended charges daily at dawn.</p>
<h3><span>Resistant Armor</span></h3>
<p><strong><em>Prerequisite: 6th-level artificer</em></strong><br>
<strong><em>Item: A suit of armor (requires attunement)</em></strong></p>
<p>While wearing this armor, a creature has resistance to one of the following damage types, which you choose when you infuse the item: acid, cold, fire, force, lightning, necrotic, poison, psychic, radiant, or thunder.</p>
<h3><span>Returning Weapon</span></h3>
<p><strong><em>Item: A simple or martial weapon with the thrown property</em></strong></p>
<p>This magic weapon grants a +1 bonus to attack and damage rolls made with it, and it returns to the wielder’s hand immediately after it is used to make a ranged attack.</p>
<h3><span>Spell-Refueling Ring</span></h3>
<p><strong><em>Prerequisite: 6th-level artificer</em></strong><br>
<strong><em>Item: A ring (requires attunement)</em></strong></p>
<p>While wearing this ring, the creature can recover one expended spell slot as an action. The recovered slot can be of 3rd level or lower. Once used, the ring can't be used again until the next dawn.</p>""",
    },
}

CLASS_DATA = {
  "_id": "VkRQ7glQvTWWiO00",
  "name": "Artificer",
  "type": "class",
  "img": "icons/commodities/tech/blueprint.webp",
  "system": {
    "description": {
      "value": """
<p>As an artificer, you gain the following class features.</p>
<h3>Hit Points</h3>
<p>
    <strong>Hit Dice:</strong> 1d8 per artificer level<br />
    <strong>Hit Points at 1st Level:</strong> 8 + your Constitution modifier<br />
    <strong>Hit Points at Higher Levels:</strong> 1d8 (or 6) + your Constitution modifier per artificer level after 1st</p>
<h3>Proficiencies</h3>
<p>
    <strong>Armor:</strong> Light armor, medium armor, shields<br />
    <strong>Weapons:</strong> Simple weapons<br />
    <strong>Tools:</strong> Thieves' tools, tinker's tools, one type of artisan's tools of your choice<br />
    <strong>Saving Throws: </strong>Constitution, Intelligence<br />
    <strong>Skills:</strong> Choose two from Arcana, History, Investigation, Medicine, Nature, Perception, Sleight of Hand
</p>
<h3>Equipment</h3>
<p>You start with the following equipment, in addition to the equipment granted by your background:</p>
<ul>
    <li>any two simple weapons</li>
    <li>a light crossbow and 20 bolts</li>
    <li>(a) studded leather armor or (b) scale mail</li>
    <li>thieves’ tools and a dungeoneer’s pack</li>
</ul>
<h1>artificer Advancement</h1>
<table>
    <thead>
        <tr>
            <td>Level</td>
            <td>Proficiency Bonus</td>
            <td>Infusions Known</td>
            <td>Infused Items</td>
            <td>Cantrips Known</td>
            <td>Features</td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1st</td>
            <td>+2</td>
            <td>-</td>
            <td>-</td>
            <td>2</td>
            <td>@Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO01]{Magical Tinkering}
                @Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO11]{Spellcasting}
            </td>
        </tr>
        <tr>
            <td>2nd</td>
            <td>+2</td>
            <td>4</td>
            <td>2</td>
            <td>2</td>
            <td>@Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO02]{Infuse Item}</td>
        </tr>
        <tr>
            <td>3rd</td>
            <td>+2</td>
            <td>4</td>
            <td>2</td>
            <td>2</td>
            <td>@Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO03]{The Right Tool for the Job}</td>
        </tr>
        <tr>
            <td>4th</td>
            <td>+2</td>
            <td>4</td>
            <td>2</td>
            <td>2</td>
            <td>@Compendium[dnd5e.classfeatures.s0Cc2zcX0JzIgam5]{Ability Score Improvement}</td>
        </tr>

        <tr>
            <td>5th</td>
            <td>+3</td>
            <td>4</td>
            <td>2</td>
            <td>2</td>
            <td>2nd Level Spell Slot, Artificer Specialist feature</td>
        </tr>
        <tr>
            <td>6th</td>
            <td>+3</td>
            <td>6</td>
            <td>3</td>
            <td>2</td>
            <td>@Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO04]{Tool Expertise}</td>
        </tr>
        <tr>
            <td>7th</td>
            <td>+3</td>
            <td>6</td>
            <td>3</td>
            <td>2</td>
            <td>@Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO05]{Flash of Genius}</td>
        </tr>
        <tr>
            <td>8th</td>
            <td>+3</td>
            <td>6</td>
            <td>3</td>
            <td>2</td>
            <td>
                @Compendium[dnd5e.classfeatures.s0Cc2zcX0JzIgam5]{Ability Score Improvement}
            </td>
        </tr>
        <tr>
            <td>9th</td>
            <td>+4</td>
            <td>6</td>
            <td>3</td>
            <td>2</td>
            <td>3rd Level Spell Slot, Artificer Specialist feature</td>
        </tr>
        <tr>
            <td>10th</td>
            <td>+4</td>
            <td>8</td>
            <td>4</td>
            <td>3</td>
            <td>
                @Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO06]{Magic Item Adept},
            </td>
        </tr>
        <tr>
            <td>11th</td>
            <td>+4</td>
            <td>8</td>
            <td>4</td>
            <td>3</td>
            <td>
                @Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO07]{Spell-Storing Item},
            </td>
        </tr>
        <tr>
            <td>12th</td>
            <td>+4</td>
            <td>8</td>
            <td>4</td>
            <td>3</td>
            <td>
                @Compendium[dnd5e.classfeatures.s0Cc2zcX0JzIgam5]{Ability Score Improvement}</td>
        </tr>
        <tr>
            <td>13th</td>
            <td>+5</td>
            <td>8</td>
            <td>4</td>
            <td>3</td>
            <td>4th Level Spell Slot</td>
        </tr>
        <tr>
            <td>14th</td>
            <td>+5</td>
            <td>10</td>
            <td>5</td>
            <td>4</td>
            <td>
                @Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO08]{Magic Item Savant}
            </td>
        </tr>
        <tr>
            <td>15th</td>
            <td>+5</td>
            <td>10</td>
            <td>5</td>
            <td>4</td>
            <td>Artificer Specialist feature</td>
        </tr>
        <tr>
            <td>16th</td>
            <td>+5</td>
            <td>10</td>
            <td>5</td>
            <td>4</td>
            <td>
                @Compendium[dnd5e.classfeatures.s0Cc2zcX0JzIgam5]{Ability Score Improvement}</td>
        </tr>
        <tr>
            <td>17th
            </td>
            <td>+6</td>
            <td>10</td>
            <td>5</td>
            <td>4</td>
            <td>5th Level Spell Slot</td>
        </tr>
        <tr>
            <td>18th</td>
            <td>+6</td>
            <td>12</td>
            <td>6</td>
            <td>4</td>
            <td>
                @Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO09]{Magic Item Master}
            </td>
        </tr>
        <tr>
            <td>19th</td>
            <td>+6</td>
            <td>12</td>
            <td>6</td>
            <td>4</td>
            <td>@Compendium[dnd5e.classfeatures.s0Cc2zcX0JzIgam5]{Ability Score Improvement}</td>
        </tr>
        <tr>
            <td>20th</td>
            <td>+6</td>
            <td>12</td>
            <td>6</td>
            <td>4</td>
            <td>@Compendium[dnd5e.classfeatures-extra.VkRQ7glQvTWWiO10]{Soul of Artifice}</td>
        </tr>

    </tbody>
</table>
<h1>artificer Archetypes</h1>
<p>At 3rd level, you choose the type of specialist you are. Your choice grants you features at 5th level and again at 9th and 15th level.</p>
""",
      "chat": "",
      "unidentified": ""
    },
    "source": "Tasha's Cauldron of Everything",
    "identifier": "artificer",
    "levels": 1,
    "hitDice": "d8",
    "hitDiceUsed": 0,
    "advancement": [],
    "saves": [
      "con",
      "int"
    ],
    "skills": {
      "number": 2,
      "choices": [
        "arc",
        "his",
        "inv",
        "med",
        "nat",
        "prc",
        "slt"
      ],
      "value": []
    },
    "spellcasting": {
      "progression": "half",
      "ability": "int"
    }
  },
  "effects": [],
  "folder": None,
  "sort": 0,
  "ownership": {
    "default": 0
  },
  "flags": {},
  "_stats": {
    "systemId": "dnd5e",
    "systemVersion": "2.1.0",
    "coreVersion": "10.291",
    "createdTime": time.time(),
    "modifiedTime": time.time(),
    "lastModifiedBy": EXPORTER_NAME
  }
}

def main():
    # get class data
    class_data = copy.deepcopy(CLASS_DATA)

    # get features
    for feature, data in FEATURE_DATA.items():
        f = copy.deepcopy(FEATURE_BASE)
        f["_id"] = data["id"]
        f["name"] = f"Artificer: {data['name']}"
        f["_stats"]["createdTime"] = time.time()
        f["_stats"]["modifiedTime"] = time.time()
        f["system"]["description"]["value"] = data["description"]
        f["system"]["source"] = "Tasha's Cauldron of Everything"
        f["img"] = data["icon"]

        subf = copy.deepcopy(SUBCLASS_FEATURE_BASE)
        subf["title"] = data["name"]
        subf["_id"] = generate_new_foundry_id()
        subf["configuration"]["items"] = [
            COMPENDIUM_REF_BASE + data["id"]
        ]
        subf["level"] = data["level"]
        class_data["system"]["advancement"].append(subf)

        feat_path = os.path.join(
            ARTIFICER_OUTPUT_DIR, 
            CLASSFEATURES_DIR,
            f"artificer-{feature}.json"
        )
        with open(feat_path, "w+") as o:
            o.write(json.dumps(f, indent=4))
    
    path = os.path.join(
        ARTIFICER_OUTPUT_DIR,
        CLASSES_DIR,
        "artificer.json",
    )
    with open(path, "w+") as o:
        o.write(json.dumps(class_data, indent=4))

if __name__ == "__main__":
    main()
