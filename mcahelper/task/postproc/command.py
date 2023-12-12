from ...cfg.node import get_node_cfg


def build(cfg: str, src: str, dst: str) -> list[str]:
    node_cfg = get_node_cfg()

    cfg = str(cfg)
    src = str(src)
    dst = str(dst)

    return [
        node_cfg.app.postproc,
        cfg,
        src,
        dst,
    ]
