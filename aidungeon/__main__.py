#!/usr/bin/env python3
# main.py or aidungeon/__main__.py (updated for Ollama)

import sys
import os
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from aidungeon.getconfig import logger
from aidungeon.utils import output, clear_lines, use_ptoolkit, input_number, list_items
from aidungeon.ollamagenerator import get_generator
from aidungeon.play import GameManager

def main():
    """Main entry point for AI Dungeon Clover Edition (Ollama)."""
    
    # Welcome message
    output("=" * 60, "message")
    output("Welcome to AI Dungeon: Clover Edition (Ollama)", "message")
    output("=" * 60, "message")
    output("")
    
    # Check if Ollama is available
    try:
        import requests
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        response.raise_for_status()
    except Exception as e:
        output("Error: Cannot connect to Ollama server!", "error")
        output("Make sure Ollama is running with: ollama serve", "message")
        output(f"Connection details: {e}", "error")
        output("")
        output("To install Ollama:", "message")
        output("  1. Visit: https://ollama.ai", "message")
        output("  2. Download and install Ollama", "message")
        output("  3. Run: ollama serve", "message")
        output("  4. Pull a model: ollama pull llama2", "message")
        return 1
    
    # Initialize the generator
    try:
        generator = get_generator()
        output(f"Successfully connected to Ollama model: {generator.model_name}", "message")
        output("")
    except Exception as e:
        output(f"Failed to initialize Ollama generator: {e}", "error")
        return 1
    
    # Start the game loop
    game_manager = GameManager(generator)
    
    try:
        while True:
            game_manager.play_story()
            
            # After a story ends, ask if they want to play another
            output("")
            output("Thanks for playing!", "message")
            list_items([
                "Start Another Adventure",
                "Exit"
            ], "menu")
            
            choice = input_number(1)
            if choice == 1:  # Exit
                break
            # Otherwise continue the loop for another adventure
            
    except KeyboardInterrupt:
        output("\nGoodbye! Thanks for playing AI Dungeon!", "message")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        output(f"An unexpected error occurred: {e}", "error")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())