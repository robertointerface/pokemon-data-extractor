from dataclasses import dataclass
from typing import List, Dict

from src.constants import POKEMON_API_URL


@dataclass
class JobResult:
    pokemon_data: dict


@dataclass
class ProcessStatus:
    process_id: str
    active: False


@dataclass
class PipelineStatus:
    pokemon_data_extractor_started: bool = False
    pokemon_data_extractor_finished: bool = False
    pokemon_data_saver_started: bool = False
    pokemon_data_saver_finished: bool = False
    error_handling_started: bool = False
    error_handling_finished: bool = False
    pokemon_extractor_workers: Dict = None
    pokemon_saver_workers: Dict = None
    error_handling_workers: Dict = None

    def set_pokemon_data_extractor_starter(self):
        self.pokemon_data_extractor_started = True

    def set_pokemon_data_extractor_finished(self):
        self.pokemon_data_extractor_finished = True

    def set_pokemon_data_saver_started_started(self):
        self.pokemon_data_saver_started = True

    def set_pokemon_data_saver_finished(self):
        self.pokemon_data_saver_finished = True

    def set_error_handling_started(self):
        self.error_handling_started = True

    def set_error_handling_finished(self):
        self.error_handling_finished = True



@dataclass
class JobStatus:
    extracted_data: bool = False
    saved_data: bool = False
    finished: bool = False
    failed: bool = False
    pokemon_data: bool = None


class PokemonJob:

    def __init__(self, pokemon_name: str):
        self.__pokemon_name = pokemon_name
        self._job_status = JobStatus()
        self._job_result = None

    @property
    def pokemon_name(self):
        return self.__pokemon_name

    @property
    def pokemon_rest_api_url(self):
        return

    def set_pokemon_result(self, pokemon_data: dict):
        self._job_result = JobResult(pokemon_data=pokemon_data)

    def get_job_result(self):
        return self._job_result

    def get_job_status(self):
        return self._job_status

    def set_job_status_extracted_data(self):
        self._job_status.extracted_data = True

    def set_job_status_saved_data(self):
        self._job_status.saved_data = True

    def set_job_failed(self):
        self._job_status.failed = True

    def has_job_failed(self):
        return self._job_status.failed