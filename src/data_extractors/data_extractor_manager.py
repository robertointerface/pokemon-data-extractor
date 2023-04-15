from src.queue_workers import JobQueue
from asyncio import Queue


class DataExtractorManager:

    def __init__(self,
                 receive_queue: JobQueue,
                 send_queue: Queue):
        self.receive_queue = receive_queue
        self.send_queue = send_queue
        self.pipeline_status = None

    def keep_processing_density_jobs(self):
        pass

    async def process_work(self, client):
        pass

