import argparse

from src.job_organizer import DataExtractorOrganizer
from src.job_status import PokemonJob
from src.queue_workers import JobQueue

parser = argparse.ArgumentParser(description="get requested pokemons")


parser.add_argument(dest="pokemons",
                    metavar="filename",
                    nargs='*',
                    help='Pokemon names')
parser.add_argument('-s',
                    '--saver',
                    metavar='saver',
                    default='mongo',
                    choices={"mongo", "txt"},
                    help="Location where to store pokemon data")


if __name__ == "__main__":
    args = parser.parse_args()
    pokemon_names = args.pokemons
    data_saver = args.saver
    pokemon_job_queue = JobQueue()
    pokemon_jobs = [PokemonJob(name) for name in pokemon_names]
    jobs_queue = map(pokemon_job_queue.enqueue, pokemon_jobs)
    extractor_organizer = DataExtractorOrganizer(jobs_queue)
    extractor_organizer.set_data_saver_mode(data_saver)

    # create a deque of JobStatus
    # init data extractor organizer
    # set data_saver mode
    # init httpx client
    #

    