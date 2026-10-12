from fastapi import FastAPI

from app.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.environment = settings.environment


@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok", "method": "GET", "status_code": 200}
