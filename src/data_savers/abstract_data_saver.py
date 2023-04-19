from abc import ABC, abstractmethod
from collections.abc import MutableMapping


class AbstractDataSaver(ABC):

    @abstractmethod
    async def save_data(self, data: MutableMapping):
        pass