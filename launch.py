import asyncio
try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()

import config
from bot import Horizon
from cogs.utils import db


def run():
    loop = asyncio.get_event_loop()
    pool = loop.run_until_complete(db.create_pool(config.credentials))

    horizon = Horizon()
    horizon.pool = pool
    horizon.run()


if __name__ == '__main__':
    run()
