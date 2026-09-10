import kuzu
from pathlib import Path

def check_timeline():
    BASE_DIR = Path(__file__).resolve().parent
    DB_PATH = str(BASE_DIR/"kuzu.db")

    db = kuzu.Database(DB_PATH, read_only=True)
    conn = kuzu.Connection(db)
    print("Querying....................")

    query = """
        MATCH (a:State)-[e]->(b:State) 
        RETURN a.id AS Source_ID, a.step_type AS source_type, LABEL(e) AS Edge, b.step_type AS target_type, b.id AS Target_ID
"""

    result = conn.execute(query)

    df = result.get_as_df() #format as pandas data frame

    print(df)

if __name__ == "__main__":
    check_timeline()