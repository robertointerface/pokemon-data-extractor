import argparse

parser = argparse.ArgumentParser(description="get requested pokemons")


parser.add_argument(dest="pokemons",
                    metavar="filename",
                    nargs='*',
                    help='Pokemon names')
parser.add_argument('-s', '--saver',
                    metavar='saver',
                    default='mongo',
                    choices={"mongo", "txt"},
                    help="Location where to store pokemon data")


if __name__ == "__main__":
    args = parser.parse_args()
    