from fastapi import FastAPI

app = FastAPI(docs_url=None, redoc_url=None)

@app.get("/")
def home():
    print("feature1 new")
    return {"message": "Hello World"}
