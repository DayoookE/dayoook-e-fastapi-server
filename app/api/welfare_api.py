# app/api/welfare_api.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from app.services.welfare_service import WelfareService

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
async def get_welfare_info(page: int = Query(default=1, ge=1, description="페이지 번호")):
    try:
        service = WelfareService()
        return await service.fetch_welfare_info(page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
