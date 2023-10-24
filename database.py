"""This file serves as OOP handling for Mongo DB to ensure more security and fewer risks when handling DB"""
import pymongo.collection
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional


class Database:
    def __init__(self, uri: str):
        self.__client = MongoClient(uri)
        self.__db = self.__client["DiscordBot"]
        self.__object_id = ObjectId("65345b94b4bd2ccc95f22d4f")
        self.__counter = self.__db.Counter

    @property
    def counter(self) -> pymongo.collection.Collection:
        return self.__counter

    @property
    def voice_channel_id(self) -> Optional[int]:
        return self.__db.Variables.find_one({"_id": self.__object_id})["voice_channel_id"]

    @voice_channel_id.setter
    def voice_channel_id(self, value) -> None:
        """
        Throws TypeError if incorrect value is tried to be set otherwise voice_channel_id will be update in DB
        :param value: INT number of voice_channel_id
        :return: None
        """
        if isinstance(value, int):
            self.__db.Variables.update_one({"_id": self.__object_id}, {"$set": {"voice_channel_id": value}})
        else:
            raise TypeError("voice_channel_id must be type int.")

    async def find_user_from_database(self, user_id: int) -> Optional[dict]:
        """
        Function is supposed to find user from database based on ID and return a record from DB else None
        :param user_id: ID of discord member
        :return: None if no record is found else record (dictionary)
        """

        return self.__counter.find_one({"id": user_id})
