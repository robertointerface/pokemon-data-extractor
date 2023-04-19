
from httpx import AsyncClient
import asyncio
from constants import JSON_FILE_SAVER_MODE, DEFAULT_JSON_FILE
from data_extractors.data_extractor_manager import DataExtractorManager
from data_savers.data_saver_manager import DataSaverManager
from data_savers.json_file_saver import JsonFileSaver
from error_handler import LogErrors
from job_status import PipelineStatus
from queue_workers import JobQueue


class DataExtractorOrganizer:
    """
    Job organizer is in charge of creating the pipeline steps and each step
    will have a predefined number of workers that will work concurrently on that
    step specific task.

    i.e lets say you have Step A, B anc C.
    Step A: has 3 workers that run concurrently.
    Step B: has 2 workers that run concurrently.
    Step C: has 4 workers that run concurrently.

    We need to start and also shut down workers, workers are started at the beggining
    at the same time and as they don't have any more work to process these are
    shut down.

    We also need to monitor the pipeline state, we need to know when Steps
    have finished at then remember that those steps have finished, this is
    necessary so next steps know how their previous steps are doing.

    As soon as the step input queue is empty the step workers need to stop,
    otherwise they will be left in an infinite wait (in case is an async queue).


    """
    def __init__(self,
                 jobs: JobQueue,
                 max_data_extractors: int = 3,
                 max_result_exporters: int = 3):
        """Set the pipeline configurations and first step queue.

        Args:
            jobs: Queue that will be consumed on the first step, this is a
                NON-ASYNC queue
            max_data_extractors: Maximum number of data extractors that can
                work concurrently.
            max_result_exporters: Maximum number of result exporters that can
                work concurrently.
        """
        self.jobs = jobs
        self.max_data_extractors = max_data_extractors
        self.max_result_exporters = max_result_exporters
        self._result_exporter_mode = None

    def result_exporter_factory(self, *args) -> JsonFileSaver:
        """Create the result exporter to export the extracted data.

        The result exporter methodology is dictated on attribute
            _result_exporter_mode
        Args:
            *args: Multiple arguments that are not required in the current version
                but might be required later one.

        Returns: the Result exporter.

        """
        if not self._result_exporter_mode:
            raise ValueError(f'attribute self._data_saver_mode must be set before'
                             f' calling method data_saver_factory')
        client = args
        if self._result_exporter_mode == JSON_FILE_SAVER_MODE:
            return JsonFileSaver(DEFAULT_JSON_FILE)
        raise NotImplementedError(
            f'Saver mode methodology {self._result_exporter_mode} has not been '
            f'implemented yet.')

    def set_result_exporter_mode(self, result_exporter_methodology: str):
        self._result_exporter_mode = result_exporter_methodology

    async def supervisor(self, httpx_client: AsyncClient):
        """Orchestrate pipeline.

        - All the pipeline steps are initialized here.
        - each pipeline step workers are initialized and connected to each step.
        - Pipeline management instance is connected to all steps and their workers
        - Async worker producers are initialised.
        - async workers producers are consumed.

        Args:
            httpx_client: AsyncClient used to call rest api
        """
        # if no jobs then just return, nothing to do here
        if not self.jobs:
            return
        # Initialize the pipeline status class
        pipeline_status = PipelineStatus()
        result_exporter_instance = self.result_exporter_factory(httpx_client)
        # initialize the async queues that will communicate between
        # data extractor - result extractor queues
        # result extractor queues - error handler queue
        extractor_send_queue = asyncio.Queue()
        data_saver_send_queue = asyncio.Queue()
        # Define the async workers
        data_extractor_workers = [
            DataExtractorManager(self.jobs, extractor_send_queue)
            for _ in range(self.max_result_exporters)]
        data_saver_workers = [
            DataSaverManager(extractor_send_queue, data_saver_send_queue)
            for _ in range(self.max_data_extractors)]
        error_handler_workers = [LogErrors(data_saver_send_queue)
                                 for _ in range(2)]
        # Initialize the worker ids, with the worker ids we can keep track
        # of their status in the pipeline
        data_workers_ids = {w.worker_id(): False for w in data_extractor_workers}
        data_saver_ids = {w.worker_id(): False for w in data_saver_workers}
        error_handler_ids = {w.worker_id(): False for w in error_handler_workers}
        pipeline_status.pokemon_extractor_workers = data_workers_ids
        pipeline_status.pokemon_saver_workers = data_saver_ids
        pipeline_status.error_handling_workers = error_handler_ids
        # connect pipeline management to each step
        [i.set_pipeline_status(pipeline_status)
         for i in [*data_extractor_workers,
                   *data_saver_workers,
                   *error_handler_workers]]
        # initialise worker producers
        data_extractor_producers = [worker.process_work(httpx_client)
                                    for worker in data_extractor_workers]
        data_saver_producers = [worker.process_work(result_exporter_instance)
                                for worker in data_saver_workers]
        error_logger_producers = [worker.handle_error()
                                  for worker in error_handler_workers]
        # call async on all workers
        await asyncio.gather(*data_extractor_producers,
                             *data_saver_producers,
                             *error_logger_producers)

    async def start(self):
        async with AsyncClient() as httpx_client:
            await self.supervisor(httpx_client)