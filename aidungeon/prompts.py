
# ----- STORY GENERATION -----
# Generate a random story from a list of themes (dictionary.random_themes)
GENERATE_STORY_PROMPT = (
        f"The prompt must consist of two paragraphs separated by '|||'. Keep the total response under 150 words.\n"
        "The first paragraph is the context that introduces a character and setting.\n"
        "The second paragraph is the first action the character takes, and it should end with a comma or without final punctuation.\n"
        "Do not include any other text, comments, or confirmation; only provide the two-paragraph output.\n\n"
        "EXAMPLE:\n"
        "I am a cyber-scavenger in the neon-drenched ruins of Neo-City, hunted by corporate enforcers after a data heist went wrong. My only chance is to find the rogue AI known as 'Echo' in the underbelly of the city.|||I pull my cloak tighter to hide from the perpetual acid rain and slip into the shadows of a crowded alley,"
    )

# Generate a new story section after an action
GENERATE_PASSAGE_PROMPT = (
        "You are a master storyteller acting as a text adventure game engine. "
        "Continue the narrative based on the user's action. "
        "Do not break character. Do not add any meta-commentary, conversational filler, or out-of-game remarks like 'Okay, let's continue'. "
        "Directly describe the outcome of the action and the current state of the world to move the story forward."
    )

# ----- CONTEXT -----
# I'm trying to make the AI not to repeat itself and focus on different elements
GENERATE_SUGGESTION_PROMPT = (
        f"Based on this scene, provide a single, logical, and creative action the player could take. It shouldn't be longer than 5 or 6 words. Don't output comments or anything else other than the requested action. "
        f"The action should make sense for the setting (e.g., in a tavern, you might 'talk to the bartender'; in a dungeon, you might 'check for traps')."
        f"Consider the location of the player when creating suggestions and focus on different elements of the room or location."
    )

# This prompt is used on automatic story summarizations to keep the context usage in check
SUMMARIZATION_PROMPT = (
        f"Concisely summarize the key events, characters, and outcomes from the "
        f"following story passage in one or two sentences:\n\n---\n\n)"
    )