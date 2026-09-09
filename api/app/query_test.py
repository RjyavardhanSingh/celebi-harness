import kuzu
from pathlib import Path

def check_timeline():
    BASE_DIR = Path(__file__).resolve().parent
    DB_PATH = str(BASE_DIR/"kuzu.db")

    db = kuzu.Database(DB_PATH, read_only=True)
    conn = kuzu.Connection(db)
    print("Querying....................")

    query = """
        MATCH (p:State)-[:TRANSITIONED_TO]->(r:State) 
        RETURN p.id AS Prompt_ID, p.step_type, r.step_type, r.id AS Response_ID
"""

    result = conn.execute(query)

    df = result.get_as_df() #format as pandas data frame

    print(df)

if __name__ == "__main__":
    check_timeline()