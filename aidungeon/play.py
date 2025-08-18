# aidungeon/play.py
from pathlib import Path
import os
import re
import random

from .getconfig import config, setting_info, get_ollama_host, get_ollama_model, logger, settings
from .storymanager import Story
from .utils import *
from .ollamagenerator import OllamaGenerator, get_generator
from .interface import instructions

# Keyword dictionary for simple state-based action suggestions
# Keyword dictionary for simple state-based action suggestions
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
    "computer": ["Log into the computer", "Search the computer's files", "Hack the computer", "Install a virus on the computer"],
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


def generate_random_prompt(generator):
    """Uses the AI to generate a random story prompt."""
    output("\nGenerating a random story from the AI...", "loading-message")
    themes = ["Sci-Fi", "Fantasy", "Horror", "Post-Apocalyptic", "Spy Thriller", "Victorian Mystery", "Pulp Adventure", "Cyberpunk", "Isekai"]
    chosen_theme = random.choice(themes)

    prompt_for_ai = (
        f"You are a creative assistant. Generate a random story prompt for a text-based adventure game with a '{chosen_theme}' theme.\n"
        "The prompt must consist of two paragraphs separated by '|||'. Keep the total response under 150 words.\n"
        "The first paragraph is the context that introduces a character and setting.\n"
        "The second paragraph is the first action the character takes, and it should end with a comma or without final punctuation.\n"
        "Do not include any other text, comments, or confirmation; only provide the two-paragraph output.\n\n"
        "EXAMPLE:\n"
        "I am a cyber-scavenger in the neon-drenched ruins of Neo-City, hunted by corporate enforcers after a data heist went wrong. My only chance is to find the rogue AI known as 'Echo' in the underbelly of the city.|||I pull my cloak tighter to hide from the perpetual acid rain and slip into the shadows of a crowded alley,"
    )

    full_prompt_text = generator.generate_raw(
        prompt_for_ai,
        temperature=1.0,
        generate_num=500,  # Increased token limit
    )

    # For debug purposes, save the raw output to a file
    try:
        save_path = Path("prompts", "random_story.txt")
        with save_path.open('w', encoding='utf-8') as f:
            f.write(full_prompt_text)
        logger.info("Saved raw random prompt response to prompts/random_story.txt")
    except IOError as e:
        logger.error(f"Failed to save debug random story file: {e}")
        output("Warning: Could not save debug file 'random_story.txt'.", "error")

    # Relaxed parsing logic
    context, first_action = None, None
    if '|||' in full_prompt_text:
        # First, try the explicit separator
        parts = full_prompt_text.split('|||', 1)
        if len(parts) == 2:
            context, first_action = parts
    elif '\n\n' in full_prompt_text:
        # Fallback to double newline if separator is missing
        parts = full_prompt_text.split('\n\n', 1)
        if len(parts) == 2:
            context, first_action = parts

    if context and first_action:
        return context.strip(), first_action.strip()
    else:
        # If both parsing methods fail
        output("Error: The AI failed to generate a valid random prompt. Please try again.", "error")
        output("Check prompts/random_story.txt for the raw AI output.", "message")
        return None, None


def d20ify_speech(action, d):
    """Add D20 flavor to speech actions."""
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
    if d == 1:
        adjective = random.sample(adjectives_say_d01, 1)[0]
        action = "You " + adjective + " " + action
    elif d == 20:
        adjective = random.sample(adjectives_say_d20, 1)[0]
        action = "You " + adjective + " say " + action
    else:
        action = "You say " + action
    return action


def d20ify_action(action, d):
    """Add D20 flavor to regular actions."""
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
    if d == 1:
        adjective = random.sample(adjective_action_d01, 1)[0]
        action = "You " + adjective + " fail to " + action
    elif d < 5:
        action = "You attempt to " + action
    elif d < 10:
        action = "You try to " + action
    elif d < 15:
        action = "You start to " + action
    elif d < 20:
        action = "You " + action
    else:
        adjective = random.sample(adjective_action_d20, 1)[0]
        action = "You " + adjective + " " + action
    return action


def settings_menu():
    """Interactive settings configuration menu."""
    all_settings = list(setting_info.keys())
    while True:
        list_items([pad_text(k, 19) + v[0] + (" " if v[0] else "") +
                    "Default: " + str(v[1]) + " | "
                                              "Current: " + settings.get(k) for k, v in setting_info.items()] + [
                       "(Finish)"])
        i = input_number(len(all_settings), default=-1)
        if i == len(all_settings):
            output("Done editing settings. ", "menu")
            return
        else:
            key = all_settings[i]
            output(key + ": " + setting_info[key][0], "menu")
            output("Default: " + str(setting_info[key][1]), "menu", beg='')
            output("Current: " + str(settings[key]), "menu", beg='')
            new_value = input_line("Enter the new value: ", "query")
            if len(new_value.strip()) == 0:
                output("Invalid value; cancelling. ", "error")
                continue
            output(key + ": " + setting_info[key][0], "menu")
            output("Current: " + str(settings[key]), "menu", beg='')
            output("New: " + str(new_value), "menu", beg='')
            output("Saving an invalid option will corrupt file! ", "message")
            if input_bool("Change setting? (y/N): ", "selection-prompt"):
                settings[key] = new_value
                try:
                    with open("config.ini", "w", encoding="utf-8") as file:
                        config.write(file)
                except IOError:
                    output("Permission error! Changes will not be saved for next session.", "error")


def load_prompt(f, format=True):
    """Load a prompt from a file."""
    with f.open('r', encoding="utf-8") as file:
        try:
            lines = file.read().strip().split('\n')
            if len(lines) < 2:
                context = lines[0]
                prompt = ""
            else:
                context = lines[0]
                prompt = ' '.join(lines[1:])
            if format:
                return format_result(context), format_result(prompt)
            else:
                return context, prompt
        except IOError:
            output("Something went wrong; aborting. ", "error")
    return None, None


def new_story(generator, context, prompt, memory=None, first_result=None):
    """Create a new story with the given parameters."""
    if memory is None:
        memory = []
    context = context.strip()
    prompt = prompt.strip()
    erase = 0
    if use_ptoolkit():
        erase = output(context, 'user-text', prompt, 'user-text', sep="\n\n")
    story = Story(generator, context, memory)
    if first_result is None:
        story.act(prompt)
    else:
        story.actions.append(prompt)
        story.results.append(first_result)
    clear_lines(erase)
    story.print_story()
    return story


def save_story(story, file_override=None, autosave=False):
    """Save the existing story to a JSON file."""
    if not file_override:
        savefile = story.savefile
        while True:
            print()
            temp_savefile = input_line("Please enter a name for this save: ", "query")
            savefile = savefile if not temp_savefile or len(temp_savefile.strip()) == 0 else temp_savefile
            if not savefile or len(savefile.strip()) == 0:
                output("Please enter a valid savefile name. ", "error")
            else:
                break
    else:
        savefile = file_override
    savefile = os.path.splitext(savefile.strip())[0]
    savefile = re.sub(r"^ *saves *[/\\] *(.*) *(?:\.json)?", "\\1", savefile).strip()
    story.savefile = savefile
    savedata = story.to_json()
    finalpath = "saves/" + savefile + ".json"
    try:
        os.makedirs(os.path.dirname(finalpath), exist_ok=True)
    except OSError:
        if not autosave:
            output("Error when creating subdirectory; aborting. ", "error")
    with open(finalpath, 'w') as f:
        try:
            f.write(savedata)
            if not autosave:
                output("Successfully saved to " + savefile, "message")
        except IOError:
            if not autosave:
                output("Unable to write to file; aborting. ", "error")


def load_story(f, gen):
    """Load a story from a JSON file."""
    with f.open('r', encoding="utf-8") as file:
        try:
            story = Story(gen, "")
            savefile = os.path.splitext(file.name.strip())[0]
            savefile = re.sub(r"^ *saves *[/\\] *(.*) *(?:\.json)?", "\\1", savefile).strip()
            story.savefile = savefile
            story.from_json(file.read())
            return story, story.context, story.actions[-1] if len(story.actions) > 0 else ""
        except FileNotFoundError:
            output("Save file not found. ", "error")
        except IOError:
            output("Something went wrong; aborting. ", "error")
    return None, None, None


def alter_text(text):
    """Interactive text editing interface."""
    if use_ptoolkit():
        return edit_multiline(text).strip()

    sentences = sentence_split(text)
    while True:
        output(" ".join(sentences), 'menu')
        list_items(
            [
                "Edit a sentence.",
                "Remove a sentence.",
                "Add a sentence.",
                "Edit entire prompt.",
                "Save and finish."
            ], 'menu')
        try:
            i = input_number(4)
        except:
            continue
        if i == 0:
            while True:
                output("Choose the sentence you want to edit.", "menu")
                list_items(sentences + ["(Back)"], "menu")
                i = input_number(len(sentences), default=-1)
                if i == len(sentences):
                    break
                else:
                    output(sentences[i], 'menu')
                    res = input_line("Enter the altered sentence: ", 'menu').strip()
                    if len(res) == 0:
                        output("Invalid sentence entered: returning to previous menu. ", 'error')
                        continue
                    sentences[i] = res
        elif i == 1:
            while True:
                output("Choose the sentence you want to remove.", "menu")
                list_items(sentences + ["(Back)"], "menu")
                i = input_number(len(sentences), default=-1)
                if i == len(sentences):
                    break
                else:
                    del sentences[i]
        elif i == 2:
            while True:
                output("Choose the sentence you want to insert after.", "menu")
                list_items(["(Beginning)"] + sentences + ["(Back)"], "menu")
                maxn = len(sentences) + 1
                i = input_number(maxn, default=-1)
                if i == maxn:
                    break
                else:
                    res = input_line("Enter the new sentence: ", 'menu').strip()
                    if len(res) == 0:
                        output("Invalid sentence entered: returning to previous menu. ", 'error')
                        continue
                    sentences.insert(i, res)
        elif i == 3:
            output(" ".join(sentences), 'menu')
            res = input_line("Enter the new altered prompt: ", 'menu').strip()
            if len(res) == 0:
                output("Invalid prompt entered: returning to previous menu. ", 'error')
                continue
            sentences = sentence_split(res)
        elif i == 4:
            break
    return " ".join(sentences).strip()


class GameManager:
    """Main game management class adapted for Ollama."""

    def __init__(self, gen: OllamaGenerator):
        self.generator = gen
        self.story, self.context, self.prompt = None, None, None

    def get_state_based_suggestions(self):
        """Parse the last result for keywords and return relevant actions."""
        if not self.story or not self.story.results:
            return []

        last_result = self.story.results[-1].lower()
        found_actions = []

        # Check for inventory-based suggestions first
        for trigger, data in INVENTORY_SUGGESTIONS.items():
            if trigger in last_result and self.story.character.has_item(data["item"]):
                found_actions.append(data["action"])

        # Check for simple keyword actions
        for keyword, actions in KEYWORD_ACTIONS.items():
            if keyword in last_result:
                found_actions.extend(actions)
        
        # Return unique actions while preserving order
        return list(dict.fromkeys(found_actions))

    def init_story(self) -> bool:
        """Initialize the story. Called by play_story."""
        self.story, self.context, self.prompt = None, None, None
        list_items(["Pick Prompt From File (Default if you type nothing)",
                    "Write Custom Prompt",
                    "Load a Saved Game",
                    "Generate Random Story",
                    "Change Settings"],
                   'menu')
        new_game_option = input_number(4)

        if new_game_option == 0:
            prompt_file = select_file(Path("prompts"), ".txt")
            if prompt_file:
                self.context, self.prompt = load_prompt(prompt_file)
            else:
                return False
        elif new_game_option == 1:
            with open(
                    Path("interface/", "prompt-instructions.txt"), "r", encoding="utf-8"
            ) as file:
                output(file.read(), "instructions", wrap=False)
            if use_ptoolkit():
                output("Context>", "main-prompt")
                self.context = edit_multiline()
                output("Prompt>", "main-prompt")
                self.prompt = edit_multiline()
            else:
                self.context = input_line("Context> ", "main-prompt")
                self.prompt = input_line("Prompt> ", "main-prompt")
            filename = input_line("Name to save prompt as? (Leave blank for no save): ", "query")
            filename = re.sub("-$", "", re.sub("^-", "", re.sub("[^a-zA-Z0-9_-]+", "-", filename)))
            if filename != "":
                try:
                    with open(Path("prompts", filename + ".txt"), "w", encoding="utf-8") as f:
                        f.write(self.context + "\n" + self.prompt)
                except IOError:
                    output("Permission error! Unable to save custom prompt. ", "error")
        elif new_game_option == 2:
            story_file = select_file(Path("saves"), ".json")
            if story_file:
                self.story, self.context, self.prompt = load_story(story_file, self.generator)
            else:
                return False
        elif new_game_option == 3:
            self.context, self.prompt = generate_random_prompt(self.generator)
            if self.context is None:
                return False
        elif new_game_option == 4:
            settings_menu()
            return False

        if len((self.context + self.prompt).strip()) == 0:
            output("Story has no prompt or context. Please enter a valid custom prompt. ", "error")
            return False

        if self.story is None:
            auto_file = ""
            if settings.getboolean("autosave"):
                while True:
                    auto_file = input_line("Autosaving enabled. Please enter a save name: ", "query")
                    if not auto_file or len(auto_file.strip()) == 0:
                        output("Please enter a valid savefile name. ", "error")
                    else:
                        break
            instructions()
            output("Generating story...", "loading-message")
            self.story = new_story(self.generator, self.context, self.prompt)
            self.story.savefile = auto_file
        else:
            instructions()
            output("Loading story...", "loading-message")
            self.story.print_story()

        if settings.getboolean("autosave"):
            save_story(self.story, file_override=self.story.savefile, autosave=True)

        return True

    def process_command(self, cmd_regex) -> bool:
        """Process an in-game command."""
        command = cmd_regex.group(1).strip().lower()
        args = cmd_regex.group(2).strip().split()
        
        if command == "set":
            if len(args) < 2:
                output("Invalid number of arguments for set command. ", "error")
                instructions()
                return False
            if args[0] in settings:
                curr_setting_val = settings[args[0]]
                output(
                    "Current Value of {}: {}     Changing to: {}".format(
                        args[0], curr_setting_val, args[1]
                    )
                )
                output("Saving an invalid option will corrupt file! ", "error")
                if input_bool("Save setting? (y/N): ", "selection-prompt"):
                    settings[args[0]] = args[1]
                    try:
                        with open("config.ini", "w", encoding="utf-8") as file:
                            config.write(f)
                    except IOError:
                        output("Permission error! Changes will not be saved for next session.", "error")
            else:
                output("Invalid setting", "error")
                instructions()

        elif command == "settings":
            settings_menu()
            self.story.print_last()

        elif command == "menu":
            if input_bool("Do you want to save? (y/N): ", "query"):
                save_story(self.story)
            return True

        elif command == "restart":
            output("Restarting story...", "loading-message")
            if len((self.context + self.prompt).strip()) == 0:
                output("Story has no prompt or context. Please enter a valid prompt. ", "error")
                return False
            self.story = new_story(self.generator, self.story.context, self.prompt)

        elif command == "quit":
            if input_bool("Do you want to save? (y/N): ", "query"):
                save_story(self.story)
            exit()

        elif command == "help":
            instructions()

        elif command == "print":
            use_wrap = input_bool("Print with wrapping? (y/N): ", "query")
            use_color = input_bool("Print with colors? (y/N): ", "query")
            output("Printing story...", "message")
            self.story.print_story(wrap=use_wrap, color=use_color)

        elif command == "retry":
            if len(self.story.actions) < 2:
                output("Restarting story...", "loading-message")
                if len((self.context + self.prompt).strip()) == 0:
                    output("Story has no prompt or context. Please enter a valid prompt. ", "error")
                    return False
                self.story = new_story(self.generator, self.story.context, self.prompt)
                return False
            else:
                output("Retrying...", "loading-message")
                new_action = self.story.actions[-1]
                self.story.revert()
                result = self.story.act(new_action)
                if self.story.is_looping():
                    self.story.revert()
                    output("That action caused the model to start looping. Try something else instead. ",
                           "error")
                    return False
                self.story.print_last()

        elif command == "revert":
            if len(self.story.actions) < 2:
                output("You can't go back any farther. ", "error")
                return False
            self.story.revert()
            output("Last action reverted. ", "message")
            self.story.print_last()
        
        elif command in ["sheet", "char", "inventory"]:
            self.story.character.display()

        elif command == "drop":
            item_to_drop = " ".join(args)
            if not item_to_drop:
                output("You need to specify what to drop. Usage: /drop [item name]", "error")
            else:
                self.story.character.remove_item(item_to_drop)

        elif command == "alter":
            self.story.results[-1] = alter_text(self.story.results[-1])
            self.story.print_last()

        elif command == "context":
            self.story.context = alter_text(self.story.context)
            self.story.print_last()

        elif command == "remember":
            memory = cmd_regex.group(2).strip()
            if len(memory) > 0:
                memory = re.sub("^[Tt]hat +(.*)", "\\1", memory)
                memory = memory.strip('.')
                memory = memory.strip('!')
                memory = memory.strip('?')
                self.story.memory.append(memory[0].upper() + memory[1:] + ".")
                output("You remember " + memory + ". ", "message")
            else:
                output("Please enter something valid to remember. ", "error")

        elif command == "memalt":
            while True:
                output("Select a memory to alter: ", "menu")
                list_items(self.story.memory + ["(Finish)"], "menu")
                i = input_number(len(self.story.memory), default=-1)
                if i == len(self.story.memory):
                    break
                else:
                    self.story.memory[i] = alter_text(self.story.memory[i])
                    if self.story.memory[i] == 0:
                        del self.story.memory[i]

        elif command == "memswap":
            while True:
                output("Select two memories to swap: ", "menu")
                list_items(self.story.memory + ["(Finish)"], "menu")
                i = input_number(len(self.story.memory), default=-1)
                if i == len(self.story.memory):
                    break
                j = input_number(len(self.story.memory), default=-1)
                if j == len(self.story.memory):
                    break
                else:
                    self.story.memory[i], self.story.memory[j] = self.story.memory[j], self.story.memory[i]

        elif command == "forget":
            while True:
                output("Select a memory to forget: ", "menu")
                list_items(self.story.memory + ["(Finish)"], "menu")
                i = input_number(len(self.story.memory), default=-1)
                if i == len(self.story.memory):
                    break
                else:
                    del self.story.memory[i]

        elif command == "save":
            save_story(self.story)

        elif command == "load":
            story_file = select_file(Path("saves"), ".json")
            if story_file:
                tstory, tcontext, tprompt = load_story(story_file, self.generator)
                if tstory:
                    output("Loading story...", "message")
                    self.story = tstory
                    self.context = tcontext
                    self.prompt = tprompt
                    self.story.print_story()
                else:
                    self.story.print_last()
            else:
                self.story.print_last()

        elif command == "summarize":
            first_result = self.story.results[-1]
            output(self.story.context, "user-text", "(YOUR SUMMARY HERE)", "message")
            output(self.story.results[-1], "ai-text")
            new_prompt = input_line("Enter the summary for the new story: ", "query")
            new_prompt = new_prompt.strip()
            if len(new_prompt) == 0:
                output("Invalid new prompt; cancelling. ", "error")
                self.story.print_last()
                return False
            if input_bool("Do you want to save your previous story? (y/N): ", "query"):
                save_story(self.story)
            self.prompt = new_prompt
            self.story = new_story(self.generator, self.context, self.prompt, memory=self.story.memory,
                                   first_result=first_result)
            self.story.savefile = ""

        elif command == "altergen":
            result = alter_text(self.story.results[-1])
            self.story.results[-1] = ""
            output("Regenerating result...", "message")
            result += ' ' + self.story.act(result, record=False)
            self.story.results[-1] = result
            self.story.print_last()

        else:
            output("Invalid command: " + command, "error")
        return False

    def process_action(self, action, suggested_actions=[]) -> bool:
        """Process an action to be submitted to the AI."""
        action = format_input(action)

        story_insert_regex = re.search("^(?: *you +)?! *(.*)$", action, flags=re.I)

        # If the player enters a story insert.
        if story_insert_regex:
            action = story_insert_regex.group(1)
            if not action or len(action.strip()) == 0:
                output("Invalid story insert. ", "error")
                return False
            output(format_result(action), "user-text")

        # If the player enters a real action
        elif action != "":
            # Roll a die. We'll use it later if action-d20 is enabled.
            d = random.randint(1, 20)
            logger.debug("roll d20=%s", d)

            # Add the "you" if it's not prompt-toolkit
            if not use_ptoolkit():
                action = re.sub("^(?: *you +)*(.+)$", "You \\1", action, flags=re.I)

            sugg_action_regex = re.search(r"^(?: *you +)?([0-9]+)$", action, flags=re.I)
            user_speech_regex = re.search(r"^(?: *you +say +)?([\"'].*[\"'])$", action, flags=re.I)
            user_action_regex = re.search(r"^(?: *you +)(.+)$", action, flags=re.I)

            if sugg_action_regex:
                action = sugg_action_regex.group(1)
                if action in [str(i) for i in range(len(suggested_actions))]:
                    action = "You " + suggested_actions[int(action)].strip()

            elif user_speech_regex:
                action = user_speech_regex.group(1)
                if settings.getboolean("action-d20"):
                    action = d20ify_speech(action, d)
                else:
                    action = "You say " + action
                action = end_sentence(action)

            elif user_action_regex:
                action = first_to_second_person(user_action_regex.group(1))
                if settings.getboolean("action-d20"):
                    action = d20ify_action(action, d)
                else:
                    action = "You " + action
                action = end_sentence(action)

            # If the user enters nothing but leaves "you", treat it like an empty action (continue)
            if re.match(r"^(?: *you *)*[.?!]? *$", action, flags=re.I):
                action = ""
            else:
                # Prompt the user with the formatted action
                output("> " + format_result(action), "transformed-user-text")

        if action == "":
            output("Continuing...", "message")

        result = self.story.act(action)

        # Check for loops
        if self.story.is_looping():
            self.story.revert()
            output("That action caused the model to start looping. Try something else instead. ",
                   "error")

        pwon, pdied = player_won(result), player_died(result)
        # If the player won or died, ask them if they want to continue.
        if pwon or pdied:
            output(result, "ai-text")
            if pwon:
                output("YOU WON. CONGRATULATIONS", "message")
                list_items(["Start a New Game", "\"I'm not done yet!\" (If you still want to play)"])
            else:
                output("YOU DIED. GAME OVER", "message")
                list_items(["Start a New Game", "\"I'm not dead yet!\" (If you didn't actually die)"])
            choice = input_number(1)
            if choice == 0:
                return True
            else:
                output("Sorry about that...where were we?", "query")

        # Output the AI's result.
        output(result, "ai-text")

    def play_story(self):
        """The main in-game loop."""
        if not self.init_story():
            return

        while True:
            suggested_actions = []
            total_suggestions_wanted = settings.getint("action-sugg")
            
            if total_suggestions_wanted > 0:
                # --- New Keyword-Priority Suggestion Logic ---
                num_keyword_suggestions = settings.getint("keyword-sugg")

                # 1. Start with a single, random, high-priority inventory suggestion if available.
                inventory_suggestions = self.get_state_based_suggestions()
                if inventory_suggestions:
                    suggested_actions.append(random.choice(inventory_suggestions))
                
                # 2. Add keyword-based suggestions up to the specified limit.
                if len(suggested_actions) < num_keyword_suggestions:
                    last_result = self.story.results[-1].lower() if self.story.results else ""
                    present_keywords = [k for k in KEYWORD_ACTIONS if k in last_result]
                    
                    # Shuffle to ensure variety
                    random.shuffle(present_keywords) 
                    
                    for keyword in present_keywords:
                        keyword_actions = KEYWORD_ACTIONS[keyword][:] # Make a copy
                        random.shuffle(keyword_actions)
                        for action in keyword_actions:
                            if action not in suggested_actions:
                                suggested_actions.append(action)
                            if len(suggested_actions) >= num_keyword_suggestions:
                                break
                        if len(suggested_actions) >= num_keyword_suggestions:
                            break
                
                # 3. Use the LLM to generate the rest of the suggestions to meet the total quota.
                num_ai_suggestions = total_suggestions_wanted - len(suggested_actions)
                if num_ai_suggestions > 0:
                    for _ in range(num_ai_suggestions):
                        new_suggestion = self.story.get_suggestion(previous_suggestions=suggested_actions)
                        if new_suggestion and new_suggestion not in suggested_actions:
                            suggested_actions.append(new_suggestion)

                # 4. Ensure the final list is unique and has the correct length.
                suggested_actions = list(dict.fromkeys(suggested_actions))[:total_suggestions_wanted]

                if suggested_actions:
                    output("Suggested actions:", "selection-value")
                    for i, suggestion in enumerate(suggested_actions):
                        output(f"{i}) {suggestion}", "selection-value")
            
            bell()
            
            action = input_line("\n> ", "main-prompt", default="You ")

            cmd_regex = re.search(r"^(?: *you *)?\/([^ ]+) *(.*)$", action, flags=re.I)

            if cmd_regex:
                if self.process_command(cmd_regex):
                    return
            else:
                if self.process_action(action, suggested_actions):
                    return

            if settings.getboolean("autosave"):
                save_story(self.story, file_override=self.story.savefile, autosave=True)