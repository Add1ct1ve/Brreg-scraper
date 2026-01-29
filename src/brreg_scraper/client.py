"""API-klient for Bronnøysundregistrene."""

import time
from collections.abc import Callable, Iterator
from typing import Any, Optional

import httpx

from brreg_scraper.models import Enhet, SearchResult, Underenhet, SearchResultUnderenheter
from brreg_scraper.regions import get_kommunenummer_list, get_fylke_kode


BASE_URL = "https://data.brreg.no/enhetsregisteret/api"
DEFAULT_TIMEOUT = 30.0
MAX_PAGE_SIZE = 100
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0


class BrregClient:
    """Klient for Bronnøysund Enhetsregisteret API."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=BASE_URL,
                timeout=self.timeout,
                headers={"Accept": "application/json"},
            )
        return self._client

    def close(self) -> None:
        """Lukk HTTP-klienten."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "BrregClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _request_with_retry(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Utfor request med retry-logikk."""
        client = self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 503:
                    last_error = e
                    wait_time = RETRY_BACKOFF ** attempt
                    time.sleep(wait_time)
                    continue
                raise
            except httpx.RequestError as e:
                last_error = e
                wait_time = RETRY_BACKOFF ** attempt
                time.sleep(wait_time)
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Unexpected error in retry loop")

    def get(self, orgnr: str) -> Optional[Enhet]:
        """Hent en enkelt enhet basert pa organisasjonsnummer."""
        try:
            data = self._request_with_retry(f"/enheter/{orgnr}", {})
            return Enhet.model_validate(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def search(
        self,
        organisasjonsform: Optional[list[str]] = None,
        kommunenummer: Optional[list[str]] = None,
        navn: Optional[str] = None,
        fraRegistreringsdatoEnhetsregisteret: Optional[str] = None,
        tilRegistreringsdatoEnhetsregisteret: Optional[str] = None,
        konkurs: Optional[bool] = None,
        size: int = MAX_PAGE_SIZE,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Iterator[Enhet]:
        """
        Sok etter enheter med paginering.

        Args:
            organisasjonsform: Liste med org.form-koder (f.eks. ["BRL", "ESEK"])
            kommunenummer: Liste med kommunenummer
            navn: Sok pa navn
            fraRegistreringsdatoEnhetsregisteret: Fra-dato (YYYY-MM-DD)
            tilRegistreringsdatoEnhetsregisteret: Til-dato (YYYY-MM-DD)
            konkurs: Filter pa konkursstatus
            size: Antall resultater per side (maks 100)
            progress_callback: Callback for progress (current, total)

        Yields:
            Enhet-objekter
        """
        params: dict[str, Any] = {
            "size": min(size, MAX_PAGE_SIZE),
        }

        if organisasjonsform:
            params["organisasjonsform"] = ",".join(organisasjonsform)
        if kommunenummer:
            params["kommunenummer"] = ",".join(kommunenummer)
        if navn:
            params["navn"] = navn
        if fraRegistreringsdatoEnhetsregisteret:
            params["fraRegistreringsdatoEnhetsregisteret"] = fraRegistreringsdatoEnhetsregisteret
        if tilRegistreringsdatoEnhetsregisteret:
            params["tilRegistreringsdatoEnhetsregisteret"] = tilRegistreringsdatoEnhetsregisteret
        if konkurs is not None:
            params["konkurs"] = str(konkurs).lower()

        fetched = 0
        total = None
        search_after: Optional[str] = None

        while True:
            if search_after:
                params["searchAfter"] = search_after

            data = self._request_with_retry("/enheter", params)
            result = SearchResult.model_validate(data)

            if total is None:
                total = result.total_elements

            for enhet in result.enheter:
                yield enhet
                fetched += 1

                if progress_callback and total:
                    progress_callback(fetched, total)

            # Sjekk om det er flere sider
            if not result.enheter:
                break

            # Hent searchAfter for neste side
            if result.links and "next" in result.links:
                next_link = result.links["next"]
                if isinstance(next_link, dict) and "href" in next_link:
                    href = next_link["href"]
                    # Parse searchAfter fra URL
                    if "searchAfter=" in href:
                        search_after = href.split("searchAfter=")[1].split("&")[0]
                    else:
                        break
                else:
                    break
            else:
                break

    def fetch_all(
        self,
        organisasjonsform: list[str],
        regions: Optional[list[str]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> list[Enhet]:
        """
        Hent alle enheter for gitte organisasjonsformer og regioner.

        Args:
            organisasjonsform: Liste med org.form-koder (f.eks. ["BRL", "ESEK"])
            regions: Liste med regionnavn (f.eks. ["oslo", "akershus"])
            progress_callback: Callback for progress (current, total)

        Returns:
            Liste med Enhet-objekter
        """
        kommunenummer: Optional[list[str]] = None
        if regions:
            fylke_koder = []
            for region in regions:
                kode = get_fylke_kode(region)
                if kode:
                    fylke_koder.append(kode)
            if fylke_koder:
                kommunenummer = get_kommunenummer_list(fylke_koder)

        return list(self.search(
            organisasjonsform=organisasjonsform,
            kommunenummer=kommunenummer,
            progress_callback=progress_callback,
        ))

    def count(
        self,
        organisasjonsform: Optional[list[str]] = None,
        kommunenummer: Optional[list[str]] = None,
    ) -> int:
        """Tell antall enheter som matcher kriteriene."""
        params: dict[str, Any] = {"size": 0}

        if organisasjonsform:
            params["organisasjonsform"] = ",".join(organisasjonsform)
        if kommunenummer:
            params["kommunenummer"] = ",".join(kommunenummer)

        data = self._request_with_retry("/enheter", params)
        result = SearchResult.model_validate(data)
        return result.total_elements

    # ==================== UNDERENHETER ====================

    def get_underenhet(self, orgnr: str) -> Optional[Underenhet]:
        """Hent en enkelt underenhet basert pa organisasjonsnummer."""
        try:
            data = self._request_with_retry(f"/underenheter/{orgnr}", {})
            return Underenhet.model_validate(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    def search_underenheter(
        self,
        overordnetEnhet: Optional[str] = None,
        kommunenummer: Optional[list[str]] = None,
        naeringskode: Optional[str] = None,
        navn: Optional[str] = None,
        size: int = MAX_PAGE_SIZE,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Iterator[Underenhet]:
        """
        Sok etter underenheter med paginering.

        Args:
            overordnetEnhet: Organisasjonsnummer til hovedenheten
            kommunenummer: Liste med kommunenummer
            naeringskode: Naeringskode (f.eks. "68.201")
            navn: Sok pa navn
            size: Antall resultater per side (maks 100)
            progress_callback: Callback for progress (current, total)

        Yields:
            Underenhet-objekter
        """
        params: dict[str, Any] = {
            "size": min(size, MAX_PAGE_SIZE),
        }

        if overordnetEnhet:
            params["overordnetEnhet"] = overordnetEnhet
        if kommunenummer:
            params["kommunenummer"] = ",".join(kommunenummer)
        if naeringskode:
            params["naeringskode"] = naeringskode
        if navn:
            params["navn"] = navn

        fetched = 0
        total = None
        search_after: Optional[str] = None

        while True:
            if search_after:
                params["searchAfter"] = search_after

            data = self._request_with_retry("/underenheter", params)
            result = SearchResultUnderenheter.model_validate(data)

            if total is None:
                total = result.total_elements

            for underenhet in result.underenheter:
                yield underenhet
                fetched += 1

                if progress_callback and total:
                    progress_callback(fetched, total)

            # Sjekk om det er flere sider
            if not result.underenheter:
                break

            # Hent searchAfter for neste side
            if result.links and "next" in result.links:
                next_link = result.links["next"]
                if isinstance(next_link, dict) and "href" in next_link:
                    href = next_link["href"]
                    if "searchAfter=" in href:
                        search_after = href.split("searchAfter=")[1].split("&")[0]
                    else:
                        break
                else:
                    break
            else:
                break

    def count_underenheter(
        self,
        overordnetEnhet: Optional[str] = None,
        kommunenummer: Optional[list[str]] = None,
    ) -> int:
        """Tell antall underenheter som matcher kriteriene."""
        params: dict[str, Any] = {"size": 0}

        if overordnetEnhet:
            params["overordnetEnhet"] = overordnetEnhet
        if kommunenummer:
            params["kommunenummer"] = ",".join(kommunenummer)

        data = self._request_with_retry("/underenheter", params)
        result = SearchResultUnderenheter.model_validate(data)
        return result.total_elements
