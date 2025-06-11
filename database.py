"""This file serves as OOP handling for Mongo DB to ensure more security and fewer risks when handling DB"""
from typing import Optional, Any, Mapping

import pymongo.collection
from pymongo import MongoClient

DB_NAME = "DiscordBot"


class Database:
    """This class is handling database connection and is middle man between discord bot and our database."""

    def __init__(self, uri: str):
        try:
            self.__client = MongoClient(uri)
            self.__db = self.__client[DB_NAME]

            # For countering some things from discord user messages
            self.__counter: pymongo.collection.Collection = self.__db.Counter
            # Variables is a SINGLE DOCUMENT and should be EXPANDED, DON'T ADD MORE DOCUMENTS, only UPDATE!
            self.__variables: pymongo.collection.Collection = self.__db.Variables
            # For reminder messages
            self.__reminder_messages: pymongo.collection.Collection = self.__db.ReminderMessages

            self.collections = {"counter": self.__counter,
                                "variables": self.__variables,
                                "reminder_messages": self.__reminder_messages
                                }

            count = self.__variables.count_documents({})
            if count == 0:  # If the document does not exist in a variable collection, I will create a new one
                self.__variables.insert_one({"voice_channel_id": 0})  # USE UPDATE_ONE ON VARIABLES ONLY!
                # self.__variables.update_one()...
            elif count != 1:  # Something went wrong in the code somewhere, only 1 document allowed
                raise InvalidVariablesCount("V kolekci Variables je povolena pouze 1 stránka, která se rozšiřuje.")
        except Exception as e:
            raise Exception("Nastala chyba v databázi. " + str(e)) from e

    async def __get_collection_from_str(self, collection_name: str) -> pymongo.collection.Collection:
        """
        Returns collection based on string name, returns exception if not found.

        :param collection_name: string name of collection based on self.collections
        :return: pymongo.collection.Collection
        """

        collection: pymongo.collection.Collection = self.collections.get(collection_name)

        if collection is None:
            raise Exception(f"Kolekce {collection_name} nebyla nalezena v self.collections.")

        return collection

    async def insert_one(self, collection_name: str, data: dict) -> None:
        """
        Inserts one document into the collection.

        :param collection_name: string name of collection based on self.collections
        :param data: data to be inserted for example {"user_id": id, "test": "haha", ...}
        """

        if collection_name == "variables":
            raise Exception("Kolekce 'variables' je určena pouze pro update_one a ne insert_one.")

        collection = await self.__get_collection_from_str(collection_name)
        collection.insert_one(data)

    async def update_one(self, collection_name: str, filter_dict: dict, update: dict) -> None:
        """
        Updates one document in the collection based on the filter dictionary.

        :param collection_name: string name of collection based on self.collections
        :param filter_dict: dictionary with filter parameters, {} updates the first one, good for variables collection.
        :param update: dictionary with update parameters name: {value, name2: value2, ...} is the way to go.
        """

        collection = await self.__get_collection_from_str(collection_name)
        collection.update_one(filter_dict, {"$set": update})

    async def find_one(self, collection_name: str, filter_dict: dict, keyword="") -> Mapping[str, Any] | None | Any:
        """
        This returns one document from a collection based on filter dictionary.

        :param collection_name: string name of collection based on self.collections
        :param filter_dict: dictionary with filter parameters, {} if variables collection
        :param keyword: string keyword to search for a specific value from returned document
        """

        collection = await self.__get_collection_from_str(collection_name)
        result = collection.find_one(filter_dict)

        if result is None:
            return None

        if keyword != "":
            return result.get(keyword)

        return result

    async def find(self, collection_name: str, filter_dict: Optional[dict] = None,
                   sort_dict: Optional[dict] = None) -> list[dict]:
        """
        This will return all documents from a collection.

        :param collection_name: string name of collection based on self.collections
        :param filter_dict: dictionary with filter parameters for find return
        :param sort_dict: dictionary with sort parameters for find return
        :return: a list of dicts with documents as dicts
        """

        if filter_dict is None:
            filter_dict = {}

        if sort_dict is None:
            sort_dict = {}

        collection = await self.__get_collection_from_str(collection_name)

        if filter_dict != {} and sort_dict == {}:
            result = list(collection.find(filter_dict))
        elif sort_dict != {}:
            result = list(collection.find(filter_dict, sort_dict))
        else:
            result = list(collection.find())

        return result


class InvalidVariablesCount(Exception):
    """
    Basic exception to know there is something wrong in a variable collection that is supposed to be
    only one page that will be expanded.
    """

    def __init__(self, err_message):
        super().__init__(err_message)
