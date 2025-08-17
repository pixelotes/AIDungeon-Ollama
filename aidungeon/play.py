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
KEYWORD_ACTIONS = {
    "door": ["Try to open the door", "Knock on the door", "Listen at the door", "Examine the door"],
    "chest": ["Try to open the chest", "Look for a key for the chest", "Examine the chest"],
    "key": ["Pick up the key", "Try using the key"],
    "enemy": ["Attack the enemy", "Try to sneak past the enemy", "Attempt to talk to the enemy"],
    "creature": ["Attack the creature", "Observe the creature from a distance"],
    "sword": ["Pick up the sword", "Inspect the sword"],
    "book": ["Read the book", "Skim through the book", "Look for a title on the book's spine"],
    "note": ["Read the note", "Pick up the note"],
    "light": ["Approach the light", "Investigate the source of the light"],
    "path": ["Follow the path", "Examine the path for tracks"],
}

# Dictionary for inventory-based conditional suggestions
INVENTORY_SUGGESTIONS = {
    "locked door": { "item": "key", "action": "Try to unlock the door with the key"},
    "locked chest": { "item": "key", "action": "Try to unlock the chest with the key"},
    "darkness": { "item": "torch", "action": "Light your torch"},
    "dark room": { "item": "lantern", "action": "Light your lantern"},
    "tangled vines": { "item": "machete", "action": "Cut through the vines with your machete"},
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

        command_was_run = False

        while True:
            act_alts = settings.getint("action-sugg")
            suggested_actions = []
            action_suggestion_lines = 0
            
            if act_alts > 0 and not command_was_run:
                # Get state-based (contextual and inventory) suggestions
                state_suggestions = self.get_state_based_suggestions()
                
                # Get AI-generated suggestions, making them aware of previous ones
                ai_suggestions = []
                num_ai_to_gen = act_alts - len(state_suggestions)
                if num_ai_to_gen > 0:
                    for _ in range(num_ai_to_gen):
                        # Combine all current suggestions to avoid generating duplicates
                        current_suggestions_for_prompt = state_suggestions + ai_suggestions
                        new_suggestion = self.story.get_suggestion(previous_suggestions=current_suggestions_for_prompt)
                        if new_suggestion.strip():
                            ai_suggestions.append(new_suggestion)
                
                # Combine and display
                combined_suggestions = state_suggestions + ai_suggestions
                unique_suggestions = list(dict.fromkeys(combined_suggestions))
                suggested_actions = unique_suggestions[:act_alts]

                if suggested_actions:
                    action_suggestion_lines += output("Suggested actions:", "selection-value")
                    for i, suggestion in enumerate(suggested_actions):
                        line = "{}) {}".format(i, suggestion)
                        action_suggestion_lines += \
                            output(line, "selection-value", beg='' if i != 0 else None)
            
            command_was_run = False

            bell()
            print()

            if use_ptoolkit():
                action = input_line("> ", "main-prompt", default="%s" % "You ")
            else:
                action = input_line("> You ", "main-prompt")

            if settings.getboolean("clear-suggestions") and action_suggestion_lines > 0 and not in_colab():
                # The +2 accounts for the blank line from print() and the user's input line
                clear_lines(action_suggestion_lines + 2)

            cmd_regex = re.search(r"^(?: *you *)?/([^ ]+) *(.*)$", action, flags=re.I)

            if cmd_regex:
                command_was_run = True
                if self.process_command(cmd_regex):
                    return
            else:
                if self.process_action(action, suggested_actions):
                    return

            if settings.getboolean("autosave"):
                save_story(self.story, file_override=self.story.savefile, autosave=True)