import json
from httpx import AsyncClient
from src.constants import POKEMON_API_URL
from httpx._status_codes import codes

from src.exceptions import PokemonNotFoundError


class AsyncPokemonRestApiConsumer:

    def __init__(self, pokemon_name: str):
        self._pokemon_name = pokemon_name.lower()
        self.api_result = None
        self.api_error = None

    def build_api_call(self) -> str:
        return f'{POKEMON_API_URL}/{self._pokemon_name}'

    @property
    def result(self) -> dict:
        if self.api_result is None:
            raise ValueError("pokemon result was not extracted yet")
        return self.api_result

    async def get_pokemon_data(self, client: 'AsyncClient' = None):
        resp = await client.get(self.build_api_call(),
                                timeout=6.1,
                                follow_redirects=True)
        if not codes.is_success(resp.status_code):
            raise PokemonNotFoundError(f'Pokemon with name = {self._pokemon_name} '
                                       f'not found')
        self.api_result = json.loads(resp.read())
