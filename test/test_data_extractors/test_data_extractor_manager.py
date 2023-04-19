import pytest
from asyncio import Queue
from unittest.mock import AsyncMock
from pytest_mock import mocker
from httpx import AsyncClient
from data_extractors.data_extractor_manager import DataExtractorManager
from job_status import PipelineStatus


@pytest.mark.unit
class TestDataExtractorManager:

    def create_data_extractor_manager(self, job_queue):
        send_queue = Queue()
        pipeline_status = PipelineStatus()
        data_extractor = DataExtractorManager(job_queue,
                                              send_queue)
        pipeline_status.pokemon_extractor_workers = {data_extractor.worker_id(): False}
        data_extractor.set_pipeline_status(pipeline_status)
        return data_extractor

    async def test_process_work_method_consumes_recieve_queue(self,
                                                mock_AsyncClient_get,
                                                job_queue):

        data_extractor = self.create_data_extractor_manager(job_queue)
        async with AsyncClient() as client:
            await data_extractor.process_work(client)
        assert job_queue.empty(), \
            "DataExtractorManager.process_work did not consume receive queue"

    async def test_process_work_calls_AsyncPokemonRestApiConsumer_get_pokemon_data_method(self,
                                                                                          mocker,
                                                                                          job_queue):
        mocked = AsyncMock(return_value=None)
        mocker.patch('src.data_extractors.data_extractor_manager.AsyncPokemonRestApiConsumer.get_pokemon_data',
                     side_effect=mocked)
        mocker.patch('src.data_extractors.data_extractor_manager.AsyncPokemonRestApiConsumer.result',
                     return_value={})
        data_extractor = self.create_data_extractor_manager(job_queue)
        async with AsyncClient() as client:
            await data_extractor.process_work(client)
        mocked.assert_awaited()

    async def test_process_work_puts_pokemon_jobs_into_send_queue(self,
                                                            mock_AsyncClient_get,
                                                            job_queue):
        number_of_jobs = len(job_queue)
        data_extractor = self.create_data_extractor_manager(job_queue)
        async with AsyncClient() as client:
            await data_extractor.process_work(client)
        assert data_extractor.send_queue.qsize() == number_of_jobs

    @pytest.mark.unit
    async def test_failed_status_is_set_for_jobs_that_failed(self,
                                                             tmp_path,
                                                             job_queue,
                                                             mock_AsyncClient_returns_error_one_time):
        data_extractor = self.create_data_extractor_manager(job_queue)
        async with AsyncClient() as client:
            await data_extractor.process_work(client)
        jobs = []
        while not data_extractor.send_queue.empty():
            jobs.append(await data_extractor.send_queue.get())
        assert any([i.has_job_failed() for i in jobs])