"""Tester for BrregClient."""

import re

import pytest
from pytest_httpx import HTTPXMock

from brreg_scraper.client import BrregClient
from brreg_scraper.models import Enhet, Underenhet


# Eksempel API-respons
SAMPLE_ENHET = {
    "organisasjonsnummer": "123456789",
    "navn": "Test Selskap AS",
    "organisasjonsform": {
        "kode": "AS",
        "beskrivelse": "Aksjeselskap"
    },
    "forretningsadresse": {
        "land": "Norge",
        "landkode": "NO",
        "postnummer": "0123",
        "poststed": "OSLO",
        "adresse": ["Testveien 1"],
        "kommune": "OSLO",
        "kommunenummer": "0301"
    },
    "epostadresse": "post@testselskap.no",
    "telefon": "12345678",
    "hjemmeside": "https://testselskap.no",
    "antallAnsatte": 10
}

SAMPLE_SEARCH_RESPONSE = {
    "_embedded": {
        "enheter": [SAMPLE_ENHET]
    },
    "page": {
        "totalElements": 1,
        "totalPages": 1,
        "size": 100,
        "number": 0
    }
}


def test_get_enhet(httpx_mock: HTTPXMock):
    """Test henting av enkelt enhet."""
    httpx_mock.add_response(
        url="https://data.brreg.no/enhetsregisteret/api/enheter/123456789",
        json=SAMPLE_ENHET
    )

    with BrregClient() as client:
        enhet = client.get("123456789")

    assert enhet is not None
    assert enhet.organisasjonsnummer == "123456789"
    assert enhet.navn == "Test Selskap AS"
    assert enhet.epostadresse == "post@testselskap.no"
    assert enhet.organisasjonsform.kode == "AS"


def test_get_enhet_not_found(httpx_mock: HTTPXMock):
    """Test at None returneres for ukjent orgnr."""
    httpx_mock.add_response(
        url="https://data.brreg.no/enhetsregisteret/api/enheter/000000000",
        status_code=404
    )

    with BrregClient() as client:
        enhet = client.get("000000000")

    assert enhet is None


def test_search(httpx_mock: HTTPXMock):
    """Test sok etter enheter."""
    httpx_mock.add_response(
        url=re.compile(r"https://data\.brreg\.no/enhetsregisteret/api/enheter.*"),
        json=SAMPLE_SEARCH_RESPONSE
    )

    with BrregClient() as client:
        enheter = list(client.search(organisasjonsform=["AS"]))

    assert len(enheter) == 1
    assert enheter[0].organisasjonsnummer == "123456789"


def test_count(httpx_mock: HTTPXMock):
    """Test telling av enheter."""
    httpx_mock.add_response(
        url=re.compile(r"https://data\.brreg\.no/enhetsregisteret/api/enheter.*"),
        json={
            "_embedded": {"enheter": []},
            "page": {"totalElements": 42}
        }
    )

    with BrregClient() as client:
        count = client.count(organisasjonsform=["AS"])

    assert count == 42


def test_model_validation():
    """Test at Enhet-modellen validerer korrekt."""
    enhet = Enhet.model_validate(SAMPLE_ENHET)

    assert enhet.organisasjonsnummer == "123456789"
    assert enhet.navn == "Test Selskap AS"
    assert enhet.epostadresse == "post@testselskap.no"
    assert enhet.forretningsadresse is not None
    assert enhet.forretningsadresse.kommune == "OSLO"
    assert enhet.kommune_navn() == "OSLO"
    assert enhet.kommunenummer() == "0301"
    assert enhet.antallAnsatte == 10


# Underenhet tester

SAMPLE_UNDERENHET = {
    "organisasjonsnummer": "987654321",
    "navn": "Test Butikk Gronland",
    "organisasjonsform": {
        "kode": "BEDR",
        "beskrivelse": "Bedrift"
    },
    "overordnetEnhet": "123456789",
    "beliggenhetsadresse": {
        "land": "Norge",
        "landkode": "NO",
        "postnummer": "0187",
        "poststed": "OSLO",
        "adresse": ["Gronlandsleiret 5"],
        "kommune": "OSLO",
        "kommunenummer": "0301"
    },
    "oppstartsdato": "2020-01-15",
    "antallAnsatte": 5
}

SAMPLE_UNDERENHET_SEARCH_RESPONSE = {
    "_embedded": {
        "underenheter": [SAMPLE_UNDERENHET]
    },
    "page": {
        "totalElements": 1,
        "totalPages": 1,
        "size": 100,
        "number": 0
    }
}


def test_get_underenhet(httpx_mock: HTTPXMock):
    """Test henting av enkelt underenhet."""
    httpx_mock.add_response(
        url="https://data.brreg.no/enhetsregisteret/api/underenheter/987654321",
        json=SAMPLE_UNDERENHET
    )

    with BrregClient() as client:
        underenhet = client.get_underenhet("987654321")

    assert underenhet is not None
    assert underenhet.organisasjonsnummer == "987654321"
    assert underenhet.navn == "Test Butikk Gronland"
    assert underenhet.overordnetEnhet == "123456789"
    assert underenhet.organisasjonsform.kode == "BEDR"


def test_search_underenheter(httpx_mock: HTTPXMock):
    """Test sok etter underenheter."""
    httpx_mock.add_response(
        url=re.compile(r"https://data\.brreg\.no/enhetsregisteret/api/underenheter.*"),
        json=SAMPLE_UNDERENHET_SEARCH_RESPONSE
    )

    with BrregClient() as client:
        underenheter = list(client.search_underenheter(overordnetEnhet="123456789"))

    assert len(underenheter) == 1
    assert underenheter[0].organisasjonsnummer == "987654321"
    assert underenheter[0].overordnetEnhet == "123456789"


def test_underenhet_model_validation():
    """Test at Underenhet-modellen validerer korrekt."""
    underenhet = Underenhet.model_validate(SAMPLE_UNDERENHET)

    assert underenhet.organisasjonsnummer == "987654321"
    assert underenhet.navn == "Test Butikk Gronland"
    assert underenhet.overordnetEnhet == "123456789"
    assert underenhet.beliggenhetsadresse is not None
    assert underenhet.beliggenhetsadresse.kommune == "OSLO"
    assert underenhet.kommune_navn() == "OSLO"
    assert underenhet.antallAnsatte == 5
