# weird code

import argparse
from random import choice


class EpicGamerError(Exception):
    def __init__(self, message="EPIC GAMER FAILURE!"):
        super().__init__(message)

    pass


EPIC_GAMER_MOMENTS = {'fps': 'https://i.redd.it/oonl4tw8pxz41.png',
                      'minecraft': 'https://i.redd.it/vws2a2yi9vz41.jpg'}


def get_epic_gamer_moment(mode):
    if mode == 'fps':
        return EPIC_GAMER_MOMENTS['fps']
    elif mode == 'minecraft':
        return EPIC_GAMER_MOMENTS['minecraft']
    elif mode == 'random':
        return choice(list(EPIC_GAMER_MOMENTS.values()))
    else:
        raise EpicGamerError()


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-g", "--epic-gamer-moment",
                           choices=["fps", "minecraft", "random"],
                           required=True,
                           help="returns a link to one of two pictures of Aden Barton "
                                "playing a video game while appearing as if he is debating")
    args = argparser.parse_args()
    print(get_epic_gamer_moment(args.epic_gamer_moment))
