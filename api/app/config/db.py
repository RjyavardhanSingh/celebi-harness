import kuzu
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=False,
)

logger = logging.getLogger(__name__)

logger.info("Starting db connection")

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BASE_DIR/"kuzu.db")

db = kuzu.Database(DB_PATH)
conn = kuzu.Connection(db)

def __init_db__():

    try:
        conn.execute("CREATE NODE TABLE State(id STRING, step_type STRING, payload STRING, PRIMARY KEY (id))") #
    except RuntimeError:
        pass
    try:   
        # Create the directional relationship table
        conn.execute("CREATE REL TABLE TRANSITIONED_TO(FROM State TO State)") #
    except RuntimeError:
        pass
    try:
        #the branching relationship
        conn.execute("CREATE REL TABLE BRANCHED_TO(FROM State TO State)")
    except RuntimeError:
        pass
        
        
    logger.info("Celebi timeline initialized successfully.")

    
    return conn


try:
    __init_db__()
except Exception as e:
    logger.critical(f"Failed to initialize database: {e}")
    raise