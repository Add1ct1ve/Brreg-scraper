"""Pydantic datamodeller for Bronnøysund API-responser."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Adresse(BaseModel):
    """Adressemodell for post- og forretningsadresser."""

    land: Optional[str] = None
    landkode: Optional[str] = None
    postnummer: Optional[str] = None
    poststed: Optional[str] = None
    adresse: Optional[list[str]] = None
    kommune: Optional[str] = None
    kommunenummer: Optional[str] = None

    def formatted(self) -> str:
        """Returner formatert adresse som en streng."""
        parts = []
        if self.adresse:
            parts.extend(self.adresse)
        if self.postnummer and self.poststed:
            parts.append(f"{self.postnummer} {self.poststed}")
        return ", ".join(parts)


class Organisasjonsform(BaseModel):
    """Organisasjonsform med kode og beskrivelse."""

    kode: str
    beskrivelse: Optional[str] = None


class Enhet(BaseModel):
    """Hovedmodell for en enhet fra Bronnøysundregistrene."""

    organisasjonsnummer: str
    navn: str
    organisasjonsform: Organisasjonsform
    registreringsdatoEnhetsregisteret: Optional[date] = None
    registrertIMvaregisteret: Optional[bool] = None
    frivilligMvaRegistrertBeskrivelser: Optional[list[str]] = None
    naeringskode1: Optional[dict] = None
    antallAnsatte: Optional[int] = None
    hjemmeside: Optional[str] = None
    forretningsadresse: Optional[Adresse] = None
    postadresse: Optional[Adresse] = None
    stiftelsesdato: Optional[date] = None
    institusjonellSektorkode: Optional[dict] = None
    registrertIForetaksregisteret: Optional[bool] = None
    registrertIStiftelsesregisteret: Optional[bool] = None
    registrertIFrivillighetsregisteret: Optional[bool] = None
    konkurs: Optional[bool] = None
    underAvvikling: Optional[bool] = None
    underTvangsavviklingEllerTvangsopplosning: Optional[bool] = None
    maalform: Optional[str] = None
    vedtektsfestetFormaal: Optional[list[str]] = None
    aktivitet: Optional[list[str]] = None

    # Kontaktinformasjon
    epostadresse: Optional[str] = None
    telefon: Optional[str] = None
    mobil: Optional[str] = None  # Separat fra telefon!

    # Kapital (for AS/ASA)
    kapital: Optional[dict] = None  # {belop, antallAksjer, valuta, type, innbetalt, fulltInnbetalt}

    # Regnskap
    sisteInnsendteAarsregnskap: Optional[str] = None  # År (f.eks. "2024")

    # Datoer
    vedtektsdato: Optional[date] = None
    registreringsdatoForetaksregisteret: Optional[date] = None
    registreringsdatoMerverdiavgiftsregisteret: Optional[date] = None
    fravalgRevisjonDato: Optional[date] = None

    # Hierarki og konsern
    overordnetEnhet: Optional[str] = None  # Orgnr til eierende enhet (KF, FKF, ORGL)
    erIKonsern: Optional[bool] = None

    # Utvidede naeringskoder
    naeringskode2: Optional[dict] = None
    naeringskode3: Optional[dict] = None

    # Ekstra registreringer
    registrertIPartiregisteret: Optional[bool] = None
    harRegistrertAntallAnsatte: Optional[bool] = None

    # Utenlandske enheter (NUF, UTLA)
    registreringsnummerIHjemlandet: Optional[str] = None
    foretaksformIHjemlandet: Optional[dict] = None  # {kode, beskrivelse}
    utenlandskRegisterNavn: Optional[str] = None
    utenlandskRegisterAdresse: Optional[Adresse] = None  # Adresse-objekt, ikke str
    underlagtLovgivningLand: Optional[str] = None
    underlagtLovgivningLandKode: Optional[str] = None

    # Linking-felt (dict fra API-et)
    links: Optional[dict] = Field(default=None, alias="_links")

    model_config = ConfigDict(populate_by_name=True)

    def kommune_navn(self) -> Optional[str]:
        """Hent kommunenavn fra forretningsadresse."""
        if self.forretningsadresse:
            return self.forretningsadresse.kommune
        return None

    def kommunenummer(self) -> Optional[str]:
        """Hent kommunenummer fra forretningsadresse."""
        if self.forretningsadresse:
            return self.forretningsadresse.kommunenummer
        return None


class Underenhet(BaseModel):
    """Modell for en underenhet/bedrift fra Bronnøysundregistrene."""

    organisasjonsnummer: str
    navn: str
    organisasjonsform: Organisasjonsform
    overordnetEnhet: str  # Orgnr til hovedenheten
    registreringsdatoEnhetsregisteret: Optional[date] = None
    oppstartsdato: Optional[date] = None  # Erstatter stiftelsesdato
    nedleggelsesdato: Optional[date] = None
    beliggenhetsadresse: Optional[Adresse] = None  # Erstatter forretningsadresse
    postadresse: Optional[Adresse] = None
    naeringskode1: Optional[dict] = None
    antallAnsatte: Optional[int] = None
    hjemmeside: Optional[str] = None

    # Kontaktinformasjon
    epostadresse: Optional[str] = None
    telefon: Optional[str] = None
    mobil: Optional[str] = None

    # Registreringer
    registrertIMvaregisteret: Optional[bool] = None
    frivilligMvaRegistrertBeskrivelser: Optional[list[str]] = None

    # Linking-felt
    links: Optional[dict] = Field(default=None, alias="_links")

    model_config = ConfigDict(populate_by_name=True)

    def kommune_navn(self) -> Optional[str]:
        """Hent kommunenavn fra beliggenhetsadresse."""
        if self.beliggenhetsadresse:
            return self.beliggenhetsadresse.kommune
        return None

    def kommunenummer(self) -> Optional[str]:
        """Hent kommunenummer fra beliggenhetsadresse."""
        if self.beliggenhetsadresse:
            return self.beliggenhetsadresse.kommunenummer
        return None


class EmbeddedEnheter(BaseModel):
    """Embedded enheter i sokeresultat."""

    enheter: list[Enhet] = []


class EmbeddedUnderenheter(BaseModel):
    """Embedded underenheter i sokeresultat."""

    underenheter: list[Underenhet] = []


class SearchResult(BaseModel):
    """Paginert sokeresultat fra API-et."""

    embedded: Optional[EmbeddedEnheter] = Field(default=None, alias="_embedded")
    page: Optional[dict] = None
    links: Optional[dict] = Field(default=None, alias="_links")

    model_config = ConfigDict(populate_by_name=True)

    @property
    def enheter(self) -> list[Enhet]:
        """Hent liste av enheter fra resultatet."""
        if self.embedded:
            return self.embedded.enheter
        return []

    @property
    def total_elements(self) -> int:
        """Hent totalt antall elementer."""
        if self.page:
            return self.page.get("totalElements", 0)
        return 0


class SearchResultUnderenheter(BaseModel):
    """Paginert sokeresultat for underenheter."""

    embedded: Optional[EmbeddedUnderenheter] = Field(default=None, alias="_embedded")
    page: Optional[dict] = None
    links: Optional[dict] = Field(default=None, alias="_links")

    model_config = ConfigDict(populate_by_name=True)

    @property
    def underenheter(self) -> list[Underenhet]:
        """Hent liste av underenheter fra resultatet."""
        if self.embedded:
            return self.embedded.underenheter
        return []

    @property
    def total_elements(self) -> int:
        """Hent totalt antall elementer."""
        if self.page:
            return self.page.get("totalElements", 0)
        return 0
