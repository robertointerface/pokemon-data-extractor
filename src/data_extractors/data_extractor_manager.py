import uuid
from src.data_extractors.api_extractor import AsyncPokemonRestApiConsumer
from src.exceptions import PokemonNotFoundError
from src.queue_workers import JobQueue
from asyncio import Queue
from src.abc_managers import AbcJobProcessorManager


class DataExtractorManager(AbcJobProcessorManager):

    def __init__(self,
                 receive_queue: JobQueue,
                 send_queue: Queue):
        """Initialize worker.
        Args:
            receive_queue: input queue.
            send_queue: output queue.
        """
        self.receive_queue = receive_queue
        self.send_queue = send_queue
        self.pipeline_status = None
        self.__worker_id = uuid.uuid4()

    def worker_id(self):
        return self.__worker_id

    def get_job(self):
        """Pull a job from the input queue"""
        return self.receive_queue.dequeue()

    def keep_processing_jobs(self):
        """Determine if we need to keep pulling from the input queue, in this
        class is easy as the input queue in non async and no more jobs will
        be added to the queue after we start pulling from it."""
        return not self.receive_queue.empty()

    def set_pipeline_status(self, pipeline_status):
        """Set the pipeline status attribute, pipeline status is shared between
        all workers so they can know the overall system status."""
        self.pipeline_status = pipeline_status

    async def process_work(self, client):
        """Extract pokemon data through the pokemon API. An instance of this
            class is part
            of a cluster of 'job instances' that concurrently are calling the pokemon
            API, The class PipelineStatus is the class that monitors the 'job
            instances' and is shared between these job instances.
            Once we have finished
            getting all the required pokemon data we need, then we need to set the flag
            'pokemon_data_extractor_finished' on the pipeline status, that flag
            tells the next step of the pipeline that no more jobs will come through
            the pipeline.
            The way we set the flag 'pokemon_data_extractor_finished' is by
            monitoring the 'receive_queue', as the queue is non-async and at this first
            stage the queue gets all its inputs at the beginning and no more
            later, we can easy know when no more jobs need to be process, if
            the queue is empty we can start turning off jobs, as they will not
            need to pull anything more form the queue, once all jobs have
            finished we can set the flag 'pokemon_data_extractor_finished'.

        Args:
            client: Httpx Asynclient used to make async httpx requests.

        """
        # if the workers are off, turn them on so the pipeline status manager
        # can keep track which workers are on or off.
        if not self.pipeline_status.pokemon_extractor_workers[self.worker_id()]:
            self.pipeline_status.pokemon_extractor_workers[self.worker_id()] = True
        self.pipeline_status.set_pokemon_data_extractor_starter()
        while self.keep_processing_jobs():
            current_job = self.get_job()
            api_caller = AsyncPokemonRestApiConsumer(current_job.pokemon_name)
            try:
                await api_caller.get_pokemon_data(client)
            except PokemonNotFoundError as e:
                print(f'job failed for {current_job.pokemon_name}')
                current_job.set_job_failed()
            else:
                current_job.set_pokemon_result(api_caller.result)
            current_job.set_job_status_extracted_data()
            print(f'finished extracting job {current_job.pokemon_name}')
            await self.send_queue.put(current_job)
        # Once the queue is empty we can set this specific worker as 'off',
        # so it knows it does not have to pull any more works from the queue.
        if self.receive_queue.empty():
            self.pipeline_status.pokemon_extractor_workers[self.worker_id()] = False
        # The pipeline_status.pokemon_extractor_workers has all the pokemon
        # extractor workers, we find out how many are still active and if None
        # of them are active then we can set the pokemon data extraction as
        # finished.
        data_workers_active = [v for _, v in self.pipeline_status.pokemon_extractor_workers.items() if v]
        if not data_workers_active:
            print(f'finished data extraction')
            self.pipeline_status.set_pokemon_data_extractor_finished()