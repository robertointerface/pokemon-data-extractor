import pytest
from asyncio import Queue
from unittest.mock import AsyncMock
from pytest_mock import mocker
from httpx import AsyncClient
from src.data_extractors.data_extractor_manager import DataExtractorManager
from src.queue_workers import JobQueue
from src.job_status import PipelineStatus, PokemonJob


@pytest.mark.unit
class TestDataExtractorManager:

    @pytest.fixture
    def receive_queue(self, job_list):
        job_queue = JobQueue()
        [job_queue.enqueue(job) for job in job_list]
        return job_queue

    def create_data_extractor_manager(self, receive_queue):
        send_queue = Queue()
        pipeline_status = PipelineStatus()
        data_extractor = DataExtractorManager(receive_queue,
                                              send_queue)
        data_extractor.set_pipeline_status(pipeline_status)
        return data_extractor

    async def test_process_work_method_consumes_recieve_queue(self,
                                                mock_AsyncClient_get,
                                                receive_queue):
        data_extractor = self.create_data_extractor_manager(receive_queue)
        async with AsyncClient() as client:
            await data_extractor.process_work(client)
        assert receive_queue.empty(), \
            "DataExtractorManager.process_work did not consume receive queue"

    async def test_process_work_calls_AsyncPokemonRestApiConsumer_get_pokemon_data_method(self,
                                                                                          mocker,
                                                                                          receive_queue):
        mocked = AsyncMock(return_value=None)
        mocker.patch('src.data_extractors.data_extractor_manager.AsyncPokemonRestApiConsumer.get_pokemon_data',
                     side_effect=mocked)
        mocker.patch('src.data_extractors.data_extractor_manager.AsyncPokemonRestApiConsumer.result',
                     return_value={})
        data_extractor = self.create_data_extractor_manager(receive_queue)
        async with AsyncClient() as client:
            await data_extractor.process_work(client)
        mocked.assert_awaited()

    async def test_process_work_puts_pokemon_jobs_into_send_queue(self,
                                                            mock_AsyncClient_get,
                                                            receive_queue):
        number_of_jobs = len(receive_queue)
        data_extractor = self.create_data_extractor_manager(receive_queue)
        async with AsyncClient() as client:
            await data_extractor.process_work(client)
        assert data_extractor.send_queue.qsize() == number_of_jobs