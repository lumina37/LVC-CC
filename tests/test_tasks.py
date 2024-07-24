from lvccc.task import CodecTask, CopyTask, Png2yuvTask, PostprocTask, PreprocTask, RenderTask, Yuv2pngTask


def test_tasks() -> None:
    tcopy = CopyTask(seq_name="NagoyaFujita", frames=1)
    tpre = PreprocTask().with_parent(tcopy)
    tp2y = Png2yuvTask().with_parent(tpre)
    tcodec = CodecTask(qp=46).with_parent(tp2y)
    ty2p = Yuv2pngTask().with_parent(tcodec)
    tpost = PostprocTask().with_parent(ty2p)
    trender = RenderTask().with_parent(tpost)

    chain = trender.chain_with_self
    trender_rec = chain[-1]
    assert trender_rec.chain[0].frames == tcopy.frames
    assert trender_rec.chain[3].qp == tcodec.qp
