import json
import os
import pytest
import sys
from httpx import AsyncClient

import src.job_organizer
from src import constants
from src.job_organizer import DataExtractorOrganizer


class TestDataExtractorOrganizer:

    @pytest.fixture
    def set_file_saver_path_to_testing_path(self, tmp_path):
        prev_DEFAULT_JSON_FILE = constants.DEFAULT_JSON_FILE
        yield
        src.job_organizer.DEFAULT_JSON_FILE = prev_DEFAULT_JSON_FILE

    @pytest.mark.unit
    async def test_json_files_are_saved(self,
                                        tmp_path,
                                        job_queue,
                                        mock_AsyncClient_get,
                                        rest_api_200_json_response):
        src.job_organizer.DEFAULT_JSON_FILE = tmp_path
        data_extractor_organizer = DataExtractorOrganizer(job_queue)
        data_extractor_organizer.set_data_saver_mode(constants.JSON_FILE_SAVER_MODE)
        async with AsyncClient() as client:
            await data_extractor_organizer.start(client)
        if not os.listdir(tmp_path):
            pytest.fail(f'No pokemon files were saved')
        for file in os.listdir(tmp_path):
            file_data = json.loads((tmp_path / str(file)).read_text())
            assert file_data == rest_api_200_json_response

    @pytest.mark.unit
    async def test_json_files_are_saved_with_no_mocking(self,
                                                        tmp_path,
                                                        job_queue):
        src.job_organizer.DEFAULT_JSON_FILE = tmp_path
        data_extractor_organizer = DataExtractorOrganizer(job_queue)
        data_extractor_organizer.set_data_saver_mode(
            constants.JSON_FILE_SAVER_MODE)
        async with AsyncClient() as client:
            await data_extractor_organizer.start(client)
        if not os.listdir(tmp_path):
            pytest.fail(f'No pokemon files were saved')
        for file in os.listdir(tmp_path):
            file_data = json.loads((tmp_path / str(file)).read_text())
            assert isinstance(file_data, dict)

    @pytest.mark.unit
    async def test_errors_are_logged(self,
                                     caplog,
                                     tmp_path,
                                     mock_AsyncClient_returns_error_one_time,
                                     job_queue):
        src.job_organizer.DEFAULT_JSON_FILE = tmp_path
        data_extractor_organizer = DataExtractorOrganizer(job_queue)
        data_extractor_organizer.set_data_saver_mode(
            constants.JSON_FILE_SAVER_MODE)
        async with AsyncClient() as client:
            await data_extractor_organizer.start(client)
        assert 'Failed to extract data from pokemon' in caplog.text