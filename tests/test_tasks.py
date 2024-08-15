from lvccc.task import CodecTask, Img2yuvTask, ImgCopyTask, PostprocTask, PreprocTask, RenderTask, Yuv2imgTask


def test_tasks():
    tcopy = ImgCopyTask(seq_name="NagoyaFujita", frames=1)
    tpre = PreprocTask().with_parent(tcopy)
    ti2y = Img2yuvTask().with_parent(tpre)
    tcodec = CodecTask(qp=46).with_parent(ti2y)
    ty2i = Yuv2imgTask().with_parent(tcodec)
    tpost = PostprocTask().with_parent(ty2i)
    trender = RenderTask().with_parent(tpost)

    chain = trender.chain_with_self
    trender_rec = chain[-1]
    assert trender_rec.chain[0].frames == tcopy.frames
    assert trender_rec.chain[0].seq_name == tcopy.seq_name
    assert trender_rec.chain[3].qp == tcodec.qp
