from lvccc.task import BaseTask, CodecTask, ConvertTask, CopyTask, PostprocTask, PreprocTask


def test_tasks():
    tcopy = CopyTask(seq_name="Fujita2", frames=1)
    tpre = PreprocTask().follow(tcopy)
    tcodec = CodecTask(qp=46).follow(tpre)
    tpost = PostprocTask().follow(tcodec)
    tconvert = ConvertTask().follow(tpost)

    chain = tconvert.to_dicts()

    tconvert_rec: ConvertTask = BaseTask.from_dicts(chain)
    assert tconvert_rec.ancestor(0).frames == tcopy.frames
    assert tconvert_rec.ancestor(0).seq_name == tcopy.seq_name
    assert tconvert_rec.ancestor(2).qp == tcodec.qp
