from fastapi import APIRouter, Depends

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.households import router as households_router
from app.api.members import router as members_router
from app.api.roles import router as roles_router
from app.api.search import router as search_router
from app.api.settings import router as settings_router
from app.api.uploads import router as uploads_router
from app.api.users import router as users_router
from app.api.villages import router as villages_router
from app.core.security import require_permission
from app.models.auth import User


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(uploads_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(villages_router)
api_router.include_router(households_router)
api_router.include_router(members_router)
api_router.include_router(search_router)
api_router.include_router(settings_router)


@api_router.get('/api/v1/dashboard', tags=['dashboard'])
def get_dashboard_placeholder(current_user: User = Depends(require_permission('member_view'))) -> dict:
    return {
        'message': '阶段 4 业务功能已就绪',
        'current_user': current_user.username,
    }
