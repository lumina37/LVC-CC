from lvccc.task import BaseTask, ConvertTask, CopyTask, DecodeTask, EncodeTask, PostprocTask, PreprocTask


def test_tasks():
    tcopy = CopyTask(seq_name="Fujita2", frames=1)
    tpre = PreprocTask().follow(tcopy)
    tenc = EncodeTask(qp=46).follow(tpre)
    tdec = DecodeTask().follow(tenc)
    tpost = PostprocTask().follow(tdec)
    tconvert = ConvertTask().follow(tpost)

    chain = tconvert.to_dicts()

    tconvert_rec: ConvertTask = BaseTask.from_dicts(chain)
    assert tconvert_rec.ancestor(0).frames == tcopy.frames
    assert tconvert_rec.ancestor(0).seq_name == tcopy.seq_name
    assert tconvert_rec.ancestor(2).qp == tenc.qp
