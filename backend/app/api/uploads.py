from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.security import get_current_user
from app.models.auth import User
from app.services.upload_service import save_upload


router = APIRouter(prefix='/api/v1/uploads', tags=['uploads'])


@router.post('')
def upload_file(
    file: UploadFile = File(...),
    category: Literal['generic', 'member-photo'] = Form(default='generic'),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        result = save_upload(file, category=category)
        return {'uploaded_by': current_user.username, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
