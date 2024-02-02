from typing import Literal

from pydantic import BaseModel


class HealthcheckResponse(BaseModel):
    ok: Literal[True]
