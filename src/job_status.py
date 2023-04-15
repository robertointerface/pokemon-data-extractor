from dataclasses import dataclass


@dataclass
class JobResult:
    pokemon_data: dict




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

    @property
    def pokemon_name(self):
        return self.__pokemon_name
