import uuid
import asyncio
from abc import ABC, abstractmethod
import logging

logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.WARNING)


class HandleErrorAbstract(ABC):
    """Abstract class for error handling"""
    @abstractmethod
    def handle_error(self):
        pass

    @abstractmethod
    def raise_error_if_specified(self):
        pass


class LogErrors(HandleErrorAbstract):
    """
    Log any errors that happen during previous pipeline steps.
    """
    def __init__(self, receive_queue: asyncio.Queue):
        """Initialise class.

        Args:
            receive_queue: Async queue from where to receive pokemon jobs
        """
        self._receive_queue = receive_queue
        self._errors = []
        self.__worker_id = uuid.uuid4()

    def worker_id(self):
        return self.__worker_id

    def set_pipeline_status(self, pipeline_status):
        self.pipeline_status = pipeline_status

    def keep_processing_jobs(self):
        return (not self._receive_queue.empty()
                or
                not self.pipeline_status.pokemon_data_saver_finished)

    async def handle_error(self):
        """Iterate over the previous pipeline steps and log any error that
            was recorded.

        Pull jobs from the receiver queue, the pulls are awaited for
            0.25 seconds, the reason for that is to avoid an infinite await in
            case the queue is empty, an infinite await can happen if we enter the
            while loop while the previous step is just about to set the step finish
            flag to True.
        """
        if not self.pipeline_status.error_handling_workers[self.worker_id()]:
            self.pipeline_status.error_handling_workers[self.worker_id()] = True
        self.pipeline_status.set_error_handling_started()
        while self.keep_processing_jobs():
            try:
                current_job = await asyncio.wait_for(self._receive_queue.get(),
                                                     timeout=0.25)
            except asyncio.TimeoutError:
                error_workers_active = [
                    v for _, v in
                    self.pipeline_status.error_handling_workers.items() if v]
                if not error_workers_active:
                    self.pipeline_status.set_error_handling_finished()
                    break
            else:
                if current_job.has_job_failed():
                    msg = f'Failed to extract data from pokemon = {current_job.pokemon_name}'
                    logging.error(msg)
                if self.pipeline_status.pokemon_data_saver_finished and self._receive_queue.empty():
                    self.pipeline_status.set_error_handling_finished()


    def raise_error_if_specified(self):
        pass