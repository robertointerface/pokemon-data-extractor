"""Test class AsyncPokemonRestApiConsumer"""
import pytest
from pytest_mock import mocker
from httpx import AsyncClient
from data_extractors.api_extractor import AsyncPokemonRestApiConsumer
from constants import POKEMON_API_URL
from collections import abc

from exceptions import PokemonNotFoundError


@pytest.mark.unit
class TestAsyncPokemonApiExtractor:

    POKEMON_NAME = 'pikachu'

    def test_property_build_api_call_returns_correct_value(self):
        api_consumer = AsyncPokemonRestApiConsumer(self.POKEMON_NAME)
        rest_api_url = api_consumer.build_api_call()
        expected_api_url = f'{POKEMON_API_URL}/{self.POKEMON_NAME}'
        assert rest_api_url == expected_api_url

    async def test_get_pokemon_data_method_async_client_is_awaited(self,
                                                                   mock_AsyncClient_get):
        api_consumer = AsyncPokemonRestApiConsumer(self.POKEMON_NAME)
        async with AsyncClient() as client:
            await api_consumer.get_pokemon_data(client)
            assert isinstance(api_consumer.api_result, abc.MutableMapping)

    async def test_PokemonNotFoundError_is_raised_if_rest_api_returns_non_2xx_response(self,
                                                                      mock_AsyncClient_returns_error):
        api_consumer =AsyncPokemonRestApiConsumer('non-existing')
        with pytest.raises(PokemonNotFoundError):
            async with AsyncClient() as client:
                await api_consumer.get_pokemon_data(client)
