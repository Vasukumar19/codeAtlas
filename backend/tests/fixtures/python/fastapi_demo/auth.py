from fastapi import APIRouter

router = APIRouter(prefix="/auth")

class AuthService:
    def login(self, username, password):
        return {"token": "fake-jwt"}

@router.post("/login")
def login_route(username: str):
    service = AuthService()
    return service.login(username, "pass")
