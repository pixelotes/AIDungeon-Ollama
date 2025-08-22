# aidungeon/charactersheet.py
from .utils import output

class CharacterSheet:
    """Holds and manages character stats and inventory."""
    def __init__(self):
        self.stats = {
            "Strength": 10,
            "Dexterity": 10,
            "Intelligence": 10,
            "Sanity": 100,
        }
        self.inventory = []

    def add_item(self, item_name):
        """Adds an item to the inventory if it's not already there."""
        item_name = item_name.strip().lower()
        if item_name not in self.inventory:
            self.inventory.append(item_name)
            output(f"[Acquired: {item_name.title()}]", "message")

    def remove_item(self, item_name):
        """Removes an item from the inventory."""
        item_name = item_name.strip().lower()
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            output(f"[Dropped: {item_name.title()}]", "message")
            return True
        output(f"You don't have '{item_name.title()}' to drop.", "error")
        return False

    def has_item(self, item_name):
        """Checks if an item (or a partial string of it) is in the inventory."""
        item_name = item_name.strip().lower()
        for item in self.inventory:
            if item_name in item:
                return True
        return False
        
    def display(self):
        """Prints the formatted character sheet to the console."""
        output("--- Character Sheet ---", "title", beg="\n")
        output("Stats:", "subtitle")
        for stat, value in self.stats.items():
            output(f"  {stat}: {value}", "menu")
        
        output("\nInventory:", "subtitle")
        if not self.inventory:
            output("  - Empty -", "menu")
        else:
            for item in sorted(self.inventory):
                output(f"  - {item.title()}", "menu")
        output("-----------------------", "title", end="\n")

    def to_dict(self):
        """Converts the character sheet to a dictionary for saving."""
        return {
            "stats": self.stats,
            "inventory": self.inventory,
        }

    def from_dict(self, data):
        """Loads the character sheet from a dictionary."""
        self.stats = data.get("stats", self.stats)
        self.inventory = data.get("inventory", [])