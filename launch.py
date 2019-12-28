import sys

from bot import Horizon
try:
    from config import token
except ImportError:
    print('Cannot find bot token. Make sure that you created a file `config.py` with a token string in it.')
    sys.exit(0)


def run():
    horizon = Horizon(db=None)
    horizon.run(token)


if __name__ == '__main__':
    run()
