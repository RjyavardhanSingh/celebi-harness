from fastapi import FastAPI
from app.router.interceptor import router as interceptor_router

app = FastAPI(title="celebi-harness")
app.include_router(interceptor_router)

@app.get("/")
def send_hello():
    return {"message": "Hello Traveller"}