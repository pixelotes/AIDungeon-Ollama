import json
import re
from .getconfig import settings
from .utils import output, format_result, format_input, get_similarity


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

    def act(self, action, record=True, format=True):
        """Generate the next part of the story based on an action."""
        assert (self.context.strip() + action.strip())
        assert (settings.getint('top-keks') is not None)
        
        # Build the story context for generation
        story_so_far = self.get_story()
        memory_context = ' '.join(self.memory)
        full_context = f"{self.context} {memory_context}".strip()
        
        # Generate the result
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
        
        if record:
            self.actions.append(format_input(action))
            self.results.append(format_input(result))
        
        return format_result(result) if format else result

    def print_action_result(self, i, wrap=True, color=True):
        """Print a specific action-result pair."""
        col1 = 'user-text' if color else None
        col2 = 'ai-text' if color else None
        
        if i == 0 or len(self.actions) == 1:
            start = format_result(self.context + ' ' + self.actions[0])
            result = format_result(self.results[0])
            is_start_end = re.match(r"[.!?]\s*$", start)  # if start ends logically
            is_result_continue = re.match(r"^\s*[a-z.!?,\"]", result)  # if result is a continuation
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

    def get_suggestion(self):
        """Generate a suggested action."""
        # Use a different temperature for action suggestions
        suggestion_prompt = self.get_story() + "\n\n> You"
        
        suggestion = self.generator.generate_raw(
            suggestion_prompt,
            self.context,
            temperature=settings.getfloat('action-temp'),
            top_p=settings.getfloat('top-p'),
            top_k=settings.getint('top-keks'),
            repetition_penalty=1.0  # Lower repetition penalty for more variety in suggestions
        )
        
        # Clean up the suggestion
        suggestion = re.sub('\n.*', '', suggestion)  # Take only first line
        suggestion = suggestion.strip()
        
        # Remove "You " prefix if present since it will be added later
        suggestion = re.sub(r'^You\s+', '', suggestion, flags=re.I)
        
        return suggestion

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
        # Add generator info for Ollama
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
        
        # Note: Model info is saved but generator needs to be set up separately

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