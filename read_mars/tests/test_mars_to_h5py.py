import subprocess
import tempfile


def test_read_mars():

    with tempfile.NamedTemporaryFile(prefix='read_mars_', suffix='.hdf5') as f:
        res = subprocess.check_call([
            'python',
            '-m',
            'read_mars.mars_to_h5py',
            'read_mars/tests/resources/ganymed_summary.root',
            f.name,
        ])

        assert res == 0
