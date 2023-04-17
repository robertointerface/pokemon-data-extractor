from src.data_extractors.api_extractor import AsyncPokemonRestApiConsumer
from src.exceptions import PokemonNotFoundError
from src.queue_workers import JobQueue
from asyncio import Queue
from src.abc_managers import AbcJobProcessorManager


class DataExtractorManager(AbcJobProcessorManager):

    def __init__(self,
                 receive_queue: JobQueue,
                 send_queue: Queue):
        self.receive_queue = receive_queue
        self.send_queue = send_queue
        self.pipeline_status = None

    def get_job(self):
        return self.receive_queue.dequeue()

    def keep_processing_jobs(self):
        return not self.receive_queue.empty()

    def set_pipeline_status(self, pipeline_status):
        self.pipeline_status = pipeline_status

    async def process_work(self, client):
        self.pipeline_status.set_pokemon_data_extractor_starter()
        while self.keep_processing_jobs():
            current_job = self.get_job()
            api_caller = AsyncPokemonRestApiConsumer(current_job.pokemon_name)
            try:
                await api_caller.get_pokemon_data(client)
            except PokemonNotFoundError as e:
                current_job.set_job_failed()
            else:
                current_job.set_pokemon_result(api_caller.result)
            current_job.set_job_status_extracted_data()
            await self.send_queue.put(current_job)
        self.pipeline_status.set_pokemon_data_extractor_finished()
