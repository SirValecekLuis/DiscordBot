"""This file serves as OOP handling for Mongo DB to ensure more security and fewer risks when handling DB"""
from typing import Optional

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

    async def find_one(self, collection_name: str, filter_dict: dict, keyword="") -> dict | None:
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

    async def find(self, collection_name: str, filter_dict=Optional[dict], sort_dict=Optional[dict]) -> list[dict]:
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

        if filter_dict is not None:
            result = list(collection.find(filter_dict))
        elif sort_dict is not None:
            result = list(collection.find(filter_dict, sort_dict))
        else:
            result = list(collection.find())

        return result

    # ---------------------------------------------------------------------------------------------------------------
    # @property
    # def voice_channel_id(self) -> Optional[int]:
    #     """
    #     This returns ID of voice-channel that was set in DB.
    #     :return: None or int
    #     """
    #     return self.__variables.find_one()["voice_channel_id"]
    #
    # @voice_channel_id.setter
    # def voice_channel_id(self, value) -> None:
    #     """
    #     Throws TypeError if incorrect value is tried to be set otherwise voice_channel_id will be update in DB
    #     :param value: INT number of voice_channel_id
    #     :return: None
    #     """
    #     if isinstance(value, int):
    #         self.__variables.update_one({}, {"$set": {"voice_channel_id": value}})
    #     else:
    #         raise TypeError("voice_channel_id must be type int.")
    #
    # async def find_user_from_database(self, user_id: int) -> Optional[dict]:
    #     """
    #     Function is supposed to find a user from a database based on ID and return a record from DB else None
    #     :param user_id: ID of discord member
    #     :return: None if no record is found else record (dictionary)
    #     """
    #
    #     return self.__counter.find_one({"id": user_id})
    #
    # async def insert_or_update_into_variables(self, name: str, value: object) -> None:
    #     """
    #     Function will insert variable with name and value in a variable collection in MongoDB.
    #     The type control should not be done in this function.
    #     :param name: String for variable name
    #     :param value: Value which can be of many types.
    #     :return: None
    #     """
    #     self.__variables.update_one({}, {"$set": {name: value}})
    #
    # async def get_variable_from_variables(self, name: str) -> Optional[object]:
    #     """
    #     Function will try to get value from a database of given name.
    #     None when doesn't exist.
    #     :param name: Name of variable in DB
    #     :return: Variable value or None
    #     """
    #     try:
    #         return self.__variables.find_one()[name]
    #     except KeyError:
    #         return None
    #
    # async def insert_reminder(self, user_id: int, date: datetime, reminder_text: str) -> None:
    #     """
    #     Inserts reminder in a database.
    #     :param user_id: ID of user
    #     :param date: Date of reminder
    #     :param reminder_text: Text to remind
    #     :return: None
    #     """
    #     self.__reminder_messages.insert_one({"user_id": user_id, "date": date, "text": reminder_text})
    #
    # async def get_all_variables_names(self) -> list:
    #     """
    #     This function will return all the names from variables collection.
    #     :return: List
    #     """
    #
    #     dict_variables = list(self.__variables.find())[0]  # Why the fuck there is no way to directly make it dict
    #
    #     return list(dict_variables.keys())[1:]


class InvalidVariablesCount(Exception):
    """
    Basic exception to know there is something wrong in a variable collection that is supposed to be
    only one page that will be expanded.
    """

    def __init__(self, err_message):
        super().__init__(err_message)
