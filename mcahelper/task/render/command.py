from ...cfg.node import get_node_cfg


def build(cfg: str) -> list[str]:
    node_cfg = get_node_cfg()

    cfg = str(cfg)

    return [
        node_cfg.app.rlc,
        cfg,
    ]
