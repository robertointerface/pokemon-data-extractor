from src.data_savers.json_file_saver import JsonFileSaver
from src.job_status import PokemonJob
from src.queue_workers import JobQueue
from asyncio import Queue
from src.abc_managers import AbcJobProcessorManager


class DataSaverManager(AbcJobProcessorManager):

    def __init__(self,
                 receive_queue: Queue,
                 send_queue: Queue):
        self.receive_queue = receive_queue
        self.send_queue = send_queue
        self.pipeline_status = None

    async def get_job(self) -> PokemonJob:
        job = await self.receive_queue.get()
        return job

    def keep_processing_jobs(self):
        return (not self.receive_queue.empty()
                or
                not self.pipeline_status.pokemon_data_extractor_finished)

    def set_pipeline_status(self, pipeline_status):
        self.pipeline_status = pipeline_status

    async def process_work(self, work_processor: JsonFileSaver):
        self.pipeline_status.set_pokemon_data_saver_started_started()
        while self.keep_processing_jobs():
            current_job = await self.get_job()
            if not current_job.has_job_failed():
                pokemon_result = current_job.get_job_result()
                await work_processor.save_data(pokemon_result.pokemon_data)
                current_job.set_job_status_saved_data()
            await self.send_queue.put(current_job)
        self.pipeline_status.set_pokemon_data_saver_finished()