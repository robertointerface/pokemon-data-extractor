import asyncio
from httpx import AsyncClient
from asyncio import Queue
from src.constants import JSON_FILE_SAVER_MODE, DEFAULT_JSON_FILE
from src.data_extractors.data_extractor_manager import DataExtractorManager
from src.data_savers.data_saver_manager import DataSaverManager
from src.data_savers.json_file_saver import JsonFileSaver
from src.error_handler import LogErrors
from src.job_status import PipelineStatus


class DataExtractorOrganizer:

    def __init__(self,
                 jobs,
                 max_data_extractors=3,
                 max_result_exporters=3):
        self.jobs = jobs
        self.max_data_extractors = max_data_extractors
        self.max_result_exporters = max_result_exporters
        self._data_saver_mode = None

    def data_saver_factory(self, *args):
        if not self._data_saver_mode:
            raise ValueError(f'attribute self._data_saver_mode must be set before'
                             f' calling method data_saver_factory')
        client = args
        if self._data_saver_mode == JSON_FILE_SAVER_MODE:
            return JsonFileSaver(DEFAULT_JSON_FILE)
        raise NotImplementedError(
            f'Saver mode methodology {self._data_saver_mode} has not been '
            f'implemented yet.')

    def set_data_saver_mode(self, data_saver_methodology: str):
        self._data_saver_mode = data_saver_methodology

    async def supervisor(self, httpx_client):
        # create the queues
        if not self.jobs:
            return
        pipeline_status = PipelineStatus()
        data_saver_instance = self.data_saver_factory(httpx_client)
        extractor_send_queue = Queue()
        data_saver_send_queue = Queue()
        data_extractor_workers = [DataExtractorManager(self.jobs, extractor_send_queue)
                                  for _ in range(self.max_result_exporters)]
        data_saver_workers = [DataSaverManager(extractor_send_queue, data_saver_send_queue)
                              for _ in range(self.max_data_extractors)]
        error_handler_workers = [LogErrors(data_saver_send_queue)
                                 for _ in range(2)]
        [i.set_pipeline_status(pipeline_status)
         for i in [*data_extractor_workers,
                   *data_saver_workers,
                   *error_handler_workers]]
        data_extractor_producers = [worker.process_work(httpx_client)
                                    for worker in data_extractor_workers]
        data_saver_producers = [worker.process_work(data_saver_instance)
                                for worker in data_saver_workers]
        error_logger_producers = [worker.handle_error()
                                  for worker in error_handler_workers]
        await asyncio.gather(*data_extractor_producers,
                             *data_saver_producers,
                             *error_logger_producers)

    async def start(self):
        async with AsyncClient() as httpx_client:
            await self.supervisor(httpx_client)