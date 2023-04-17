import json
from pathlib import Path
from aiofile import async_open
from collections.abc import MutableMapping


class JsonFileSaver:

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
        pokemon_name = data.get('name')
        if isinstance(data, MutableMapping):
            data = json.dumps(data)
        async with async_open(self.file_path / f'{pokemon_name}.json',
                              'w+') as async_fp:
            await async_fp.write(data)