from .base import *  # noqa

Q_CLUSTER["sync"] = True

VAPID_PRIVATE_KEY = ROOT_DIR.path("muni_portal/tests/data/vapid_private_key.pem")
VAPID_PUBLIC_KEY = ROOT_DIR.path("muni_portal/tests/data/vapid_public_key.pem")
