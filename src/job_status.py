from dataclasses import dataclass
from typing import Dict


@dataclass
class JobResult:
    """Store pokemon rest api response"""
    pokemon_data: dict




@dataclass
class PipelineStatus:
    """Over all pipeline status, monitor the pipeline status to keep track
    which steps have started, finished and the workers on each step."""
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
    """Over all pokemon job status"""
    extracted_data: bool = False
    saved_data: bool = False
    finished: bool = False
    failed: bool = False
    pokemon_data: bool = None


class PokemonJob:
    """PokemonJob instances are the objects that get passed between steps by
    the queues, in the instance we keep the job status (if it failed on one step
    or what steps finished....), we also save the api result"""
    def __init__(self, pokemon_name: str):
        self.__pokemon_name = pokemon_name
        self._job_status = JobStatus()
        self._job_result = None

    @property
    def pokemon_name(self):
        """Get the pokemon name related to the job"""
        return self.__pokemon_name

    def set_pokemon_result(self, pokemon_data: dict):
        """Save the result form the api.

        Args:
            pokemon_data: pokemon data form Rest API
        """
        self._job_result = JobResult(pokemon_data=pokemon_data)

    def get_job_result(self) -> JobResult:
        """Get the job result"""
        return self._job_result

    def get_job_status(self) -> JobStatus:
        """Get the job status flags"""
        return self._job_status

    def set_job_status_extracted_data(self):
        """Set the job status flag extracted_data"""
        self._job_status.extracted_data = True

    def set_job_status_saved_data(self):
        """Set the job status flag saved_data"""
        self._job_status.saved_data = True

    def set_job_failed(self):
        """Set the job status flag failed"""
        self._job_status.failed = True

    def has_job_failed(self) -> bool:
        """Answer if the job has failed or not.

        If the job failed on any of the steps it should have set the flag
            failed= True

        Returns: if the job has failed or not.
        """
        return self._job_status.failed