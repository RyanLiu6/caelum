from enum import Enum

from dotenv import dotenv_values


config = dotenv_values(".env")

NOTION_TOKEN = config["NOTION_TOKEN"]
NOTION_DATABASE = config["NOTION_DATABASE"]

class Tags(Enum):
    @classmethod
    def keys(cls):
        return list(map(lambda c: c.value, cls))

    RECURRING = "Recurring"
    GROCERIES = "Groceries"
    RESTAURANTS = "Restaurants"
    GAMES = "Games"
    SHOPPING = "Shopping"
    MISC = "Misc"

TAG_ICONS = {
    Tags.RECURRING: "💵",
    Tags.GROCERIES: "🥦",
    Tags.RESTAURANTS: "🍜",
    Tags.GAMES: "🎮",
    Tags.SHOPPING: "🛍",
    Tags.MISC: "⭐️",
}

TAG_FILTERS = {
    Tags.RECURRING: ["amazon web services", "apple.com/bill", "bitwarden", "proton", "insurance"],
    Tags.GROCERIES: ["supermarket", "wholesale", "superstore"],
    Tags.RESTAURANTS: ["ubereats", "uber* eats", "restaurant", "resta", "bar", "grill", "cuisine",
        "kitchen", "eatery", "liquor", "coffee", "starbucks", "cafe", "tea", "sushi", "bbq"],
    Tags.GAMES: ["games", "game", "steam"],
    Tags.SHOPPING: ["amazon.ca", "mec"],
}
