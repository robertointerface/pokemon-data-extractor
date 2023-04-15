from src.constants import POKEMON_API_URL


class AsyncPokemonApiExtractor:

    def __init__(self, pokemon_name: str):
        self._pokemon_name = pokemon_name
        self.api_result = None

    def build_api_call(self) -> str:
        return f'{POKEMON_API_URL}/{self._pokemon_name}'

    async def get_pokemon_data(self):
        pass

