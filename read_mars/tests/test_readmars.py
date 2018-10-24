from read_mars import read_mars


def test_ganymed_analysis():
    df = read_mars('read_mars/tests/resources/ganymed_summary.root')

    assert len(df) == 48846
    assert 'MHillas.fWidth' in df.columns


def test_ganymed_leafs():
    df = read_mars(
        'read_mars/tests/resources/ganymed_summary.root',
        leaf_names=['MHillas.fWidth', 'MHillas.fLength', 'EvtNumber.fVal']
    )

    assert len(df) == 48846
    assert len(df.columns) == 3
