import uvicorn
from fastapi import FastAPI

from forecast.api.routes import root_router
from forecast.config import config
from forecast.logging import logger_provider

logger = logger_provider(__name__)

app = FastAPI()

logger.info('Including the root router')
app.include_router(root_router)


if __name__ == '__main__':
    uvicorn.run(
        'forecast.api.__main__:app',
        host=config.api.host,
        port=config.api.port,
        reload=True,
    )
