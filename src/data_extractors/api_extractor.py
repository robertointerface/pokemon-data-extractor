import json
from httpx import AsyncClient
from src.constants import POKEMON_API_URL
from httpx._status_codes import codes

from src.exceptions import PokemonNotFoundError


class AsyncPokemonRestApiConsumer:
    """Get pokemon data from the Rest API"""
    def __init__(self, pokemon_name: str):
        self._pokemon_name = pokemon_name.lower()
        self.api_result = None
        self.api_error = None

    def build_api_call(self) -> str:
        """Build the https url used to call the Rest API.

        Returns: String with the https
        """
        return f'{POKEMON_API_URL}/{self._pokemon_name}'

    @property
    def result(self) -> dict:
        """get the api result"""
        if self.api_result is None:
            raise ValueError("pokemon result was not extracted yet")
        return self.api_result

    async def get_pokemon_data(self, client: 'AsyncClient'):
        """Get pokemon data from rest API.

        Call pokemon rest api with the provided pokomen name on attribute
            "_pokemon_name".

        Args:
            client: httpx async client used to make http request

        Raises:
            PokemonNotFoundError if the Rest API returned non 2xx code.
        """
        resp = await client.get(self.build_api_call(),
                                timeout=6.1,
                                follow_redirects=True)
        if not codes.is_success(resp.status_code):
            raise PokemonNotFoundError(f'Pokemon with name = {self._pokemon_name} '
                                       f'not found')
        self.api_result = json.loads(resp.read())
