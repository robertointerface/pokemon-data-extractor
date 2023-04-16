from dataclasses import dataclass
from src.constants import POKEMON_API_URL


@dataclass
class JobResult:
    pokemon_data: dict


@dataclass
class PipelineStatus:
    pokemon_data_extractor_started = False
    pokemon_data_extractor_finished = False
    pokemon_data_saver_started = False
    pokemon_data_saver_finished = False
    error_handling_started = False
    error_handling_finished = False

    def set_pokemon_data_extractor_starter(self):
        if not self.pokemon_data_extractor_started:
            self.pokemon_data_extractor_started = True

    def set_pokemon_data_extractor_finished(self):
        if not self.pokemon_data_extractor_finished:
            self.pokemon_data_extractor_finished = True

    def set_pokemon_data_saver_started_started(self):
        if not self.pokemon_data_saver_started:
            self.pokemon_data_saver_started = True

    def set_pokemon_data_saver_finished(self):
        if not self.pokemon_data_saver_finished:
            self.pokemon_data_saver_finished = True


class JobStatus:

    def __init__(self):
        self.extracted_data = False
        self.saved_data = False
        self.finished = False
        self.failed = False
        self.pokemon_data = None


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

    def get_job_status(self):
        return self._job_status
