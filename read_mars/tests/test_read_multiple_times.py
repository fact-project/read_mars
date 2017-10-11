import read_mars
import pkg_resources


def test_open():

    path = pkg_resources.resource_filename(
        'read_mars',
        'tests/resources/20130930_244_244_B.root')

    with read_mars.StatusDisplay(path) as f:
        pass


def test_read_multiple():

    path = pkg_resources.resource_filename(
        'read_mars',
        'tests/resources/20130930_244_244_B.root')

    for i in range(30):
        with read_mars.StatusDisplay(path) as f:
            pass

