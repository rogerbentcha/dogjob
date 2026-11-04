from fastapi import APIRouter

router = APIRouter()


@router.get("/auth")
def auth() -> dict[str, str]:
    print("check auth")
    return {"status": "ok"}
