import argparse
import asyncio

from src.constants import JSON_FILE_SAVER_MODE
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
                    default=JSON_FILE_SAVER_MODE,
                    choices={"mongo", JSON_FILE_SAVER_MODE},
                    help="Location where to store pokemon data")



if __name__ == "__main__":
    # args = parser.parse_args()
    # pokemon_names = args.pokemons
    # data_saver = args.saver
    extra_poke = ['Ivysaur', 'Wartortle', 'Metapod',
                  'Pidgey', 'Pidgeotto', 'Fearow', 'Arbok']
    pokemon_names = ['mewtwo', 'non-existing', *extra_poke]
    pokemon_job_queue = JobQueue()
    pokemon_jobs = [PokemonJob(name) for name in pokemon_names]
    [pokemon_job_queue.enqueue(job) for job in pokemon_jobs]
    extractor_organizer = DataExtractorOrganizer(pokemon_job_queue)
    extractor_organizer.set_result_exporter_mode(JSON_FILE_SAVER_MODE)
    asyncio.run(extractor_organizer.start())
