from typing import override
import logging

import firebase_admin
from firebase_admin import firestore, credentials
from google.cloud.firestore import CollectionReference, DocumentReference
from google.cloud.exceptions import GoogleCloudError

from .file_sys import FileSys, Dir, File

class Document(File):
    def __init__(self, document: DocumentReference):
        self.__ref = document
        self.path = self.__ref.path
    
    @override
    def write(self, data: dict) -> bool:
        try:
            self.__ref.set(data, merge=True)
            return True
        except GoogleCloudError as e:
            logging.exception(e)
            return False
        
    @override
    def read(self) -> dict | None:
        try:
            return self.__ref.get().to_dict()
        except GoogleCloudError as e:
            logging.exception(e)
            return None

class Collection(Dir):
    def __init__(self, collection: CollectionReference):
        self.__ref = collection
        self.path = self.__ref.id

    @override
    def create_file(self, document_id: str) -> Document | None:
        try:
            doc = self.__get(document_id)
            doc.set({})
            return Document(doc)
        except GoogleCloudError as e:
            logging.exception(e)
            return None

    @override
    def get_file(self, document_id: str) -> Document | None:
        try:
            doc = self.__get(document_id)
            return Document(doc)
        except GoogleCloudError as e:
            logging.exception(e)
            return None

    @override
    def delete_file(self, document_id: str) -> bool:
        try:
            doc = self.__get(document_id)
            doc.delete()
            return True
        except GoogleCloudError as e:
            logging.exception(e)
            return False

    def __get(self, document_id: str) -> DocumentReference:
        return self.__ref.document(document_id)

class Firebase(FileSys):
    def __init__(self, cert: str | dict | None = None):
        """
        Args:
            cert (str | None): 
                - str: JSON file path.
                - dict: JSON data.
                - None: default auth.
        """

        # 存在確認
        if not firebase_admin._apps:
            # 認証（certがNoneのときは自動的にデフォルト認証）
            cred = credentials.Certificate(cert) if cert else None
            firebase_admin.initialize_app(cred)

        # クライアント
        self.__client = firestore.client()
    
    @override
    def create_dir(self, collection_path: str) -> Collection | None:
        """
        Create directory and create dummy document.
        Firestore does not allow empty collections, so a "_dummy" document is created.
        """
        try:
            col = self.__get(collection_path)
            dummy_doc: DocumentReference = col.document("_dummy")
            dummy_doc.set({})
            return Collection(col)
        except GoogleCloudError as e:
            logging.exception(e)
            return None

    @override
    def get_dir(self, collection_path: str) -> Collection | None:
        try:
            col = self.__get(collection_path)
            return Collection(col)
        except GoogleCloudError as e:
            logging.exception(e)
            return None

    @override
    def delete_dir(self, collection_path: str) -> bool:
        """Delete all document in directory."""
        try:
            col = self.__get(collection_path)
            self.__client.recursive_delete(col)
            return True
        except GoogleCloudError as e:
            logging.exception(e)
            return False
        
    def __get(self, collection_path: str) -> CollectionReference:
        return self.__client.collection(collection_path)