

class DataExtractorOrganizer:

    def __init__(self,
                 jobs,
                 max_data_extractors=3,
                 max_result_exporters=3):
        self.jobs = jobs
        self.max_data_extractors = max_data_extractors
        self.max_result_exporters = max_result_exporters
        self._data_saver_mode = None

    async def set_data_saver_mode(self, mode: str):

        pass

    async def supervisor(self, s3_client):
        # create the queues

        pass

    async def start(self, client):
        pass

