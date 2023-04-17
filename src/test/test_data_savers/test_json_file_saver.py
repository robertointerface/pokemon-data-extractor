import json

import pytest

from src.data_savers.json_file_saver import JsonFileSaver


@pytest.mark.unit
def test_file_path_setter_raises_ValueError_when_non_path_value_is_used():
    with pytest.raises(ValueError):
        _ = JsonFileSaver(32)


@pytest.mark.unit
async def test_save_data_on_file_method_saves_data(tmp_path, rest_api_200_json_response):
    temp_json_file = tmp_path / f'{rest_api_200_json_response.get("name")}.json'
    f_saver = JsonFileSaver(tmp_path)
    await f_saver.save_data(rest_api_200_json_response)
    with open(temp_json_file, 'r+') as fp:
        assert json.loads(fp.read()) == rest_api_200_json_response