import os


def full_path(path):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data/{}'.format(path))