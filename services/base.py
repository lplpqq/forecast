from typing import Optional

from requests import Session, RequestException


class Requestor:
    def __init__(self,
                 api_key: str,
                 base_endpoint_url: str,
                 session: Session):
        self.api_key = api_key
        self.base_endpoint_url = base_endpoint_url
        self.session = session

    def _request(
            self,
            path: str,
            *,
            method: str,
            **kwargs
    ):
        if not path.startswith("https://"):
            path = self.base_endpoint_url + path

        try:
            resp = self.session.request(
                method,
                path,
                **kwargs
            )
            resp.raise_for_status()
            return resp
        except RequestException as e:
            raise e

    def _get(self, path: str, **kwargs):
        return self._request(path, method="GET", **kwargs).json()

    def _post(self, path: str, **kwargs):
        return self._request(path, method="POST", **kwargs).json()
