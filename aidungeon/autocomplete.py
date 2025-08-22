# aidungeon/autocomplete.py

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
import re
from .keywords import KEYWORD_ACTIONS, INVENTORY_SUGGESTIONS

class GameCompleter(Completer):
    """Custom completer for the AI Dungeon game."""
    
    def __init__(self, story=None):
        self.story = story
        self.commands = [
            '/revert', '/quit', '/menu', '/retry', '/restart', '/print', '/sheet',
            '/look', '/drop', '/alter', '/altergen', '/context', '/remember',
            '/memalt', '/memswap', '/roll', '/forget', '/save', '/load',
            '/summarize', '/generate', '/help', '/set', '/settings',
            # Add dice shortcuts as commands too
            '/d4', '/d6', '/d8', '/d10', '/d12', '/d20', '/d100'
        ]
        
        self.action_verbs = [
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
        
        self.dice_shortcuts = [
            'd4', 'd6', 'd8', 'd10', 'd12', 'd20', 'd100',
            '1d4', '1d6', '1d8', '1d10', '1d12', '1d20', '1d100',
            '2d6', '3d6', '4d6', '2d8', '3d8', '2d10', '2d12'
        ]

    def get_keywords(self):
        """Get contextual keywords based on the current story state."""
        keywords = set()
        
        # Add basic keywords
        keywords.update(KEYWORD_ACTIONS.keys())
        
        # Add inventory-based suggestions
        for trigger in INVENTORY_SUGGESTIONS.keys():
            keywords.update(trigger.split())
        
        # Add character inventory items if story is available
        if self.story and hasattr(self.story, 'character') and self.story.character:
            try:
                keywords.update(self.story.character.inventory)
            except (AttributeError, TypeError):
                pass  # Inventory might not be a list/set
        
        # Add contextual keywords from recent story text
        if self.story and hasattr(self.story, 'results') and self.story.results:
            recent_text = ' '.join(self.story.results[-2:]).lower()
            # Extract nouns and important words from recent text
            words = re.findall(r'\b[a-zA-Z]{3,}\b', recent_text)
            keywords.update(words[:20])  # Limit to avoid too many suggestions
            
        return list(keywords)

    def get_completions(self, document, complete_event):
        """Generate completions based on the current input."""
        text = document.text
        word_before_cursor = document.get_word_before_cursor()
        
        # Command completion (starts with /)
        if text.startswith('/'):
            for cmd in self.commands:
                if cmd.startswith(text):
                    yield Completion(
                        cmd[len(text):],
                        display=cmd,
                        style='class:autocomplete'
                    )
                    
        # Dice roll completion
        elif text.startswith(('d', '1d', '2d', '3d', '4d')) or '/roll' in text:
            for dice in self.dice_shortcuts:
                if dice.startswith(word_before_cursor.lower()):
                    yield Completion(
                        dice[len(word_before_cursor):],
                        display=f"🎲 {dice}",
                        style='class:autocomplete'
                    )

        # Action verb completion
        else:
            # Complete action verbs at the start of input (after "you")
            clean_text = re.sub(r'^(you\s+)?', '', text.lower().strip())
            
            for verb in self.action_verbs:
                if verb.startswith(clean_text) or verb.startswith(word_before_cursor.lower()):
                    completion_text = verb
                    if not text.lower().startswith('you'):
                        completion_text = f"You {verb}"
                    
                    yield Completion(
                        completion_text[len(text):] if text.lower().startswith('you') else completion_text,
                        display=f"▶ {completion_text}",
                        style='class:autocomplete'
                    )
            
            # Complete with contextual keywords
            try:
                keywords = self.get_keywords()
                for keyword in keywords:
                    if keyword.lower().startswith(word_before_cursor.lower()) and len(word_before_cursor) >= 2:
                        yield Completion(
                            keyword[len(word_before_cursor):],
                            display=f"🔸 {keyword}",
                            style='class:autocomplete'
                        )
            except Exception:
                # If keyword generation fails, just continue without contextual suggestions
                pass


# Enhanced input function with autocomplete support
def input_line_with_autocomplete(prompt_text, col1="default", default="", completer=None):
    """Enhanced input_line with autocomplete support."""
    from .utils import use_ptoolkit, ptcolors, input_line
    
    if use_ptoolkit() and ptcolors['displaymethod'] == "prompt-toolkit":
        try:
            from prompt_toolkit.shortcuts import CompleteStyle
            from prompt_toolkit.styles import Style
            from prompt_toolkit import prompt as ptprompt
            from prompt_toolkit.formatted_text import to_formatted_text
            from prompt_toolkit.key_binding import KeyBindings
            
            # Create custom key bindings
            kb = KeyBindings()
            
            @kb.add('enter')
            def _(event):
                """Handle Enter key - complete if menu is showing, otherwise accept input."""
                buffer = event.app.current_buffer
                
                # If there's a completion menu visible and something is selected
                if buffer.complete_state and buffer.complete_state.completions:
                    # Apply the current completion
                    buffer.apply_completion(buffer.complete_state.current_completion)
                else:
                    # No completion menu or nothing selected, accept the line
                    buffer.validate_and_handle()
            
            @kb.add('tab')
            def _(event):
                """Handle Tab key - show completions or cycle through them."""
                buffer = event.app.current_buffer
                if buffer.complete_state:
                    buffer.complete_next()
                else:
                    buffer.start_completion()
            
            @kb.add('s-tab')  # Shift+Tab
            def _(event):
                """Handle Shift+Tab - cycle backwards through completions."""
                buffer = event.app.current_buffer
                if buffer.complete_state:
                    buffer.complete_previous()
            
            style = Style.from_dict({
                'completion-menu.completion': 'bg:#87ceeb fg:black',
                'completion-menu.completion.current': 'bg:#005f87 fg:white bold',
                'scrollbar.background': 'bg:#88aaaa',
                'scrollbar.button': 'bg:#222222',
                'autocomplete': 'fg:#888888',  # Style for autocomplete suggestions
            })
            
            col1_style = ptcolors[col1] if col1 and ptcolors[col1] else ""
            
            val = ptprompt(
                to_formatted_text(prompt_text, col1_style),
                default=default,
                completer=completer,
                complete_style=CompleteStyle.MULTI_COLUMN,
                style=style,
                complete_while_typing=True,
                key_bindings=kb  # Add our custom key bindings
            )
        except ImportError:
            # Fallback if prompt_toolkit components are missing
            val = input_line(prompt_text, col1, default)
    else:
        # Fallback to original input_line for non-prompt_toolkit
        val = input_line(prompt_text, col1, default)
    
    return val