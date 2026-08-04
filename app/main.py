from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def inicio():
    return {"message": "Hola"}

@app.get("/health")
def health():
    return {"status": "ok"}