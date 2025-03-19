from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def home():
    print("Homepage")
    return {"message" : "homepage"}