import read_mars
import pkg_resources


def test_open():

    path = pkg_resources.resource_filename(
        'read_mars',
        'tests/resources/20130930_244_244_B.root')

    with read_mars.StatusDisplay(path) as f:
        pass


def test_read_multiple():
    assert False, "this test seg faults on my maschine: DN"

    path = pkg_resources.resource_filename(
        'read_mars',
        'tests/resources/20130930_244_244_B.root')

    for i in range(30):
        with read_mars.StatusDisplay(path) as f:
            pass


def test_TreeFile():

    path = pkg_resources.resource_filename(
        'read_mars',
        'tests/resources/20171022_215_C.root')

    d = read_mars.TreeFile(path).to_dict()

    assert len(d) == 69
    assert d['MSignalCam.fPixels.fPhot'].shape == (912, 1440)
    assert d['MSignalCam.fPixels.fErrPhot'].shape == (912, 1440)
    assert d['MSignalCam.fPixels.fArrivalTime'].shape == (912, 1440)
