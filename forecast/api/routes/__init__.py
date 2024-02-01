from fastapi import APIRouter

from forecast.api.models.healthcheck import HealthcheckResponse
from forecast.api.routes.weather import router as history_router

root_router = APIRouter()


@root_router.get('/')
async def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(ok=True)


routers = [history_router]
for router in routers:
    root_router.include_router(router)
