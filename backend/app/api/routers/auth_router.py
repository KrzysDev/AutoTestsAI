from fastapi import APIRouter, Depends, HTTPException
from backend.app.services.auth_service import AuthService
from backend.app.dependencies import get_auth_service
from backend.app.models.schemas import UserRegister, UserLogin

router = APIRouter(prefix="/v1/auth", tags=["auth"])

@router.post("/login")
async def login(request: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    success = await auth_service.login(request.email, request.password)
    
    if not success:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {"message": "Login successful", "success": True}

@router.post("/register")
async def register(request: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    try:
        response = await auth_service.register(request.username, request.email, request.password)
        return {"message": "User registered successfully", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

