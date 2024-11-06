import secrets

from fastapi import FastAPI

app = FastAPI()


@app.get("/api/test")
async def reply_square():
    return {"num": secrets.randbelow(11) ** 2}
