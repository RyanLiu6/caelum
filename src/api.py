import csv
import logging

from typing import Dict
from notion_client import Client

from pprint import pprint

from src.config import NOTION_TOKEN, NOTION_DATABASE
from src.config import Tags, TAG_ICONS, TAG_FILTERS


class Expense:
    def __init__(self, **kwargs):
        """
        Constructor for the Expense class.

        When amount is positive (kwargs["amount"]), we don't process these transactions
        as they typically are usually payments towards the card. There are other occasions
        where this may happen, such as a refund or a credit. In that case, please manually
        add these transactions, which you can do so by inspecting the .db file generated
        and sorting by amount.

        Raises:
            ValueError: kwargs["amount"] was a positive number.
        """
        amount = float(kwargs["amount"])
        if amount > 0:
            raise ValueError

        self.name = kwargs["description"]
        self.amount = -1*amount
        self.date = kwargs["timestamp"]
        self.fi = kwargs["account_type"]
        self.tag = None
        self.icon = None

    def __repr__(self) -> str:
        return f"Name: {self.name} | Amount: {self.amount} | Date: {self.date} | FI: {self.fi} | Tag: {self.tag} | Icon: {self.icon}"

    def tag_expense(self, tag: Tags) -> None:
        self.tag = tag
        self.icon = TAG_ICONS[tag]

class Caelum:
    def __init__(self):
        self.client = Client(auth=NOTION_TOKEN)
        self.expense_database = self.client.databases.retrieve(database_id=NOTION_DATABASE)

        # pprint(self.expense_database)
        # pprint(self.client.databases.query(database_id=NOTION_DATABASE))

        self.expenses = []

        self.setup_properties()

    def setup_properties(self) -> None:
        """
        A bit of pre-processing here:
        1. Expect that we have the following properties inside the database:
            a. Card -> Which has Credit Cards based on your FI. When importing a CSV,
                please import different FI separately! When running the importer, please
                indicate your FI. If no property matches the FI, a new property will
                be created!

            b. Month -> January to December

            c. Tag -> Please refer to the tag_expense and setup_tags functions below
                for details on what tags are currently defined and how expenses are categorized!
        """
        properties = self.expense_database["properties"]
        # pprint(properties)

        self.cards = dict((cards["name"], cards["id"]) for cards in properties["Card"]["select"]["options"])
        self.months = dict((cards["name"], cards["id"]) for cards in properties["Month"]["select"]["options"])

        self.setup_tags(properties=properties)

    def setup_tags(self, properties: Dict) -> None:
        """
        Setup tagging system - we expect there to have:
            1. Recurring - Bills, rent, mortgage, car, loan, etc
            2. Groceries - Groceries
            3. Restaurants - Whether Delivery or Restaurant
            4. Games - Video, Board, Card, etc
            5. Shopping - All types of shopping. Can be fine-tuned for specifics
            6. Misc - everything else

        Args:
            properties (Dict): Database properties
        """
        self.tags = dict((cards["name"], cards["id"]) for cards in properties["Tag"]["select"]["options"])

        # Ensure all tags are represented
        to_create = {
            "Tag": properties["Tag"]
        }

        existing_keys = self.tags.keys()
        for tag in Tags.keys():
            if tag not in existing_keys:
                logging.info(f"{tag} did not exist - creating")
                to_create["Tag"]["select"]["options"].append({"color": "gray", "name": tag})

        self.client.databases.update(database_id=NOTION_DATABASE, properties=to_create)

    def tag_expense(self, expense: Expense) -> None:
        """
        Tags expenses with appropriate tag, as defined above.

        We go through the list of tags in the order as defined.

        Args:
            expense (Expense): the expense to tag
        """
        name = expense.name.lower()
        for tag, tf in TAG_FILTERS.items():
            for item in tf:
                if item in name:
                    expense.tag_expense(tag)
        pprint(expense)


    def parse_csv(self, csv_file: str) -> None:
        """
        CSV Headers are: id,account_type,timestamp,description,amount

        Args:
            csv_file (str): CSV file that contains transaction information
        """
        with open(csv_file, newline="") as to_read:
            reader = csv.DictReader(to_read)
            for row in reader:
                try:
                    self.expenses.append(Expense(**row))
                except ValueError:
                    logging.info(f"Transaction ID #{row['id']} has positive amount, \
                        considered as payment to card and not processed.")

        for expense in self.expenses:
            self.tag_expense(expense)


