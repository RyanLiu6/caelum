from dotenv import dotenv_values


config = dotenv_values(".env")
NOTION_TOKEN = config["NOTION_TOKEN"]
