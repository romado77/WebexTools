import json
import time
from http import HTTPStatus
from urllib.parse import urlparse

import httpx

from webextools.helper import debug, prompt_proxy_credentials, verbose
from webextools.settings import DEFAULT_BASE_URL


class RateLimit(Exception):
    """API rate limit exceeded."""

    def __init__(self, url: str, retry_after: int):
        self.url = url
        self.retry_after = retry_after


class ProxyAuthenticationRequired(Exception):
    """Proxy authentication required."""


class Session:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        authorization: str = "",
        max_retries: int = 6,
        **params,
    ):
        """
        Initialize the Session object.

        :param base_url: base URL for the requests
        :param authorization: authorization token
        :param max_retries: maximum number of retries
        :param params: additional parameters to pass to the HTTPx client
        """
        self.base_url = base_url
        self.max_retries = max_retries
        self.params = params if params else {}

        if "timeout" not in self.params:
            self.params["timeout"] = 10

        if authorization:
            self.params["headers"] = {"Authorization": authorization}

    def get(self, url: str, **kwargs):
        """
        Make a GET request.

        :param url: URL to make the request
        :param kwargs: additional arguments to pass to the request
        """
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        """
        Make a POST request.

        :param url: URL to make the request
        :param kwargs: additional arguments to pass to the request
        """
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        """
        Make a PUT request.

        :param url: URL to make the request
        :param kwargs: additional arguments to pass to the request
        """
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs):
        """
        Make a DELETE request.

        :param url: URL to make the request
        :param kwargs: additional arguments to pass to the request
        """
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs):
        """
        Make a PATCH request.

        :param url: URL to make the request
        :param kwargs: additional arguments to pass to the request
        """
        return self.request("PATCH", url, **kwargs)

    def request(self, method: str, url: str, **params) -> httpx.Response:
        """
        Make an HTTP request.

        :param method: HTTP method (GET, POST, PUT, DELETE, PATCH)
        :param url: URL to make the request
        :param max_retries: maximum number of retries
        :param params: additional arguments to pass to the request

        :return: HTTP response
        :raises: httpx.RequestError, httpx.HTTPStatusError
        """
        retries = 0

        with httpx.Client(**self.params) as client:
            while retries <= self.max_retries and url:
                try:
                    response = client.request(method, self.normalize_url(url), **params)
                    debug(f"Request URL: {response.request.url}")
                    verbose(f"Request: {response.request.method} {response.request.url}")
                    verbose(
                        f"Request headers: {json.dumps(dict(response.request.headers), indent=2)}"
                    )

                    print()

                    verbose(f"Response: {response.status_code}")
                    verbose(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")

                    self.process_response(response)

                    yield response

                    if link_header := response.headers.get("Link"):
                        links = httpx._utils.parse_header_links(link_header)

                        for link in links:
                            if link["rel"] == "next":
                                url = link["url"]
                                continue

                    url = None

                except RateLimit as err:
                    verbose(
                        (
                            "Received 429 Too Many Requests. ",
                            f"Retrying after {err.retry_after} seconds... ",
                            f"(Attempt {retries + 1}/{self.max_retries + 1})",
                        )
                    )

                    time.sleep(err.retry_after)
                    retries = retries + 1
                except ProxyAuthenticationRequired:
                    username, password = prompt_proxy_credentials()
                    self.params["headers"]["Proxy-Authorization"] = httpx.BasicAuth(
                        username, password
                    )
                    retries = retries + 1
                except httpx.RequestError as err:
                    debug(
                        f"An error occurred while requesting URL: {err.request.url}, error: {err}",
                    )
                    raise err
                except httpx.HTTPStatusError as err:
                    debug(
                        f"An error occurred while requesting URL: {err.request.url}, error: {err.response.status_code}",
                    )
                    raise err

    def normalize_url(self, url: str) -> str:
        """
        Normalize the URL.

        :param url: URL to normalize

        :return: normalized URL
        """
        if not urlparse(url).scheme or not url.startswith(urlparse(url).scheme):
            url = f"{self.base_url}/{url}"

        return url

    def process_response(self, response: httpx.Response) -> None:
        """
        Process the HTTP response.

        :param response: HTTP response

        :raises: NextPage, RateLimit if the response requires further processing
        """
        if response.cookies:
            if "cookies" in self.params:
                self.params["cookies"].update(response.cookies)
            else:
                self.params["cookies"] = response.cookies

        if response.status_code in (
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT,
        ):
            debug("Request successful")
            return

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            raise RateLimit(response.url, int(response.headers.get("Retry-After", 15)))
        if response.status_code == HTTPStatus.PROXY_AUTHENTICATION_REQUIRED:
            raise ProxyAuthenticationRequired()

        response.raise_for_status()
