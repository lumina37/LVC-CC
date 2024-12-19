from lvccc.task import Chain, CodecTask, ConvertTask, CopyTask, PostprocTask, PreprocTask


def test_tasks():
    tcopy = CopyTask(seq_name="NagoyaFujita", frames=1)
    tpre = PreprocTask().with_parent(tcopy)
    tcodec = CodecTask(qp=46).with_parent(tpre)
    tpost = PostprocTask().with_parent(tcodec)
    tconvert = ConvertTask().with_parent(tpost)

    chain = Chain(tconvert.to_dicts())
    tconvert_rec = chain[-1]
    assert tconvert_rec.chain[0].frames == tcopy.frames
    assert tconvert_rec.chain[0].seq_name == tcopy.seq_name
    assert tconvert_rec.chain[2].qp == tcodec.qp
