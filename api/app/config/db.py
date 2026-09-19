import logging
import os
from pathlib import Path

import kuzu

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=False,
)

logger = logging.getLogger(__name__)

logger.info("Starting db connection")

BASE_DIR = Path(__file__).resolve().parent.parent
# Packaged installs live in a read-only dir (/opt/celebi/...) — the GUI
# sets CELEBI_DATA_DIR to a writable location (~/.celebi) for those.
_data_dir = os.environ.get("CELEBI_DATA_DIR")
if _data_dir:
    Path(_data_dir).mkdir(parents=True, exist_ok=True)
    DB_PATH = str(Path(_data_dir) / "kuzu.db")
else:
    DB_PATH = str(BASE_DIR / "kuzu.db")

db = kuzu.Database(DB_PATH)
conn = kuzu.Connection(db)


def __init_db__():

    try:
        conn.execute(
            "CREATE NODE TABLE State(id STRING, step_type STRING, payload STRING, PRIMARY KEY (id))"
        )
    except RuntimeError as e:
        if "already exists" not in str(e):
            logger.warning("Failed to create State table: %s", e)
    try:
        # Create the directional relationship table
        conn.execute("CREATE REL TABLE TRANSITIONED_TO(FROM State TO State)")
    except RuntimeError as e:
        if "already exists" not in str(e):
            logger.warning("Failed to create TRANSITIONED_TO table: %s", e)
    try:
        # the branching relationship
        conn.execute("CREATE REL TABLE BRANCHED_TO(FROM State TO State)")
    except RuntimeError as e:
        if "already exists" not in str(e):
            logger.warning("Failed to create BRANCHED_TO table: %s", e)

    logger.info("Celebi timeline initialized successfully.")

    return conn


try:
    __init_db__()
except Exception as e:
    logger.critical(f"Failed to initialize database: {e}")
    raise
