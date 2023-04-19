import json
from pathlib import Path
from aiofile import async_open
from collections.abc import MutableMapping
from data_savers.abstract_data_saver import AbstractDataSaver


class JsonFileSaver(AbstractDataSaver):
    """
    Save data in a json file
    """
    def __init__(self, file_path: Path):
        self.file_path = file_path

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        if not isinstance(value, Path):
            raise ValueError(f'Provided file_path in class {self.__class__.__name__} '
                             f'must be of type {type(Path)}')
        self._file_path = value

    async def save_data(self, data: MutableMapping):
        """Save data returned from pokemon API on a json file. The name
            of the file will <pokemon_name>.json, files are saved on the
            specified path when initialising this class.

        Args:
            data: Data in dictionary format.
        """
        pokemon_name = data.get('name')
        if isinstance(data, MutableMapping):
            data = json.dumps(data)
        async with async_open(self.file_path / f'{pokemon_name}.json',
                              'w+') as async_fp:
            await async_fp.write(data)