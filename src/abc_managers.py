from abc import ABC, abstractmethod


class AbcDataExtractorManager(ABC):

    @abstractmethod
    def get_job(self):
        pass

    @abstractmethod
    def keep_processing_density_jobs(self):
        pass

    @abstractmethod
    def process_work(self, client):
        pass
