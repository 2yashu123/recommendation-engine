from fastapi import FastAPI

app = FastAPI(title="AI Recommendation Engine")

@app.get("/")
def read_root():
    return {"status": "ok"}
