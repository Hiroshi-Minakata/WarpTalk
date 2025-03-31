from abc import ABC, abstractmethod
from typing import Any

class File(ABC):
    def __init__(self):
        self.path = ""

    @abstractmethod
    def write(self, data: Any) -> bool:
        pass

    @abstractmethod
    def read(self) -> Any | None:
        pass

class Dir(ABC):
    def __init__(self):
        self.path = ""

    @abstractmethod
    def create_file(self, name: str) -> File | None:
        pass

    @abstractmethod
    def get_file(self, name: str) -> File | None:
        pass

    @abstractmethod
    def delete_file(self, name: str) -> bool:
        pass

    def get_all_files(self) -> list[File] | None:
        raise NotImplementedError

class FileSys(ABC):
    @abstractmethod
    def create_dir(self, path: str) -> Dir | None:
        pass

    @abstractmethod
    def get_dir(self, path: str) -> Dir | None:
        pass

    @abstractmethod
    def delete_dir(self, path: str) -> bool:
        pass

    def get_all_dires(self) -> list[Dir] | None:
        raise NotImplementedError