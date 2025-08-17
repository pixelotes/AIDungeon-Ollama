import configparser
import logging
import os

config = configparser.ConfigParser()
config.read("config.ini")
settings = config["Settings"]

colorschemefile = settings["color-scheme"]
colorconfig = configparser.ConfigParser()
colorconfig.read(colorschemefile)
ptcolors = colorconfig["Colors"]

colorschemefile = settings["backup-color-scheme"]
colorconfig = configparser.ConfigParser()
colorconfig.read(colorschemefile)
colors = colorconfig["Colors"]

logger = logging.getLogger(__name__)
logLevel = settings.getint("log-level")
oneLevelUp = 20

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logLevel + oneLevelUp,
)
logger.setLevel(logLevel)

"""
Settings descriptions and their default values keyed by their name.
These settings appear in the settings menu and the /help prompt.
Updated for Ollama backend.
"""
setting_info = {
    "temp":             ["Higher values make the AI more random.", 0.4],
    "rep-pen":          ["Controls how repetitive the AI is allowed to be.", 1.2],
    "rep-pen-range":    ["Controls how many tokens are affected by the penalty.", 512],
    "rep-pen-slope":    ["Controls the penalty curve slope.", 3.33],
    "text-wrap-width":  ["Maximum width of lines printed by computer.", 80],
    "console-bell":     ["Beep after AI generates text.", "on"],
    "top-keks":         ["Number of words the AI can randomly choose.", 20],
    "action-sugg":      ["How many actions to generate; 0 is off.", 4],
    "action-d20":       ["Makes actions difficult.", "on"],
    "action-temp":      ["How random the suggested actions are.", 1],
    "prompt-toolkit":   ["Whether or not to use the prompt_toolkit library.", "on"],
    "autosave":         ["Whether or not to save after every action.", "on"],
    "generate-num":     ["Approximate number of tokens to generate.", 60],
    "top-p":            ["Changes nucleus sampling threshold.", 0.9],
    "log-level":        ["Development log level. <30 is for developers.", 30],
    "clear-suggestions":["Clears the suggestion list after you make a choice.", "on"],
    # Ollama-specific settings
    "ollama-host":      ["Ollama server URL.", "http://localhost:11434"],
    "ollama-model":     ["Default Ollama model to use.", "llama2:7b"],
    "ollama-timeout":   ["Timeout for Ollama requests in seconds.", 120],
}

# Add Ollama-specific environment variable support
def get_ollama_host():
    """Get Ollama host from settings or environment."""
    return os.environ.get("OLLAMA_HOST", settings.get("ollama-host", "http://localhost:11434"))

def get_ollama_model():
    """Get Ollama model from environment, falling back to settings."""
    return os.environ.get("OLLAMA_MODEL", settings.get("ollama-model", "llama2:7b"))

def get_ollama_timeout():
    """Get Ollama timeout from environment, falling back to settings."""
    default_timeout = settings.getint("ollama-timeout", 120)
    return int(os.environ.get("OLLAMA_TIMEOUT", default_timeout))

def get_action_suggestions():
    """Get the number of action suggestions from environment, falling back to settings."""
    default_suggestions = settings.getint("action-sugg", 2)
    return int(os.environ.get("ACTION_SUGGESTIONS", default_suggestions))

# Update the settings object with values that might come from environment variables
# This ensures consistency when the settings are displayed in the /help menu
settings["ollama-host"] = get_ollama_host()
settings["ollama-model"] = get_ollama_model()
settings["ollama-timeout"] = str(get_ollama_timeout())
settings["action-sugg"] = str(get_action_suggestions())
