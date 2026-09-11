from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.router.interceptor import router as interceptor_router
from app.config.db import conn

app = FastAPI(title="celebi-harness")
app.include_router(interceptor_router)

@app.get("/")
def send_hello():
    return {"message": "Hello Traveller"}

@app.get("/graph")
def get_graph():
    """Return all graph edges for visualization."""
    try:
        result = conn.execute("""
            MATCH (a:State)-[e]->(b:State)
            RETURN a.id, a.step_type, LABEL(e), b.step_type, b.id,
                   a.payload, b.payload
        """)

        edges = []
        node_ids = set()

        while result.has_next():
            row = result.get_next()
            sid, stype, etype, ttype, tid, spayload, tpayload = row
            node_ids.add(sid)
            node_ids.add(tid)
            edges.append({
                "source_id": sid,
                "source_type": stype,
                "edge_type": etype,
                "target_type": ttype,
                "target_id": tid,
                "source_payload": spayload or "",
                "target_payload": tpayload or "",
            })

        return JSONResponse({
            "nodes": len(node_ids),
            "edges": len(edges),
            "data": edges,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)