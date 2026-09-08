import kuzu
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=False,
)

logger = logging.getLogger(__name__)

db = kuzu.Database("./kuzu.db")
conn = kuzu.Connection(db)

def __init_db__():

    try:
        conn.execute("CREATE NODE TABLE State(id STRING, step_type STRING, payload STRING, PRIMARY KEY (id))") #
        
        # Create the directional relationship table
        conn.execute("CREATE REL TABLE TRANSITIONED_TO(FROM State TO State)") #
        logger.info("Celebi timeline initialized successfully.")
    except RuntimeError:
        logger.error("Time line schema exists, moving to rewind")
    
    return conn

if __name__ == "__main__":
    __init_db__()