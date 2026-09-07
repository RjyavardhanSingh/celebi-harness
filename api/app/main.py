from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def send_hello():
    return {"message": "Hello Traveller"}