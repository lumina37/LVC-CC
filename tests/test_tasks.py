from lvccc.task import BaseTask, ConvertTask, CopyTask, DecodeTask, EncodeTask


def test_tasks():
    tcopy = CopyTask(seq_name="Fujita2", frames=1)
    tenc = EncodeTask(qp=46).follow(tcopy)
    tdec = DecodeTask().follow(tenc)
    tconvert = ConvertTask().follow(tdec)

    chain = tconvert.to_dicts()

    tconvert_rec: ConvertTask = BaseTask.from_dicts(chain)
    assert tconvert_rec.ancestor(0).frames == tcopy.frames
    assert tconvert_rec.ancestor(0).seq_name == tcopy.seq_name
    assert tconvert_rec.ancestor(1).qp == tenc.qp
