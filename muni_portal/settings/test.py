from .base import *  # noqa

Q_CLUSTER = Q_CLUSTER
Q_CLUSTER["sync"] = True

VAPID_PRIVATE_KEY = ROOT_DIR.path("tests/data/vapid_private_key.pem")
