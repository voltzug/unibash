from typing import Any, Dict, Optional

import requests
from executor.interfaces import IHttpExecutor


class PureHttpExecutor(IHttpExecutor):
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        res = requests.get(url, headers=headers)
        return res.text

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ) -> Any:
        res = requests.post(url, headers=headers, data=body)
        return res.text

    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ) -> Any:
        res = requests.put(url, headers=headers, data=body)
        return res.text

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        res = requests.delete(url, headers=headers)
        return res.text

    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ) -> Any:
        res = requests.patch(url, headers=headers, data=body)
        return res.text
