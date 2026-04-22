from fastapi import FastAPI

from .control_router import router as control_router
from .monitoring_router import router as monitoring_router

app = FastAPI(
    title="TurbinControl API",
    description="Wind turbine monitoring and control system",
    version="0.1.0",
)

app.include_router(monitoring_router)
app.include_router(control_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
