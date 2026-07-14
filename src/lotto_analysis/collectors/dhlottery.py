"""Single-draw collector backed by the official Donghaeng Lottery website."""

from datetime import datetime, timezone
from html.parser import HTMLParser
import logging
import time
from typing import Any, Callable, Mapping, Optional

import requests

from lotto_analysis.collectors.base import (
    CollectorConnectionError,
    DrawCollector,
    DrawNotFoundError,
    ResponseFormatError,
)
from lotto_analysis.config import Settings
from lotto_analysis.models import LottoDraw
from lotto_analysis.storage.raw_json import RawJsonStore


LOGGER = logging.getLogger(__name__)
RESULT_PATH = "/lt645/selectPstLt645InfoNew.do"
RESULT_PAGE_PATH = "/lt645/result"


class DhlotteryDrawCollector(DrawCollector):
    """Collect one normalized draw from the official lottery result endpoint."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        session: Optional[requests.Session] = None,
        raw_store: Optional[RawJsonStore] = None,
        now: Optional[Callable[[], datetime]] = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        resolved_settings = settings or Settings.from_env()
        if resolved_settings.request_timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self._base_url = resolved_settings.source_base_url
        self._timeout_seconds = resolved_settings.request_timeout_seconds
        self._max_retries = resolved_settings.request_max_retries
        self._retry_backoff_seconds = (
            resolved_settings.request_retry_backoff_seconds
        )
        self._user_agent = resolved_settings.user_agent
        self._session = session or requests.Session()
        self._raw_store = raw_store
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._sleep = sleep

    def collect_draw(self, draw_number: int) -> LottoDraw:
        """Fetch and normalize exactly one requested draw."""
        if isinstance(draw_number, bool) or not isinstance(draw_number, int):
            raise ValueError("draw_number must be an integer")
        if draw_number <= 0:
            raise ValueError("draw_number must be positive")

        LOGGER.info("Collecting Lotto draw %s from the official source", draw_number)
        payload = self._request(draw_number)
        item = self._find_draw(payload, draw_number)
        if self._raw_store is not None:
            self._raw_store.save(draw_number, item)
        return self._to_model(item)

    def get_latest_draw_number(self) -> int:
        """Return the latest completed draw number shown by the official page."""
        response = self._get_with_retry(
            self._base_url + RESULT_PAGE_PATH,
            headers={"User-Agent": self._user_agent},
            context="the official result page",
        )

        parser = _LatestDrawParser()
        try:
            parser.feed(response.text)
        except (TypeError, ValueError) as exc:
            raise ResponseFormatError("Official result page is invalid HTML") from exc
        if parser.draw_number is None:
            raise ResponseFormatError(
                "Official result page does not contain the latest draw number"
            )
        return parser.draw_number

    def _request(self, draw_number: int) -> Mapping[str, Any]:
        response = self._get_with_retry(
            self._base_url + RESULT_PATH,
            params={"srchDir": "center", "srchLtEpsd": str(draw_number)},
            headers={"Accept": "application/json", "User-Agent": self._user_agent},
            context="draw {0}".format(draw_number),
        )

        try:
            payload = response.json()
        except ValueError as exc:
            raise ResponseFormatError("Official source returned invalid JSON") from exc

        if not isinstance(payload, Mapping):
            raise ResponseFormatError("Official source JSON must be an object")
        return payload

    def _get_with_retry(
        self,
        url: str,
        context: str,
        params: Optional[Mapping[str, str]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> requests.Response:
        """GET one official resource and retry only transient failures."""
        last_error: Optional[requests.RequestException] = None
        attempts_made = 0
        for attempt in range(self._max_retries + 1):
            attempts_made = attempt + 1
            try:
                response = self._session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self._timeout_seconds,
                )
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= self._max_retries or not _is_retryable(exc):
                    break
                delay = self._retry_backoff_seconds * (2 ** attempt)
                LOGGER.warning(
                    "Transient error requesting %s; retry %s/%s in %.2fs",
                    context,
                    attempt + 1,
                    self._max_retries,
                    delay,
                )
                if delay:
                    self._sleep(delay)

        raise CollectorConnectionError(
            "Failed to request {0} from the official source after {1} attempt(s)".format(
                context, attempts_made
            )
        ) from last_error

    @staticmethod
    def _find_draw(
        payload: Mapping[str, Any], draw_number: int
    ) -> Mapping[str, Any]:
        data = payload.get("data")
        if not isinstance(data, Mapping):
            raise ResponseFormatError("Response is missing the data object")
        items = data.get("list")
        if not isinstance(items, list):
            raise ResponseFormatError("Response is missing the draw list")

        for item in items:
            if not isinstance(item, Mapping):
                raise ResponseFormatError("Draw list contains a non-object item")
            try:
                item_draw_number = _required_int(item, "ltEpsd")
            except ResponseFormatError as exc:
                raise ResponseFormatError("Draw item is missing its number") from exc
            if item_draw_number == draw_number:
                return item

        raise DrawNotFoundError(
            "Draw {0} was not found in the official response".format(draw_number)
        )

    def _to_model(self, item: Mapping[str, Any]) -> LottoDraw:
        try:
            numbers = tuple(
                _required_int(item, "tm{0}WnNo".format(index))
                for index in range(1, 7)
            )
            draw_date = datetime.strptime(
                _required_text(item, "ltRflYmd"), "%Y%m%d"
            ).date()
            return LottoDraw(
                draw_number=_required_int(item, "ltEpsd"),
                draw_date=draw_date,
                numbers=numbers,  # type: ignore[arg-type]
                bonus_number=_required_int(item, "bnsWnNo"),
                first_prize_winners=_required_int(item, "rnk1WnNope"),
                first_prize_amount=_required_int(item, "rnk1WnAmt"),
                total_sales_amount=_required_int(item, "wholEpsdSumNtslAmt"),
                collected_at=self._now(),
            )
        except (TypeError, ValueError) as exc:
            raise ResponseFormatError(
                "Official draw data failed normalization"
            ) from exc


def _required_int(item: Mapping[str, Any], field: str) -> int:
    """Return one required integer field without accepting booleans."""
    value = item.get(field)
    if isinstance(value, bool):
        raise ResponseFormatError("Field {0} must be an integer".format(field))
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ResponseFormatError("Field {0} must be an integer".format(field)) from exc


def _required_text(item: Mapping[str, Any], field: str) -> str:
    """Return one required non-empty text field."""
    value = item.get(field)
    if not isinstance(value, str) or not value:
        raise ResponseFormatError("Field {0} must be non-empty text".format(field))
    return value


class _LatestDrawParser(HTMLParser):
    """Extract the latest draw number from the official result page."""

    def __init__(self) -> None:
        super().__init__()
        self.draw_number: Optional[int] = None

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag != "input":
            return
        attributes = dict(attrs)
        if attributes.get("id") != "opt_val":
            return
        value = attributes.get("value")
        try:
            draw_number = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("latest draw value must be an integer") from exc
        if draw_number <= 0:
            raise ValueError("latest draw value must be positive")
        self.draw_number = draw_number


def _is_retryable(exc: requests.RequestException) -> bool:
    """Return whether a request error is likely to be temporary."""
    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        status_code = exc.response.status_code
        return status_code == 429 or status_code >= 500
    return False
