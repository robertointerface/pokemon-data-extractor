import asyncio
import uuid
from src.data_savers.json_file_saver import JsonFileSaver
from src.job_status import PokemonJob
from asyncio import Queue
from src.abc_managers import AbcJobProcessorManager


class DataSaverManager(AbcJobProcessorManager):

    def __init__(self,
                 receive_queue: Queue,
                 send_queue: Queue):
        self.receive_queue = receive_queue
        self.send_queue = send_queue
        self.pipeline_status = None
        self.__worker_id = uuid.uuid4()

    def worker_id(self):
        return self.__worker_id

    async def get_job(self) -> PokemonJob:
        job = await self.receive_queue.get()
        return job

    def keep_processing_jobs(self):
        """For this worker, it will stop processing jobs as soon as the queue
        is empty AND the previous step is Finished, this is consuming and async
        queue, so even if the queue is empty it does not mean that it can terminate
        as maybe it terminates but the queue starts getting full right after."""
        return (not self.receive_queue.empty()
                or
                not self.pipeline_status.pokemon_data_extractor_finished)

    def set_pipeline_status(self, pipeline_status):
        self.pipeline_status = pipeline_status

    async def process_work(self, work_processor: JsonFileSaver):
        """

        Args:
            work_processor:

        Returns:

        """
        if not self.pipeline_status.pokemon_saver_workers[self.worker_id()]:
            self.pipeline_status.pokemon_saver_workers[self.worker_id()] = True
        self.pipeline_status.set_pokemon_data_saver_started_started()
        while self.keep_processing_jobs():
            try:
                current_job = await asyncio.wait_for(self.get_job(),
                                                     timeout=0.25)
            except asyncio.TimeoutError:
                data_workers_active = [
                    v for _, v in self.pipeline_status.pokemon_saver_workers.items() if v]
                if not data_workers_active:
                    self.pipeline_status.set_pokemon_data_saver_finished()
                    break
            else:
                if not current_job.has_job_failed():
                    print(f'saving job {current_job.pokemon_name}')
                    pokemon_result = current_job.get_job_result()
                    await work_processor.save_data(pokemon_result.pokemon_data)
                    current_job.set_job_status_saved_data()
                await self.send_queue.put(current_job)
                if self.pipeline_status.pokemon_data_extractor_finished and self.receive_queue.empty():
                    self.pipeline_status.set_pokemon_data_saver_finished()

