random_themes = [
    "Sci-Fi", 
    "Fantasy", 
    "Horror", 
    "Post-Apocalyptic", 
    "Spy Thriller", 
    "Victorian Mystery", 
    "Pulp Adventure", 
    "Cyberpunk", 
    "Isekai"
]

alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = r"(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|ca|gg|tv|co|net|org|io|gov)"

you_dead_regexps = [
    r"you('re| are) (dead|killed|slain|no more|nonexistent)",
    r"you (die|pass away|perish|suffocate|drown|bleed out)",
    r"you('ve| have) (died|perished|suffocated|drowned|been (killed|slain))",
    r"you (\w* )?(yourself )?to death",
    r"you (\w* )*(collapse|bleed out|chok(e|ed|ing)|drown|dissolve) (\w* )*and (die(|d)|pass away|cease to exist|(\w* )+killed)",
]

won_phrases = [
    r"you ((\w* )*and |)live happily ever after",
    r"you ((\w* )*and |)live (forever|eternally|for eternity)",
    r"you ((\w* )*and |)(are|become|turn into) ((a|now) )?(deity|god|immortal)",
    r"you ((\w* )*and |)((go|get) (in)?to|arrive (at|in)) (heaven|paradise)",
    r"you ((\w* )*and |)celebrate your (victory|triumph)",
    r"you ((\w* )*and |)retire",
]

first_to_second_mappings = [
    ("I'm", "you're"),
    ("i'm", "you're"),
    ("Im", "you're"),
    ("im", "you're"),
    ("Ive", "you've"),
    ("ive", "you've"),
    ("I am", "you are"),
    ("i am", "you are"),
    ("wasn't I", "weren't you"),
    ("I", "you"),
    ("I'd", "you'd"),
    ("i", "you"),
    ("I've", "you've"),
    ("was I", "were you"),
    ("am I", "are you"),
    ("was i", "were you"),
    ("am i", "are you"),
    ("wasn't I", "weren't you"),
    ("I", "you"),
    ("i", "you"),
    ("I'd", "you'd"),
    ("i'd", "you'd"),
    ("I've", "you've"),
    ("i've", "you've"),
    ("I was", "you were"),
    ("i was", "you were"),
    ("my", "your"),
    ("we", "you"),
    ("we're", "you're"),
    ("mine", "yours"),
    ("me", "you"),
    ("us", "you"),
    ("our", "your"),
    ("I'll", "you'll"),
    ("i'll", "you'll"),
    ("myself", "yourself"),
]

second_to_first_mappings = [
    ("you're", "I'm"),
    ("your", "my"),
    ("you are", "I am"),
    ("you were", "I was"),
    ("are you", "am I"),
    ("you", "I"),
    ("you", "me"),
    ("you'll", "I'll"),
    ("yourself", "myself"),
    ("you've", "I've"),
]

adjectives_say_d01 = [
    "mumble",
    "prattle",
    "incoherently say",
    "whine",
    "ramble",
    "wheeze",
]

adjectives_say_d20 = [
    "successfully",
    "persuasively",
    "expertly",
    "conclusively",
    "dramatically",
    "adroitly",
    "aptly",
]

adjective_action_d01 = [
    "disastrously",
    "incompetently",
    "dangerously",
    "stupidly",
    "horribly",
    "miserably",
    "sadly",
]

adjective_action_d20 = [
    "successfully",
    "expertly",
    "conclusively",
    "adroitly",
    "aptly",
    "masterfully",
]

palette_commands = [
    '/revert', '/quit', '/menu', '/retry', '/restart', '/print', '/sheet',
    '/look', '/drop', '/alter', '/altergen', '/context', '/remember',
    '/memalt', '/memswap', '/roll', '/forget', '/save', '/load',
    '/summarize', '/generate', '/help', '/set', '/settings',
    # Add dice shortcuts as commands too
    '/d4', '/d6', '/d8', '/d10', '/d12', '/d20', '/d100'
]

palette_action_verbs = [
    'go', 'walk', 'run', 'move', 'travel', 'head', 'venture',
    'take', 'get', 'grab', 'pick up', 'collect', 'gather',
    'drop', 'put down', 'place', 'set down', 'leave',
    'open', 'close', 'shut', 'unlock', 'lock',
    'use', 'utilize', 'employ', 'operate', 'activate',
    'examine', 'look at', 'inspect', 'study', 'observe', 'check',
    'search', 'look for', 'find', 'seek', 'hunt for',
    'attack', 'fight', 'strike', 'hit', 'punch', 'kick',
    'defend', 'block', 'parry', 'dodge', 'evade',
    'speak to', 'talk to', 'say', 'whisper', 'shout', 'call',
    'climb', 'jump', 'leap', 'hop', 'vault',
    'hide', 'sneak', 'creep', 'skulk', 'prowl',
    'push', 'pull', 'drag', 'lift', 'carry',
    'break', 'smash', 'destroy', 'shatter', 'crush',
    'fix', 'repair', 'mend', 'restore', 'rebuild',
    'read', 'write', 'draw', 'sketch', 'note',
    'listen', 'hear', 'eavesdrop',
    'smell', 'sniff', 'taste',
    'wait', 'rest', 'sleep', 'sit', 'stand',
    'throw', 'toss', 'hurl', 'cast', 'fling',
    'buy', 'sell', 'trade', 'purchase', 'barter',
    'give', 'hand over', 'offer', 'present',
    'follow', 'chase', 'pursue', 'track',
    'escape', 'flee', 'run away', 'retreat'
]

palette_dice_shortcuts = [
    'd4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100',
    '1d4', '1d6', '1d8', '1d10', '1d12', '1d20', '1d100',
    '2d6', '3d6', '4d6', '2d8', '3d8', '2d10', '2d12'
]

palette_important_nouns = [
    # Important nouns/objects
    'sword', 'shield', 'armor', 'potion', 'scroll', 'book', 'chest',
    'door', 'window', 'stairs', 'ladder', 'bridge', 'path', 'road',
    'forest', 'mountain', 'river', 'cave', 'castle', 'tower', 'dungeon',
    'treasure', 'gold', 'silver', 'jewel', 'crystal', 'magic', 'spell',
    'monster', 'dragon', 'goblin', 'orc', 'wizard', 'knight', 'guard',
    'merchant', 'innkeeper', 'bartender', 'priest', 'king', 'queen'
]

KEYWORD_ACTIONS = {
    # --- Fantasy & Pulp Adventure ---
    "door": ["Try to open the door", "Knock on the door", "Listen at the door", "Examine the door for traps", "Barricade the door"],
    "chest": ["Try to open the chest", "Look for a key", "Examine the chest for traps", "Try to smash the chest", "Leave the chest alone"],
    "key": ["Pick up the key", "Try using the key on a nearby lock", "Examine the key's inscription", "Hide the key"],
    "enemy": ["Attack the enemy", "Try to sneak past the enemy", "Attempt to talk to the enemy", "Look for a weakness", "Create a diversion"],
    "creature": ["Attack the creature", "Observe the creature from a distance", "Try to communicate with the creature", "Slowly back away", "Offer it food"],
    "sword": ["Pick up the sword", "Inspect the sword for maker's marks", "Practice a few swings", "Sharpen the blade"],
    "book": ["Read the book", "Skim through the book", "Look for a title on the spine", "Check for hidden notes in the margins"],
    "note": ["Read the note", "Pick up the note", "Check the other side of the note", "Look for a hidden message using a light source"],
    "light": ["Approach the light", "Investigate the source of the light", "Shield your eyes", "Extinguish the light source"],
    "path": ["Follow the path", "Examine the path for tracks", "Look for an alternate route", "Set a trap on the path"],
    "river": ["Try to swim across the river", "Look for a bridge", "Search for a shallow spot to cross", "Build a raft"],
    "bridge": ["Cross the bridge carefully", "Test the bridge's stability", "Look under the bridge", "Cut the ropes of the bridge"],
    "rope": ["Climb the rope", "Pull the rope", "Cut the rope", "Tie the rope to a sturdy object"],
    "lever": ["Pull the lever", "Push the lever", "Examine the mechanism it's connected to", "Jam the lever with something"],
    "torch": ["Pick up the torch", "Use the torch to light up the area", "Extinguish the torch", "Use the torch to set something flammable on fire"],
    "potion": ["Drink the potion", "Examine the potion's color and smell", "Save the potion for later", "Try to identify the potion"],
    "scroll": ["Read the scroll", "Unfurl the scroll", "Store the scroll in your bag", "Copy the text from the scroll"],
    "bed": ["Rest on the bed", "Search under the bed", "Check the pillows for hidden items", "Flip the mattress"],
    "window": ["Look out the window", "Try to open the window", "Break the window", "Barricade the window"],
    "guard": ["Talk to the guard", "Try to bribe the guard", "Attempt to distract the guard", "Wait for the guard to change shifts", "Attack the guard"],
    "merchant": ["Ask the merchant what they are selling", "Try to haggle with the merchant", "Ask the merchant for local rumors", "Attempt to sell an item"],
    "altar": ["Kneel at the altar", "Examine the altar for offerings", "Place an item on the altar", "Desecrate the altar"],
    "statue": ["Examine the statue", "Look for any moving parts on the statue", "Try to push the statue", "Pray to the statue"],
    "trap": ["Try to disarm the trap", "Look for a way around the trap", "Throw an object to trigger the trap", "Mark the trap's location"],
    "body": ["Search the body for loot", "Examine the body for the cause of death", "Hide the body", "Give the body a proper burial"],
    "mirror": ["Look into the mirror", "Check for reflections that seem out of place", "Touch the mirror's surface", "Smash the mirror"],
    "map": ["Study the map", "Look for landmarks on the map", "Try to determine your position", "Update the map with new information"],
    "crystal": ["Touch the crystal", "Examine the crystal for flaws", "Hold the crystal up to a light source", "Channel energy into the crystal"],
    "throne": ["Sit on the throne", "Examine the throne for secret levers", "Look behind the throne", "Claim the throne as your own"],
    "wall": ["Search the wall for secret passages", "Try to climb the wall", "Listen for sounds on the other side", "Attempt to break down the wall"],
    "sound": ["Follow the sound", "Try to identify the source of the sound", "Hide from the sound", "Call out in response to the sound"],
    "darkness": ["Wait for your eyes to adjust", "Listen carefully for any sounds", "Feel your way forward", "Call out into the darkness"],

    # --- Sci-Fi & Post-Apocalyptic ---
    "computer": ["Access the computer terminal", "Look for a password", "Hack the system", "Download the files", "Wipe the hard drive"],
    "console": ["Activate the console", "Check the console for error messages", "Reroute power through the console", "Interface your datapad with the console"],
    "robot": ["Activate the robot", "Deactivate the robot", "Give the robot a command", "Search the robot for salvageable components"],
    "laser": ["Dodge the laser beam", "Find the laser's power source", "Use a reflective object to deflect the laser", "Disrupt the emitter"],
    "alien": ["Try to communicate with the alien using universal gestures", "Observe the alien's behavior", "Scan the alien with your tricorder", "Offer a gift to the alien"],
    "spaceship": ["Board the spaceship", "Attempt to start the spaceship's engines", "Check the ship's logs", "Hide in the cargo bay"],
    "airlock": ["Cycle the airlock", "Check the airlock's external viewscreen", "Sabotage the airlock controls", "Put on an enviro-suit"],
    "jetpack": ["Put on the jetpack", "Test the jetpack's thrusters", "Refuel the jetpack", "Use the jetpack to reach a high ledge"],
    "zombie": ["Attack the zombie in the head", "Shove the zombie away", "Run from the zombie", "Lure the zombie into a trap"],
    "horde": ["Run from the horde", "Find a defensible position", "Throw a Molotov cocktail at the horde", "Create a loud noise to distract them"],
    "survivor": ["Approach the survivor cautiously", "Offer the survivor supplies", "Ask the survivor to join you", "Be wary of the survivor"],
    "barricade": ["Strengthen the barricade", "Look for a way around the barricade", "Dismantle the barricade for supplies", "Set up a watch post"],
    "scrap": ["Scavenge the scrap pile for useful parts", "Use the scrap to build something", "Check the scrap for hidden dangers"],
    "radiation": ["Avoid the radioactive area", "Look for protective gear", "Use a Geiger counter to measure the radiation levels"],
    "bunker": ["Search for the bunker entrance", "Try to open the bunker hatch", "Listen for sounds from inside the bunker", "Look for an alternate power source"],
    "engine": ["Try to start the engine", "Check the fuel tank", "Look for missing parts", "Hotwire the engine"],

    # --- Victorian, Noir, & Lovecraftian ---
    "clue": ["Examine the clue closely with a magnifying glass", "Look for more clues in the area", "Think about what the clue implies", "Pocket the clue as evidence"],
    "footprints": ["Follow the footprints", "Examine the footprints to identify the type of shoe", "Make a plaster cast of the footprints", "Cover your own tracks"],
    "safe": ["Try to crack the safe", "Look for the combination written nearby", "Listen to the tumblers with a stethoscope", "Use dynamite on the safe"],
    "telegram": ["Read the telegram", "Check who sent the telegram", "Look for a hidden meaning in the message", "Send a reply"],
    "informant": ["Meet with the informant in a discreet location", "Ask the informant for information", "Pay the informant for their help", "Question the informant's motives"],
    "contraption": ["Examine the strange contraption", "Try to figure out the contraption's purpose", "Activate the contraption carefully", "Look for the inventor's notes"],
    "fog": ["Proceed cautiously through the fog", "Listen for the sound of footsteps", "Use a gas lamp to see", "Hide in an alleyway"],
    "séance": ["Participate in the séance", "Question the medium", "Look for signs of trickery", "Try to communicate with a specific spirit"],
    "diary": ["Read the diary", "Look for entries written in code", "Check for torn-out pages", "Cross-reference the diary with known events"],
    "madness": ["Try to steady your nerves", "Avert your gaze from the horror", "Recite a calming phrase", "Embrace the madness"],
    "cultist": ["Eavesdrop on the cultists' conversation", "Interrupt the ritual", "Steal the artifact from the cultists", "Infiltrate the cult"],
    "artifact": ["Examine the strange artifact", "Resist the artifact's influence", "Attempt to destroy the artifact", "Hide the artifact from the world"],
    "shadow": ["Watch the shadow", "Move away from the shadow", "Shine a light on the shadow", "Try to interact with the shadow"],

    # --- Modern & Urban ---
    "car": ["Get in the car", "Start the car", "Check the trunk", "Siphon gas from the car", "Hotwire the car"],
    "phone": ["Check the phone for messages", "Make a call", "Look through the phone's contacts", "Check the phone's battery"],
    "camera": ["Check the security camera footage", "Disable the camera", "Find the camera's blind spot", "Use the camera to your advantage"],
    "elevator": ["Take the elevator", "Check the elevator's maintenance panel", "Pry open the elevator doors"],
    "television": ["Turn on the television", "Change the channel", "Look for a news report", "Smash the television"],
    "vending machine": ["Buy something from the vending machine", "Shake the vending machine", "Try to break into the vending machine"],
}

# Dictionary for inventory-based conditional suggestions
INVENTORY_SUGGESTIONS = {
    # --- Fantasy & Pulp Adventure ---
    "locked door": { "item": "key", "action": "Try to unlock the door with the key"},
    "stuck door": { "item": "crowbar", "action": "Use the crowbar to pry the door open"},
    "heavy door": { "item": "battering ram", "action": "Use the battering ram to break down the door"},
    "locked chest": { "item": "lockpick", "action": "Attempt to pick the lock on the chest"},
    "ancient inscription": { "item": "journal", "action": "Consult your journal to translate the inscription"},
    "deep chasm": { "item": "whip", "action": "Use your whip to swing across the chasm"},
    "pressure plate": { "item": "idol", "action": "Carefully swap the idol with a bag of sand"},
    "darkness": { "item": "torch", "action": "Light your torch to see"},
    "dark room": { "item": "lantern", "action": "Light your lantern to illuminate the room"},
    "tangled vines": { "item": "machete", "action": "Cut through the vines with your machete"},
    "brittle wall": { "item": "hammer", "action": "Use the hammer to break through the wall"},
    "loose dirt": { "item": "shovel", "action": "Use the shovel to dig in the loose dirt"},
    "riddle": { "item": "book", "action": "Look for clues to the riddle in your book"},
    "golem": { "item": "scroll", "action": "Read the scroll to see if it affects the golem"},
    "ghost": { "item": "amulet", "action": "Hold up the amulet to ward off the ghost"},
    "undead creature": { "item": "holy symbol", "action": "Present your holy symbol to the undead creature"},
    "sleeping guard": { "item": "potion", "action": "Use the sleeping potion to keep the guard asleep"},
    "guard patrol": { "item": "invisibility potion", "action": "Drink the invisibility potion to sneak past the guards"},
    "wound": { "item": "healing herb", "action": "Apply the healing herb to your wound"},
    "poisoned food": { "item": "antidote", "action": "Take the antidote to cure the poison"},
    "cursed idol": { "item": "holy water", "action": "Sprinkle the holy water on the idol to cleanse it"},
    "palace guard": { "item": "royal seal", "action": "Show the royal seal to the palace guard"},
    "hungry animal": { "item": "food", "action": "Offer food to the animal to pacify it"},
    "coded message": { "item": "cipher", "action": "Use your cipher to decode the message"},

    # --- Sci-Fi & Post-Apocalyptic ---
    "computer terminal": { "item": "access card", "action": "Use the access card on the computer terminal"},
    "offline terminal": { "item": "power cell", "action": "Insert the power cell to activate the terminal"},
    "laser grid": { "item": "hacking device", "action": "Use your hacking device to disable the laser grid"},
    "damaged robot": { "item": "repair kit", "action": "Use the repair kit to fix the robot"},
    "strange alien": { "item": "translator", "action": "Use your universal translator to speak with the alien"},
    "hostile drone": { "item": "EMP grenade", "action": "Throw an EMP grenade to disable the drone"},
    "horde of zombies": { "item": "shotgun", "action": "Use your shotgun to clear a path through the zombies"},
    "armored zombie": { "item": "armor-piercing rounds", "action": "Load your weapon with armor-piercing rounds"},
    "boarded up window": { "item": "crowbar", "action": "Use the crowbar to remove the boards"},
    "broken generator": { "item": "scrap metal", "action": "Use scrap metal to try and repair the generator"},
    "radioactive zone": { "item": "geiger counter", "action": "Use the Geiger counter to find the safest path"},
    "irradiated area": { "item": "rad-away", "action": "Use a Rad-Away to cleanse the radiation"},
    "empty magazine": { "item": "ammo", "action": "Reload your weapon with your spare ammunition"},
    "unfiltered water": { "item": "water purifier", "action": "Use the water purifier before drinking"},
    "barbed wire": { "item": "wire cutters", "action": "Use the wire cutters to get through the fence"},
    "locked vehicle": { "item": "slim jim", "action": "Use the slim jim to unlock the car door"},

    # --- Victorian, Noir, & Lovecraftian ---
    "faint writing": { "item": "magnifying glass", "action": "Use your magnifying glass to examine the writing"},
    "locked safe": { "item": "stethoscope", "action": "Use the stethoscope to listen to the safe's tumblers"},
    "secret document": { "item": "camera", "action": "Use your camera to photograph the document"},
    "suspicious person": { "item": "disguise kit", "action": "Use your disguise kit to follow the person unnoticed"},
    "bloodstain": { "item": "testing kit", "action": "Use your forensic kit to analyze the bloodstain"},
    "strange device": { "item": "toolkit", "action": "Use your toolkit to disassemble the strange device"},
    "fainting spell": { "item": "smelling salts", "action": "Use the smelling salts to revive the person"},
    "unsettling presence": { "item": "laudanum", "action": "Take a dose of laudanum to calm your nerves"},
    "cryptic letter": { "item": "codebook", "action": "Use your codebook to decipher the letter"},
    "non-euclidean geometry": { "item": "sanity potion", "action": "Drink the sanity potion to steady your mind"},
    "eldritch symbol": { "item": "elder sign", "action": "Present the Elder Sign to ward off the evil"},
    "whispering shadows": { "item": "silver locket", "action": "Clutch the silver locket for comfort"},

    # --- Modern & Urban ---
    "locked door": { "item": "credit card", "action": "Try to slip the lock with your credit card"},
    "electronic lock": { "item": "laptop", "action": "Use your laptop to hack the electronic lock"},
    "dark alley": { "item": "flashlight", "action": "Use your flashlight to see in the dark alley"},
    "security camera": { "item": "spray paint", "action": "Use spray paint to obscure the camera's lens"},
    "empty fuel tank": { "item": "gas can", "action": "Refuel the vehicle with the gas can"},
    "flat tire": { "item": "tire iron", "action": "Use the tire iron and spare to change the flat tire"},
    "fire": { "item": "fire extinguisher", "action": "Use the fire extinguisher to put out the fire"},
    "power outage": { "item": "backup generator", "action": "Start the backup generator to restore power"},
}