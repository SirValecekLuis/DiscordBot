"""This file serves as OOP handling for Mongo DB to ensure more security and fewer risks when handling DB"""
from datetime import datetime
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
            # Variables is a single document and should be expanded, don't add more documents, only UPDATE!
            self.__variables: pymongo.collection.Collection = self.__db.Variables
            # For reminder messages
            self.__reminder_messages: pymongo.collection.Collection = self.__db.ReminderMessages

            count = self.__variables.count_documents({})
            if count == 0:  # If the document does not exist in a variable collection, I will create a new one
                self.__variables.insert_one({"voice_channel_id": 0})  # USE UPDATE_ONE AFTER THIS
                # self.__variables.update_one()...
            elif count != 1:  # Something went wrong in the code somewhere, only 1 document allowed
                raise InvalidVariablesCount("V kolekci Variables je povolena pouze 1 stránka, která se rozšiřuje.")
        except Exception as e:
            raise Exception("Nastala chyba v databázi. " + str(e)) from e

    @property
    def counter(self) -> pymongo.collection.Collection:
        """
        Returns counter-collection to work with.
        :return: Pymongo collection
        """
        return self.__counter

    @property
    def voice_channel_id(self) -> Optional[int]:
        """
        This returns ID of voice-channel that was set in DB.
        :return: None or int
        """
        return self.__variables.find_one()["voice_channel_id"]

    @voice_channel_id.setter
    def voice_channel_id(self, value) -> None:
        """
        Throws TypeError if incorrect value is tried to be set otherwise voice_channel_id will be update in DB
        :param value: INT number of voice_channel_id
        :return: None
        """
        if isinstance(value, int):
            self.__variables.update_one({}, {"$set": {"voice_channel_id": value}})
        else:
            raise TypeError("voice_channel_id must be type int.")

    async def find_user_from_database(self, user_id: int) -> Optional[dict]:
        """
        Function is supposed to find a user from a database based on ID and return a record from DB else None
        :param user_id: ID of discord member
        :return: None if no record is found else record (dictionary)
        """

        return self.__counter.find_one({"id": user_id})

    async def insert_or_update_into_variables(self, name: str, value: object) -> None:
        """
        Function will insert variable with name and value in a variable collection in MongoDB.
        The type control should not be done in this function.
        :param name: String for variable name
        :param value: Value which can be of many types.
        :return: None
        """
        self.__variables.update_one({}, {"$set": {name: value}})

    async def get_variable_from_variables(self, name: str) -> Optional[object]:
        """
        Function will try to get value from a database of given name.
        None when doesn't exist.
        :param name: Name of variable in DB
        :return: Variable value or None
        """
        try:
            return self.__variables.find_one()[name]
        except KeyError:
            return None

    async def insert_reminder(self, user_id: int, date: datetime, reminder_text: str) -> None:
        """
        Inserts reminder in a database.
        :param user_id: ID of user
        :param date: Date of reminder
        :param reminder_text: Text to remind
        :return: None
        """
        self.__reminder_messages.insert_one({"user_id": user_id, "date": date, "text": reminder_text})

    # async def remove_reminder(self, user_id: int, date: datetime, reminder_text: str) -> bool:
    #     ...

    async def get_reminders(self, user_id: int) -> list:
        """
        Returns list of reminders based on user id.
        :param user_id: ID of a user
        :return: list
        """
        return list(self.__reminder_messages.find({"user_id": user_id}))

    async def get_all_variables_names(self) -> list:
        """
        This function will return all the names from variables collection.
        :return: List
        """

        dict_variables = list(self.__variables.find())[0]  # Why the fuck there is no way to directly make it dict

        return list(dict_variables.keys())[1:]


class InvalidVariablesCount(Exception):
    """
    Basic exception to know there is something wrong in a variable collection that is supposed to be
    only one page that will be expanded.
    """

    def __init__(self, err_message):
        super().__init__(err_message)
