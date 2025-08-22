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
from .dictionary import KEYWORD_ACTIONS, INVENTORY_SUGGESTIONS
from .autocomplete import GameCompleter, input_line_with_autocomplete
from .prompts import GENERATE_STORY_PROMPT
from .dictionary import adjective_action_d01, adjective_action_d20, adjectives_say_d01, adjectives_say_d20, random_themes

def roll_dice(dice_notation):
    """
    Parse dice notation and return results.
    Supports formats like: 1d20, 3d6, 2d10+5, 1d6-1, d20 (assumes 1d20)
    
    Returns a dictionary with:
    - 'total': final sum
    - 'rolls': list of individual dice results
    - 'modifier': any bonus/penalty applied
    - 'notation': the original notation
    """
    # Clean the input
    dice_notation = dice_notation.strip().lower().replace(" ", "")
    
    # Handle shorthand notation (d20 -> 1d20)
    if dice_notation.startswith('d'):
        dice_notation = '1' + dice_notation
    
    # Parse the dice notation with regex
    pattern = r'^(\d+)d(\d+)([+-]\d+)?$'
    match = re.match(pattern, dice_notation)
    
    if not match:
        return {
            'error': f"Invalid dice notation: {dice_notation}",
            'notation': dice_notation,
            'total': 0,
            'rolls': [],
            'modifier': 0
        }
    
    num_dice = int(match.group(1))
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    # Sanity checks
    if num_dice > 100:
        return {
            'error': "Too many dice! Maximum is 100.",
            'notation': dice_notation,
            'total': 0,
            'rolls': [],
            'modifier': modifier
        }
    
    if die_size < 2 or die_size > 1000:
        return {
            'error': "Invalid die size! Must be between 2 and 1000.",
            'notation': dice_notation,
            'total': 0,
            'rolls': [],
            'modifier': modifier
        }
    
    # Roll the dice!
    rolls = [random.randint(1, die_size) for _ in range(num_dice)]
    total = sum(rolls) + modifier
    
    return {
        'notation': dice_notation,
        'total': total,
        'rolls': rolls,
        'modifier': modifier,
        'num_dice': num_dice,
        'die_size': die_size
    }

def format_dice_result(result):
    """Format dice roll results for display."""
    if 'error' in result:
        return f"❌ {result['error']}"
    
    notation = result['notation'].upper()
    rolls = result['rolls']
    modifier = result['modifier']
    total = result['total']
    
    # Format individual rolls
    if len(rolls) == 1:
        roll_text = str(rolls[0])
    else:
        roll_text = f"[{', '.join(map(str, rolls))}]"
    
    # Add modifier text
    modifier_text = ""
    if modifier > 0:
        modifier_text = f" + {modifier}"
    elif modifier < 0:
        modifier_text = f" - {abs(modifier)}"
    
    # Special cases for critical hits/fails on d20
    critical_text = ""
    if result['die_size'] == 20 and len(rolls) == 1:
        if rolls[0] == 20:
            critical_text = " 🎯 CRITICAL!"
        elif rolls[0] == 1:
            critical_text = " 💥 FUMBLE!"
    
    return f"🎲 {notation}: {roll_text}{modifier_text} = **{total}**{critical_text}"


def generate_random_prompt(generator):
    """Uses the AI to generate a random story prompt."""
    output("\nGenerating a random story from the AI...", "loading-message")
    chosen_theme = random.choice(random_themes)

    full_prompt_text = generator.generate_raw(
        f"You are a creative assistant. Generate a random story prompt for a text-based adventure game with a '{chosen_theme}' theme.\n" + GENERATE_STORY_PROMPT,
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
    """Interactive settings configuration menu with autocomplete support."""
    all_settings = list(setting_info.keys())
    
    # Create a simple completer for settings
    from prompt_toolkit.completion import WordCompleter
    settings_completer = WordCompleter(all_settings, ignore_case=True)
    
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
            
            # Use autocomplete for setting value input if possible
            if use_ptoolkit():
                new_value = input_line_with_autocomplete(
                    "Enter the new value: ", 
                    "query",
                    completer=settings_completer if key in ['true', 'false', 'on', 'off'] else None
                )
            else:
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
        self.skip_suggestion_regeneration = False
        self.hide_suggestions_for_next_prompt = False
        self.last_suggestions = []
        self.completer = None

    def _initialize_completer(self):
        """Initialize the GameCompleter with the current story."""
        self.completer = GameCompleter(story=self.story)

    def _display_prompt_and_get_action(self, suggestions):
        """Displays suggestions and the input prompt, then returns the user's action."""
        # Use the 'suggestions' argument passed to the function
        if suggestions and not self.hide_suggestions_for_next_prompt:
            suggestions_text = "".join([f"\n{i}) {s}" for i, s in enumerate(suggestions)])
            output("Suggested actions: \n" + suggestions_text, "selection-value")
        
        bell()
        
        # Use autocomplete-enabled input if available
        if self.completer and use_ptoolkit():
            return input_line_with_autocomplete("\n> ", "main-prompt", default="You ", completer=self.completer)
        else:
            return input_line("\n> ", "main-prompt", default="You ")
    

    def regenerate_suggestions(self):
        """Generates a new set of suggestions and stores them in self.last_suggestions."""
        total_suggestions_wanted = settings.getint("action-sugg")
        suggested_actions = []

        if total_suggestions_wanted > 0:
            num_keyword_suggestions = settings.getint("keyword-sugg")
            inventory_suggestions = self.get_state_based_suggestions()
            if inventory_suggestions:
                suggested_actions.append(random.choice(inventory_suggestions))

            if len(suggested_actions) < num_keyword_suggestions:
                last_result = self.story.results[-1].lower() if self.story.results else ""
                present_keywords = [k for k in KEYWORD_ACTIONS if k in last_result]
                random.shuffle(present_keywords)

                for keyword in present_keywords:
                    keyword_actions = KEYWORD_ACTIONS[keyword][:]
                    random.shuffle(keyword_actions)
                    for action in keyword_actions:
                        if action not in suggested_actions:
                            suggested_actions.append(action)
                        if len(suggested_actions) >= num_keyword_suggestions:
                            break
                    if len(suggested_actions) >= num_keyword_suggestions:
                        break


            num_ai_suggestions = total_suggestions_wanted - len(suggested_actions)
            if num_ai_suggestions > 0:
                for _ in range(num_ai_suggestions):
                    new_suggestion = self.story.get_suggestion(previous_suggestions=suggested_actions)
                    if new_suggestion and new_suggestion not in suggested_actions:
                        suggested_actions.append(new_suggestion)

            self.last_suggestions = list(dict.fromkeys(suggested_actions))[:total_suggestions_wanted]
        else:
            self.last_suggestions = []

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

        # Initialize the autocomplete completer after story is created
        self._initialize_completer()

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

        elif command == "generate":
            self.process_action("", [])
            return False

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

        # Add /roll command for D&D-style gameplay
        elif command == "roll":
            if not args:
                # Default to d20 if no dice specified
                dice_notation = "1d20"
            else:
                dice_notation = args[0]
            
            self.skip_suggestion_regeneration = True
            self.hide_suggestions_for_next_prompt = True
            result = roll_dice(dice_notation)
            formatted_result = format_dice_result(result)
            output(formatted_result, "message")
            
            # Optional: Add the roll result to the story context for dramatic effect
            if 'error' not in result and settings.getboolean("dice-in-story", fallback=False):
                roll_action = f"You roll {result['notation'].upper()} and get {result['total']}"
                self.story.act(roll_action, record=True)

        # Dice shortcuts. Use "/roll" for rolling multiple dice.
        elif command in ["d4", "d6", "d8", "d10", "d12", "d20", "d100"]:
            die_size = command[1:]  # Remove the 'd'
            result = roll_dice(f"1d{die_size}")
            formatted_result = format_dice_result(result)
            output(formatted_result, "message")
            self.skip_suggestion_regeneration = True
            self.hide_suggestions_for_next_prompt = True

        elif command == "suggest":
            self.regenerate_suggestions()
            self.story.print_last()
            # The main game loop will now handle displaying the suggestions.
            self.skip_suggestion_regeneration = True
            self.hide_suggestions_for_next_prompt = False
            return False

        elif command in ["look", "recall"]:
            self.story.print_last()
            if self.last_suggestions:
                # Use the same formatting as _display_prompt_and_get_action
                suggestions_text = "".join([f"\n{i}) {s}" for i, s in enumerate(self.last_suggestions)])
                output("Suggested actions:\n" + suggestions_text, "selection-value")
            else:
                output("No suggestions to display.", "message")
            self.skip_suggestion_regeneration = True
            self.hide_suggestions_for_next_prompt = True

        elif command in ["quit", "exit"]:
            if input_bool("Do you want to save? (y/N): ", "query"):
                save_story(self.story)
            exit()

        elif command == "help":
            instructions()
            self.skip_suggestion_regeneration = True

        elif command in ["sheet", "char", "inventory"]:
            self.story.character.display()
            #self.story.print_last()
            self.skip_suggestion_regeneration = True
            self.hide_suggestions_for_next_prompt = True

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
            #else:
                # Prompt the user with the formatted action
                #output("> " + format_result(action), "transformed-user-text")

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
            # Generate suggestions if not skipped
            if not self.skip_suggestion_regeneration:
                self.regenerate_suggestions()

            # Reset the flag after checking it
            self.skip_suggestion_regeneration = False

            # Get user input
            action = self._display_prompt_and_get_action(self.last_suggestions)

            # Process user input
            cmd_regex = re.search(r"^(?: *you *)?\/([^ ]+) *(.*)$", action, flags=re.I)

            if cmd_regex:
                if self.process_command(cmd_regex):
                    return  # Exit game loop if command returns True
            else:
                if self.process_action(action, self.last_suggestions):
                    return  # Exit game loop if action returns True

            if settings.getboolean("autosave"):
                save_story(self.story, file_override=self.story.savefile, autosave=True)