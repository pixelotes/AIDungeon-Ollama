import json
import re
from .getconfig import settings, logger
from .utils import output, format_result, format_input, get_similarity
from .charactersheet import CharacterSheet


class Story:
    """
    Story manager adapted for Ollama backend.
    Main changes: simplified context management without tokenization.
    """
    
    def __init__(self, generator, context='', memory=None):
        if memory is None:
            memory = []
        self.generator = generator
        self.context = context
        self.memory = memory
        self.actions = []
        self.results = []
        self.savefile = ""
        self.character = CharacterSheet()
        # Constants for the summarization feature
        self.SUMMARIZE_THRESHOLD = 10
        self.STORY_CHUNK_SIZE = 8

    def find_and_update_inventory(self, text):
        """Parses text to find items acquired by the player."""
        match = re.search(r"you (?:pick up|take|acquire|get|find) (?:the|a|an) ([\w\s]+)", text, flags=re.I)
        if match:
            item_name = match.group(1).strip()
            item_name = item_name.split('.')[0].split(',')[0].strip()
            if item_name:
                self.character.add_item(item_name)

    def summarize_chunk(self):
        """Summarizes the oldest chunk of the story and prepends it to the context."""
        logger.info("Attempting to summarize story chunk...")
        chunk_actions = self.actions[:self.STORY_CHUNK_SIZE]
        chunk_results = self.results[:self.STORY_CHUNK_SIZE]
        story_chunk_text = "\n\n".join([val for pair in zip(chunk_actions, chunk_results) for val in pair])
        prompt = (
            "Concisely summarize the key events, characters, and outcomes from the "
            f"following story passage in one or two sentences:\n\n---\n\n{story_chunk_text}"
        )
        summary = self.generator.generate_raw(
            prompt,
            context="",
            temperature=0.5,
            generate_num=100,
        ).strip()
        if not summary:
            logger.warning("Failed to generate story summary. Skipping.")
            return
        separator = "\n" if self.context else ""
        self.context = f"{self.context}{separator}[Previously: {summary}]"
        self.actions = self.actions[self.STORY_CHUNK_SIZE:]
        self.results = self.results[self.STORY_CHUNK_SIZE:]
        logger.info("Story chunk summarized and pruned.")
        logger.debug(f"New context: {self.context}")

    def act(self, action, record=True, format=True):
        """Generate the next part of the story based on an action."""
        assert (self.context.strip() + action.strip())
        assert (settings.getint('top-keks') is not None)
        
        story_so_far = self.get_story()
        memory_context = ' '.join(self.memory)
        base_context = f"{self.context} {memory_context}".strip()

        # Add a system prompt to guide the AI's behavior for story generation
        instructions = (
            "You are a master storyteller acting as a text adventure game engine. "
            "Continue the narrative based on the user's action. "
            "Do not break character. Do not add any meta-commentary, conversational filler, or out-of-game remarks like 'Okay, let's continue'. "
            "Directly describe the outcome of the action and the current state of the world to move the story forward."
        )
        full_context = f"[System Prompt: {instructions}]\n\n{base_context}"
        
        result = self.generator.generate(
            story_so_far + action,
            full_context,
            temperature=settings.getfloat('temp'),
            top_p=settings.getfloat('top-p'),
            top_k=settings.getint('top-keks'),
            repetition_penalty=settings.getfloat('rep-pen'),
            repetition_penalty_range=settings.getint('rep-pen-range'),
            repetition_penalty_slope=settings.getfloat('rep-pen-slope')
        )
        
        self.find_and_update_inventory(result)
        if "!" in action:
            self.find_and_update_inventory(action)

        if record:
            self.actions.append(format_input(action))
            self.results.append(format_input(result))
            if len(self.actions) > self.SUMMARIZE_THRESHOLD:
                self.summarize_chunk()
        
        return format_result(result) if format else result

    def print_action_result(self, i, wrap=True, color=True):
        """Print a specific action-result pair."""
        col1 = 'user-text' if color else None
        col2 = 'ai-text' if color else None
        
        if i == 0 or len(self.actions) == 1:
            start = format_result(self.context + ' ' + self.actions[0])
            result = format_result(self.results[0])
            is_start_end = re.match(r"[.!?]\s*$", start)
            is_result_continue = re.match(r"^\s*[a-z.!?,\"]", result)
            sep = ' ' if not is_start_end and is_result_continue else '\n'
            
            if not self.actions[0]:
                output(self.context, col1, self.results[0], col2, sep=sep)
            else:
                output(self.context, col1)
                output(self.actions[0], col1, self.results[0], col2, sep=sep)
        else:
            if i < len(self.actions) and self.actions[i].strip() != "":
                caret = "> " if re.match(r"^ *you +", self.actions[i], flags=re.I) else ""
                output(format_result(caret + self.actions[i]), col1, wrap=wrap)
            if i < len(self.results) and self.results[i].strip() != "":
                output(format_result(self.results[i]), col2, wrap=wrap)

    def print_story(self, wrap=True, color=True):
        """Print the entire story."""
        for i in range(0, max(len(self.actions), len(self.results))):
            self.print_action_result(i, wrap=wrap, color=color)

    def print_last(self, wrap=True, color=True):
        """Print the last action-result pair."""
        self.print_action_result(-1, wrap=wrap, color=color)

    def get_story(self):
        """Get the story text as a single string."""
        lines = [val for pair in zip(self.actions, self.results) for val in pair]
        return '\n\n'.join(lines)

    def revert(self):
        """Remove the last action-result pair."""
        self.actions = self.actions[:-1]
        self.results = self.results[:-1]

    def get_suggestion(self, previous_suggestions=None):
        """Generate a creative, context-aware action."""
        story_so_far = self.get_story()
        
        exclusion_prompt = ""
        if previous_suggestions:
            exclusions = "\n".join(f"- {s}" for s in previous_suggestions)
            exclusion_prompt = f"\n\nTo ensure variety, do not suggest any of the following actions:\n{exclusions}"

        # MODIFIED: A much more direct and powerful prompt.
        suggestion_prompt = (
            f"Here is the current scene from a text adventure game:\n\n{story_so_far}\n\n"
            f"Based on this scene, provide a single, logical, and creative action the player could take. It shouldn't be longer than 5 or 6 words. Don't output comments or anything else other than the requested action. "
            f"The action should make sense for the setting (e.g., in a tavern, you might 'talk to the bartender'; in a dungeon, you might 'check for traps').{exclusion_prompt}"
        )
        
        suggestion = self.generator.generate_raw(
            suggestion_prompt,
            self.context,
            generate_num=15,
            temperature=settings.getfloat('action-temp'),
            top_p=settings.getfloat('top-p'),
            top_k=settings.getint('top-keks'),
            repetition_penalty=1.2,
            stop_tokens=["\n", "."]
        )
        
        suggestion = suggestion.strip().replace("You ", "", 1).lstrip(" >!.?")
        return suggestion if suggestion else None


    def __str__(self):
        return self.context + ' ' + self.get_story()

    def to_dict(self):
        """Convert story to dictionary for saving."""
        res = {}
        res["temp"] = settings.getfloat('temp')
        res["top-p"] = settings.getfloat("top-p")
        res["top-keks"] = settings.getint("top-keks")
        res["rep-pen"] = settings.getfloat("rep-pen")
        res["rep-pen-range"] = settings.getint("rep-pen-range")
        res["rep-pen-slope"] = settings.getfloat("rep-pen-slope")
        res["context"] = self.context
        res["memory"] = self.memory
        res["actions"] = self.actions
        res["results"] = self.results
        res["character_sheet"] = self.character.to_dict()
        if hasattr(self.generator, 'model_name'):
            res["model_name"] = self.generator.model_name
            res["ollama_host"] = self.generator.ollama_host
        return res

    def from_dict(self, d):
        """Load story from dictionary."""
        settings["temp"] = str(d["temp"])
        settings["top-p"] = str(d["top-p"])
        settings["top-keks"] = str(d["top-keks"])
        settings["rep-pen"] = str(d["rep-pen"])
        try:
            settings["rep-pen-range"] = str(d["rep-pen-range"])
            settings["rep-pen-slope"] = str(d["rep-pen-slope"])
        except KeyError:
            settings["rep-pen-range"] = "512"
            settings["rep-pen-slope"] = "3.33"
        
        self.context = d["context"]
        self.memory = d["memory"]
        self.actions = d["actions"]
        self.results = d["results"]
        if "character_sheet" in d:
            self.character.from_dict(d["character_sheet"])

    def to_json(self):
        """Convert story to JSON string."""
        return json.dumps(self.to_dict())

    def from_json(self, j):
        """Load story from JSON string."""
        self.from_dict(json.loads(j))

    def is_looping(self, threshold=0.9):
        """Check if the AI is generating repetitive content."""
        if len(self.results) >= 2:
            similarity = get_similarity(self.results[-1], self.results[-2])
            if similarity > threshold:
                return True
        return False