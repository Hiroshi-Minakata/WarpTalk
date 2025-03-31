from typing import override
import logging

import google.auth
from google.oauth2.service_account import Credentials
import gspread
from gspread.exceptions import GSpreadException

from .file_sys import FileSys, Dir, File

class Worksheet(File):
    def __init__(self, worksheet: gspread.Worksheet):
        self.__ws = worksheet
        self.path = self.__ws.title

    @override
    def write(self, data: list[list]) -> bool:
        try:
            self.__ws.update(data)
            return True
        except GSpreadException as e:
            logging.exception(e)
            return False

    @override
    def read(self) -> list[list] | None:
        try:
            return self.__ws.get_all_values()
        except GSpreadException as e:
            logging.exception(e)
            return None

class Spreadsheet(Dir):
    def __init__(self, spreadsheet: gspread.Spreadsheet):
        self.__ss = spreadsheet
        self.path = self.__ss.url

    @override
    def create_file(self, title: str, rows = 1000, cols = 26) -> Worksheet | None:
        try:
            ws = self.__ss.add_worksheet(title, rows, cols)
            return Worksheet(ws)
        except GSpreadException as e:
            logging.exception(e)
            return None

    @override
    def get_file(self, title: str) -> Worksheet | None:
        try:
            return Worksheet(self.__get(title))
        except GSpreadException as e:
            logging.exception(e)
            return None

    @override
    def delete_file(self, title: str) -> bool:
        try:
            self.__ss.del_worksheet(self.__get(title))
            return True
        except GSpreadException as e:
            logging.exception(e)
            return False

    def __get(self, title: str) -> gspread.Worksheet:
        return self.__ss.worksheet(title)

class GSpread(FileSys):
    def __init__(self, cert: str | None = None):
        """
        Args:
            cert (str | None): 
                - str: JSON file path.
                - None: default auth.
        """

        # 認証
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        cred = Credentials.from_service_account_file(cert, scopes=scopes) if cert else google.auth.default(scopes)[0]
        self.__client = gspread.authorize(cred)

    @override
    def create_dir(self, title: str) -> Spreadsheet | None:
        try:
            return Spreadsheet(self.__client.create(title))
        except GSpreadException as e:
            logging.exception(e)
            return None

    @override
    def get_dir(self, url: str) -> Spreadsheet | None:
        try:
            return Spreadsheet(self.__get(url))
        except GSpreadException as e:
            logging.exception(e)
            return None

    @override
    def delete_dir(self, url: str) -> bool:
        try:
            file_id = self.__get(url).id
            self.__client.del_spreadsheet(file_id)
            return True
        except GSpreadException as e:
            logging.exception(e)
            return False
        
    def __get(self, url: str) -> gspread.Spreadsheet:
        return self.__client.open_by_url(url)