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
    
    # API settings
    "api_base_url":     ["API endpoint URL.", "http://localhost:11434"],
    "api_key":          ["API key for the service.", "ollama"],
    "model":            ["Default model to use.", "llama2:7b"],
    "timeout":          ["Timeout for API requests in seconds.", 120],
}

def get_api_base_url():
    """Get API base URL from environment, falling back to settings."""
    return os.environ.get("API_BASE_URL", settings.get("api_base_url", "http://localhost:11434"))

def get_api_key():
    """Get API key from environment, falling back to settings."""
    return os.environ.get("API_KEY", settings.get("api_key", "ollama"))

def get_model():
    """Get model name from environment, falling back to settings."""
    return os.environ.get("MODEL", settings.get("model", "llama2:7b"))

def get_timeout():
    """Get timeout from environment, falling back to settings."""
    default_timeout = settings.getint("timeout", 120)
    return int(os.environ.get("TIMEOUT", default_timeout))

def get_action_suggestions():
    """Get the number of action suggestions from environment, falling back to settings."""
    default_suggestions = settings.getint("action-sugg", 2)
    return int(os.environ.get("ACTION_SUGGESTIONS", default_suggestions))

# Update the settings object with values that might come from environment variables
settings["api_base_url"] = get_api_base_url()
settings["api_key"] = get_api_key()
settings["model"] = get_model()
settings["timeout"] = str(get_timeout())
settings["action-sugg"] = str(get_action_suggestions())
