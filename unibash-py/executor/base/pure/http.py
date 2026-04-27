from typing import Any, Dict, Optional

import httpx
from executor.interfaces import IHttpExecutor
from runtime.models import HttpResponse


class PureHttpExecutor(IHttpExecutor):
    def __init__(
        self,
        timeout: Optional[float] = 10.0,
        verify: Optional[bool] = True,
        follow_redirects: Optional[bool] = True,
    ):
        self.default_timeout = timeout
        self.default_verify = verify
        self.default_follow_redirects = follow_redirects

    def _request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        res = httpx.request(
            method,
            url,
            headers=headers,
            data=body,
            timeout=self.default_timeout if timeout is None else timeout,
            verify=self.default_verify if verify is None else verify,
            follow_redirects=(
                self.default_follow_redirects
                if follow_redirects is None
                else follow_redirects
            ),
        )
        return HttpResponse(
            status_code=res.status_code,
            headers=dict(res.headers),
            text=res.text,
        )

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self._request(
            "GET",
            url,
            headers=headers,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
        )

    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self._request(
            "HEAD",
            url,
            headers=headers,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
        )

    def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self._request(
            "POST",
            url,
            headers=headers,
            body=body,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
        )

    def put(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self._request(
            "PUT",
            url,
            headers=headers,
            body=body,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
        )

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self._request(
            "DELETE",
            url,
            headers=headers,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
        )

    def patch(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: Optional[float] = None,
        verify: Optional[bool] = None,
        follow_redirects: Optional[bool] = None,
    ) -> Any:
        return self._request(
            "PATCH",
            url,
            headers=headers,
            body=body,
            timeout=timeout,
            verify=verify,
            follow_redirects=follow_redirects,
        )
