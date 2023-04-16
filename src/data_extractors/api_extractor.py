import json
from httpx import AsyncClient
from src.constants import POKEMON_API_URL


class AsyncPokemonRestApiConsumer:

    def __init__(self, pokemon_name: str):
        self._pokemon_name = pokemon_name
        self.api_result = None

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
        self.api_result = json.loads(resp.read())
