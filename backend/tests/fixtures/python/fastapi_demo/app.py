from fastapi import FastAPI
from users import router as users_router
from auth import router as auth_router

app = FastAPI()

app.include_router(users_router)
app.include_router(auth_router)

@app.get("/health")
def health_check():
    # TODO: Add database check
    return {"status": "ok"}
