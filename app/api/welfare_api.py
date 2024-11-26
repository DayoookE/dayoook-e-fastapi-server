# app/api/welfare_api.py
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel
from typing import List
from app.services.welfare_service import WelfareService
from app.utils.security import get_current_user
router = APIRouter(prefix="/api/welfare", tags=["welfare"])


class WelfareInfo(BaseModel):
    title: str
    content: str
    start_date: str
    end_date: str
    organization: str
    status: str
    detail_url: str


@router.get("/info", response_model=List[WelfareInfo])
async def get_welfare_info(request: Request,
                           page: int = Query(default=1, ge=1, description="페이지 번호"),
                           email: str = Depends(get_current_user)):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        service = WelfareService()
        return await service.fetch_welfare_info(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))