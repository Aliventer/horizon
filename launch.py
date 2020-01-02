#!/usr/bin/env python3

try:
    import uvloop
except ImportError:
    pass
else:
    uvloop.install()

from bot import Horizon


def run():
    horizon = Horizon()
    horizon.run()


if __name__ == '__main__':
    run()
