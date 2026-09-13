from fastapi import FastAPI, Query
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

@app.get("/search")
def search_conversations(q: str = Query(..., min_length=1)):
    """Search across all prompt/response payloads for matching text."""
    try:
        result = conn.execute(
            "MATCH (n:State) WHERE n.payload CONTAINS $q RETURN n.id, n.step_type, n.payload",
            {"q": q},
        )

        matches = []
        while result.has_next():
            row = result.get_next()
            nid, ntype, payload = row
            matches.append({
                "node_id": nid,
                "step_type": ntype,
                "payload": payload or "",
            })

        return JSONResponse({"query": q, "count": len(matches), "results": matches})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/node/{node_id}")
def get_node(node_id: str):
    """Return full details for a single node."""
    try:
        result = conn.execute(
            "MATCH (n:State) WHERE n.id = $id RETURN n.id, n.step_type, n.payload",
            {"id": node_id},
        )

        if not result.has_next():
            return JSONResponse({"error": "Node not found"}, status_code=404)

        row = result.get_next()
        nid, ntype, payload = row
        return JSONResponse({
            "node_id": nid,
            "step_type": ntype,
            "payload": payload or "",
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/analytics")
def get_analytics():
    """Return token usage analytics extracted from response payloads."""
    try:
        result = conn.execute(
            "MATCH (n:State) WHERE n.step_type = 'response' RETURN n.id, n.payload"
        )

        total_prompt_tokens = 0
        total_completion_tokens = 0
        request_count = 0
        per_request = []

        while result.has_next():
            row = result.get_next()
            nid, payload = row
            if not payload:
                continue

            request_count += 1
            req_prompt = 0
            req_completion = 0

            for chunk in payload.split("data: "):
                chunk = chunk.strip()
                if not chunk or chunk == "[DONE]":
                    continue
                try:
                    import json as _json
                    d = _json.loads(chunk)
                    usage = d.get("usage")
                    if usage:
                        req_prompt = usage.get("prompt_tokens", 0)
                        req_completion = usage.get("completion_tokens", 0)
                except Exception:
                    pass

            total_prompt_tokens += req_prompt
            total_completion_tokens += req_completion
            per_request.append({
                "node_id": nid[:12],
                "prompt_tokens": req_prompt,
                "completion_tokens": req_completion,
                "total_tokens": req_prompt + req_completion,
            })

        return JSONResponse({
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_prompt_tokens + total_completion_tokens,
            "request_count": request_count,
            "per_request": per_request,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)