from abc import ABC, abstractmethod


class AbcJobProcessorManager(ABC):

    @abstractmethod
    def get_job(self):
        pass

    @abstractmethod
    def keep_processing_jobs(self):
        pass

    @abstractmethod
    def process_work(self, client):
        pass
