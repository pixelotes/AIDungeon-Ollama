# aidungeon/autocomplete.py

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
import re
from .dictionary import KEYWORD_ACTIONS, INVENTORY_SUGGESTIONS
from .dictionary import palette_commands, palette_action_verbs, palette_dice_shortcuts

class GameCompleter(Completer):
    """Custom completer for the AI Dungeon game."""
    
    def __init__(self, story=None):
        self.story = story
        self.commands = palette_commands   
        self.action_verbs = palette_action_verbs      
        self.dice_shortcuts = palette_dice_shortcuts

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
            # Get the word we're trying to complete
            if word_before_cursor:
                # Complete individual words within the input
                for verb in self.action_verbs:
                    if verb.lower().startswith(word_before_cursor.lower()):
                        # Replace the partial word with the complete verb
                        yield Completion(
                            verb[len(word_before_cursor):],
                            display=f"▶ You {verb}",
                            style='class:autocomplete'
                        )
                        
                # Complete with contextual keywords
                try:
                    keywords = self.get_keywords()
                    for keyword in keywords:
                        if (keyword.lower().startswith(word_before_cursor.lower()) and 
                            len(word_before_cursor) >= 2 and
                            keyword.lower() not in [v.lower() for v in self.action_verbs]):  # Avoid duplicates
                            yield Completion(
                                keyword[len(word_before_cursor):],
                                display=f"🔸 {keyword}",
                                style='class:autocomplete'
                            )
                except Exception:
                    # If keyword generation fails, just continue without contextual suggestions
                    pass
            else:
                # If no partial word, suggest starting with "You " followed by verbs
                for verb in self.action_verbs[:10]:  # Limit to first 10 to avoid overwhelming
                    if not text.lower().startswith('you'):
                        yield Completion(
                            f"You {verb}",
                            display=f"▶ You {verb}",
                            style='class:autocomplete'
                        )


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
                
                # If there's a completion menu visible with completions
                if (buffer.complete_state and 
                    buffer.complete_state.completions and 
                    buffer.complete_state.current_completion is not None):
                    # Apply the current completion and close the menu
                    buffer.apply_completion(buffer.complete_state.current_completion)
                    buffer.cancel_completion()
                else:
                    # No completion menu or nothing selected, accept the line
                    buffer.validate_and_handle()
            
            @kb.add('tab')
            def _(event):
                """Handle Tab key - apply current completion or start completion."""
                buffer = event.app.current_buffer
                if buffer.complete_state and buffer.complete_state.current_completion is not None:
                    # Apply the currently highlighted completion and close menu
                    buffer.apply_completion(buffer.complete_state.current_completion)
                    buffer.cancel_completion()
                else:
                    # Start completion if none active
                    buffer.start_completion()
            
            @kb.add('c-n')  # Ctrl+N - next completion
            def _(event):
                """Handle Ctrl+N - cycle to next completion."""
                buffer = event.app.current_buffer
                if buffer.complete_state:
                    buffer.complete_next()
                else:
                    buffer.start_completion()
            
            @kb.add('c-p')  # Ctrl+P - previous completion  
            def _(event):
                """Handle Ctrl+P - cycle to previous completion."""
                buffer = event.app.current_buffer
                if buffer.complete_state:
                    buffer.complete_previous()
                else:
                    buffer.start_completion()
                    
            @kb.add('down')  # Down arrow - next completion
            def _(event):
                """Handle Down arrow - cycle to next completion."""
                buffer = event.app.current_buffer
                if buffer.complete_state:
                    buffer.complete_next()
                    
            @kb.add('up')  # Up arrow - previous completion
            def _(event):
                """Handle Up arrow - cycle to previous completion."""
                buffer = event.app.current_buffer
                if buffer.complete_state:
                    buffer.complete_previous()
            
            @kb.add('escape')
            def _(event):
                """Handle Escape key - close completion menu."""
                buffer = event.app.current_buffer
                if buffer.complete_state:
                    buffer.cancel_completion()
                    
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