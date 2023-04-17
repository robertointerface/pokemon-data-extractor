import pytest
from asyncio import Queue

from src.constants import DEFAULT_JSON_FILE
from src.data_savers.data_saver_manager import DataSaverManager
from src.data_savers.json_file_saver import JsonFileSaver
from src.job_status import PokemonJob, PipelineStatus

@pytest.mark.unit
class TestDataSaverManager:

    POKEMONS_TO_TEST = ['mewtwo', 'charizar', 'Bulbasaur', 'Gengar',
                        'Lapras', 'pikachu']


    def create_datasaver_manager_ready_to_user(self,
                                               receive_queue: Queue) -> DataSaverManager:
        pipeline_status = PipelineStatus()
        pipeline_status.set_pokemon_data_extractor_finished()
        send_queue = Queue()
        data_saver_manager = DataSaverManager(receive_queue, send_queue)
        data_saver_manager.set_pipeline_status(pipeline_status)
        return data_saver_manager

    async def test_get_job_returns_PokemonJob(self, mock_job_queue: Queue):
        data_saver_manager = self.create_datasaver_manager_ready_to_user(mock_job_queue)
        pokemon_job = await data_saver_manager.get_job()
        assert isinstance(pokemon_job, PokemonJob)

    async def test_save_data_method_is_called_with_correct_parameters(self,
                                                                      rest_api_200_json_response,
                                                                      mock_job_queue: Queue,
                                                                      mock_JsonFileSaver_save_data_method):
        data_saver_manager = self.create_datasaver_manager_ready_to_user(mock_job_queue)
        json_file_saver = JsonFileSaver(DEFAULT_JSON_FILE)
        await data_saver_manager.process_work(json_file_saver)
        mock_JsonFileSaver_save_data_method.assert_called_with(rest_api_200_json_response)

    async def test_receive_queue_is_consumed(self,
                                             mock_job_queue: Queue,
                                             mock_JsonFileSaver_save_data_method):
        data_saver_manager = self.create_datasaver_manager_ready_to_user(mock_job_queue)
        json_file_saver = JsonFileSaver(DEFAULT_JSON_FILE)
        await data_saver_manager.process_work(json_file_saver)
        assert mock_job_queue.empty()

    async def test_pokemon_jobs_are_put_in_send_queue(self,
                                                      mock_job_queue: Queue,
                                                      mock_JsonFileSaver_save_data_method):
        list_of_jobs_to_process = mock_job_queue.qsize()
        data_saver_manager = self.create_datasaver_manager_ready_to_user(
            mock_job_queue)
        json_file_saver = JsonFileSaver(DEFAULT_JSON_FILE)
        await data_saver_manager.process_work(json_file_saver)
        assert data_saver_manager.send_queue.qsize() == list_of_jobs_to_process

