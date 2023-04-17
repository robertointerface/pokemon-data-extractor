from asyncio import Queue as asyncQueue
from abc import ABC, abstractmethod
import logging

logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.WARNING)


class HandleErrorAbstract(ABC):

    @abstractmethod
    def handle_error(self):
        pass

    @abstractmethod
    def raise_error_if_specified(self):
        pass


class LogErrors(HandleErrorAbstract):

    def __init__(self, receive_queue: asyncQueue):
        self._receive_queue = receive_queue
        self._errors = []

    def set_pipeline_status(self, pipeline_status):
        self.pipeline_status = pipeline_status

    def keep_processing_work(self):
        return (not self._receive_queue.empty()
                or
                not self.pipeline_status.pokemon_data_saver_finished)

    async def handle_error(self):
        self.pipeline_status.set_error_handling_started()
        while self.keep_processing_work():
            current_job = await self._receive_queue.get()
            if current_job.has_job_failed():
                msg = f'Failed to extract data from pokemon = {current_job.pokemon_name}'
                logging.error(msg)
        self.pipeline_status.set_error_handling_finished()

    def raise_error_if_specified(self):
        pass