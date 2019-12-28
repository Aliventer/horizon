from bot import Horizon


def run():
    horizon = Horizon(db=None)
    horizon.run()


if __name__ == '__main__':
    run()
