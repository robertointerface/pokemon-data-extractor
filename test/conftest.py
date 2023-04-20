import random
from unittest.mock import AsyncMock
from typing import Dict
import asyncio
import pytest
from pytest_mock import mocker
from httpx import AsyncClient
import json
from collections import abc
from pathlib import Path

from data_savers.json_file_saver import JsonFileSaver
from job_status import PokemonJob
from queue_workers import JobQueue

TEST_DATA_PATH = Path(__file__).parent / 'test_data'
POKEMONS_TO_TEST = ['mewtwo', 'charmander', 'gengar',
                    'lapras', 'pikachu']

POKEMON_TO_TEST_ONE_WRONG = ['mewtwo', 'non-existing', 'gengar',
                             'lapras', 'pikachu']


def mock_httpx_response(response_status_code: int, response_json: Dict=None):
    """Mock an httpx response.

    Args:
        response_status_code: http response status
        response_json: json response
    """
    class MockedResponse:
        def __init__(self, status_code: int, response: dict = None):
            self._status_code = status_code
            self._response = response

        def json(self):
            return self._response

        @property
        def status_code(self):
            return self._status_code

        def read(self):
            return json.dumps(self._response).encode('utf-8')

        def set_json(self, json_response):
            if isinstance(json_response, str):
                self._response = json.loads(json_response)
            elif isinstance(json_response, abc.MutableMapping):
                self._response = json_response
            else:
                msg = f'json response must be of type json or dictionary and not' \
                      f' of type {type(json_response)}'
                raise TypeError(msg)

    return MockedResponse(response_status_code, response_json)


@pytest.fixture
def rest_api_200_json_response():
    json_data = TEST_DATA_PATH / 'rest_api_200_response.json'
    return json.loads(json_data.read_text())


@pytest.fixture
def mock_success_httpx_response(rest_api_200_json_response):
    """Mock an async http call that returns a successful response"""
    httpx_response = mock_httpx_response(200,
                                         response_json=rest_api_200_json_response)
    httpx_mocked = AsyncMock(return_value=httpx_response)
    return httpx_mocked


@pytest.fixture
def mock_failure_httpx_response():
    """Mock an async http call that returns a failed response"""
    wrong_response = {'data': 'Darkroom_is_blocked_and_we_can_not_release_:)'}
    httpx_response = mock_httpx_response(400, response_json=wrong_response)
    # for failures need to include those attributes on response
    httpx_response.__dict__['content'] = 'ERROR DOOM'
    httpx_response.__dict__['errors'] = 'SUPER ERRORS DOOM'
    httpx_mocked = AsyncMock(return_value=httpx_response)
    return httpx_mocked


@pytest.fixture(name='mock_AsyncClient_get')
def mock_AsyncClient_returns_pokemon_data_correctly(mocker,
                                                    mock_success_httpx_response):
    mocker.patch.object(AsyncClient,
                        'get',
                        side_effect=mock_success_httpx_response)

@pytest.fixture()
def mock_AsyncClient_returns_error(mocker,
                                   mock_failure_httpx_response):
    mocker.patch.object(AsyncClient,
                        'get',
                        side_effect=mock_failure_httpx_response)

@pytest.fixture()
def mock_AsyncClient_returns_error_one_time(mocker,
                                            mock_failure_httpx_response,
                                            mock_success_httpx_response):
    random_failure = random.randint(0, len(POKEMONS_TO_TEST) - 1)
    side_effects_list = []
    for i in range(len(POKEMONS_TO_TEST)):
        # mock_failure_httpx_response and mock_success_httpx_response are
        # already AsyncMocks, we can not set a list of AsyncMocks as side_effect
        # To have multiple side effect values you need ONE single AsyncMock with
        # multiple side effects as below, that is why we take the 'return_value'
        # of mock_failure_httpx_response & mock_success_httpx_response
        if i == random_failure:
            side_effects_list.append(mock_failure_httpx_response.return_value)
        else:
            side_effects_list.append(mock_success_httpx_response.return_value)
    mocked = AsyncMock(side_effect=side_effects_list)
    mocker.patch.object(AsyncClient,
                        'get',
                        side_effect=mocked)


@pytest.fixture(name="job_list")
def mock_pokemon_jobs_list():
    return [PokemonJob(pokemon) for pokemon in POKEMONS_TO_TEST]


@pytest.fixture
def contaminated_job_list():
    return [PokemonJob(pokemon) for pokemon in POKEMON_TO_TEST_ONE_WRONG]


@pytest.fixture
def mock_JsonFileSaver_save_data_method(mocker):
    mocked = AsyncMock()
    mocker.patch.object(JsonFileSaver,
                        'save_data',
                        side_effect=mocked)
    return mocked


@pytest.fixture
async def mock_job_queue(job_list, rest_api_200_json_response):
    queue = asyncio.Queue()
    for job in job_list:
        job.set_pokemon_result(rest_api_200_json_response)
        job.set_job_status_extracted_data()
        await queue.put(job)
    return queue


@pytest.fixture
def job_queue(job_list):
    job_queue = JobQueue()
    [job_queue.enqueue(job) for job in job_list]
    return job_queue


@pytest.fixture(name='contaminated_job_queue')
def job_queue_with_one_failure(contaminated_job_list):
    job_queue = JobQueue()
    [job_queue.enqueue(job) for job in contaminated_job_list]
    return job_queue

