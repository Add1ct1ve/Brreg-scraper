"""Eksportfunksjoner for Brreg-data."""

from pathlib import Path
from typing import Optional, Sequence

import pandas as pd

from brreg_scraper.models import Enhet, Underenhet


# Kolonne-presets for fleksibel eksport
COLUMN_PRESETS: dict[str, list[str] | None] = {
    "minimal": [
        "organisasjonsnummer",
        "navn",
        "organisasjonsform",
    ],
    "basic": [
        "organisasjonsnummer",
        "navn",
        "organisasjonsform",
        "adresse",
        "postnummer",
        "poststed",
        "kommune",
        "stiftelsesdato",
    ],
    "contact": [
        "organisasjonsnummer",
        "navn",
        "organisasjonsform",
        "epostadresse",
        "telefon",
        "mobil",
        "hjemmeside",
        "adresse",
        "postnummer",
        "poststed",
        "kommune",
    ],
    "financial": [
        "organisasjonsnummer",
        "navn",
        "organisasjonsform",
        "aksjekapital",
        "antall_ansatte",
        "siste_aarsregnskap",
        "naeringskode",
        "naeringskode_beskrivelse",
        "konkurs",
        "under_avvikling",
    ],
    "full": None,  # Alle kolonner
}


def get_columns_for_preset(preset: str) -> list[str] | None:
    """
    Hent kolonner for et preset.

    Args:
        preset: Navn pa preset (minimal, basic, contact, financial, full)

    Returns:
        Liste med kolonnenavn, eller None for alle kolonner.

    Raises:
        ValueError: Hvis preset ikke finnes.
    """
    if preset not in COLUMN_PRESETS:
        valid = ", ".join(COLUMN_PRESETS.keys())
        raise ValueError(f"Ukjent preset '{preset}'. Gyldige presets: {valid}")
    return COLUMN_PRESETS.get(preset)


def list_presets() -> dict[str, list[str] | None]:
    """Returner alle tilgjengelige presets."""
    return COLUMN_PRESETS.copy()


DEFAULT_COLUMNS = [
    "organisasjonsnummer",
    "navn",
    "organisasjonsform",
    "epostadresse",
    "telefon",
    "hjemmeside",
    "adresse",
    "postnummer",
    "poststed",
    "kommune",
    "kommunenummer",
    "stiftelsesdato",
    "antall_ansatte",
]


def enhet_to_dict(enhet: Enhet) -> dict:
    """Konverter en Enhet til flat dict for eksport."""
    # Hent forretningsadresse
    adresse = ""
    postnummer = ""
    poststed = ""
    kommune = ""
    kommunenummer = ""
    land = ""

    if enhet.forretningsadresse:
        addr = enhet.forretningsadresse
        if addr.adresse:
            adresse = ", ".join(addr.adresse)
        postnummer = addr.postnummer or ""
        poststed = addr.poststed or ""
        kommune = addr.kommune or ""
        kommunenummer = addr.kommunenummer or ""
        land = addr.land or ""
    elif enhet.postadresse:
        addr = enhet.postadresse
        if addr.adresse:
            adresse = ", ".join(addr.adresse)
        postnummer = addr.postnummer or ""
        poststed = addr.poststed or ""
        kommune = addr.kommune or ""
        kommunenummer = addr.kommunenummer or ""
        land = addr.land or ""

    # Hent postadresse (separat)
    post_adresse = ""
    post_postnummer = ""
    post_poststed = ""
    if enhet.postadresse:
        addr = enhet.postadresse
        if addr.adresse:
            post_adresse = ", ".join(addr.adresse)
        post_postnummer = addr.postnummer or ""
        post_poststed = addr.poststed or ""

    # Naeringskode
    naeringskode = ""
    naeringskode_beskrivelse = ""
    if enhet.naeringskode1:
        naeringskode = enhet.naeringskode1.get("kode", "")
        naeringskode_beskrivelse = enhet.naeringskode1.get("beskrivelse", "")

    # Kapital (for AS/ASA)
    aksjekapital = ""
    antall_aksjer = ""
    kapital_type = ""
    kapital_valuta = ""
    kapital_innbetalt = ""
    kapital_fullt_innbetalt = ""
    if enhet.kapital:
        aksjekapital = enhet.kapital.get("belop", "")
        antall_aksjer = enhet.kapital.get("antallAksjer", "")
        kapital_type = enhet.kapital.get("type", "")
        kapital_valuta = enhet.kapital.get("valuta", "")
        kapital_innbetalt = enhet.kapital.get("innbetalt", "")
        kapital_fullt_innbetalt = enhet.kapital.get("fulltInnbetalt", "")

    # Naeringskode 2 og 3
    naeringskode2 = ""
    naeringskode2_beskrivelse = ""
    if enhet.naeringskode2:
        naeringskode2 = enhet.naeringskode2.get("kode", "")
        naeringskode2_beskrivelse = enhet.naeringskode2.get("beskrivelse", "")

    naeringskode3 = ""
    naeringskode3_beskrivelse = ""
    if enhet.naeringskode3:
        naeringskode3 = enhet.naeringskode3.get("kode", "")
        naeringskode3_beskrivelse = enhet.naeringskode3.get("beskrivelse", "")

    # Institusjonell sektorkode
    sektorkode = ""
    sektorkode_beskrivelse = ""
    if enhet.institusjonellSektorkode:
        sektorkode = enhet.institusjonellSektorkode.get("kode", "")
        sektorkode_beskrivelse = enhet.institusjonellSektorkode.get("beskrivelse", "")

    # Utenlandsk foretaksform
    utenlandsk_foretaksform = ""
    if enhet.foretaksformIHjemlandet:
        utenlandsk_foretaksform = enhet.foretaksformIHjemlandet.get("beskrivelse", "")

    # Aktivitet/formal
    aktivitet = ""
    if enhet.aktivitet:
        aktivitet = " | ".join(enhet.aktivitet)
    elif enhet.vedtektsfestetFormaal:
        aktivitet = " | ".join(enhet.vedtektsfestetFormaal)

    return {
        "organisasjonsnummer": enhet.organisasjonsnummer,
        "navn": enhet.navn,
        "organisasjonsform": enhet.organisasjonsform.kode,
        "organisasjonsform_beskrivelse": enhet.organisasjonsform.beskrivelse or "",
        # Kontaktinfo
        "epostadresse": enhet.epostadresse or "",
        "telefon": enhet.telefon or "",
        "mobil": enhet.mobil or "",
        "hjemmeside": enhet.hjemmeside or "",
        # Forretningsadresse
        "adresse": adresse,
        "postnummer": postnummer,
        "poststed": poststed,
        "kommune": kommune,
        "kommunenummer": kommunenummer,
        "land": land,
        # Postadresse (separat)
        "postadresse": post_adresse,
        "postadresse_postnummer": post_postnummer,
        "postadresse_poststed": post_poststed,
        # Naeringskode
        "naeringskode": naeringskode,
        "naeringskode_beskrivelse": naeringskode_beskrivelse,
        # Aktivitet
        "aktivitet": aktivitet,
        # Datoer
        "stiftelsesdato": str(enhet.stiftelsesdato) if enhet.stiftelsesdato else "",
        "registreringsdato": str(enhet.registreringsdatoEnhetsregisteret) if enhet.registreringsdatoEnhetsregisteret else "",
        # Kapital (AS/ASA)
        "aksjekapital": aksjekapital,
        "antall_aksjer": antall_aksjer,
        "kapital_type": kapital_type,
        "kapital_valuta": kapital_valuta,
        "kapital_innbetalt": kapital_innbetalt,
        "kapital_fullt_innbetalt": kapital_fullt_innbetalt,
        # Regnskap
        "siste_aarsregnskap": enhet.sisteInnsendteAarsregnskap or "",
        # Ansatte
        "antall_ansatte": enhet.antallAnsatte if enhet.antallAnsatte is not None else "",
        # Status
        "konkurs": enhet.konkurs or False,
        "under_avvikling": enhet.underAvvikling or False,
        "under_tvangsavvikling": enhet.underTvangsavviklingEllerTvangsopplosning or False,
        # Registreringer
        "registrert_i_mva": enhet.registrertIMvaregisteret or False,
        "registrert_i_foretaksregisteret": enhet.registrertIForetaksregisteret or False,
        "registrert_i_frivillighetsregisteret": enhet.registrertIFrivillighetsregisteret or False,
        "registrert_i_stiftelsesregisteret": enhet.registrertIStiftelsesregisteret or False,
        "registrert_i_partiregisteret": enhet.registrertIPartiregisteret or False,
        "har_registrert_antall_ansatte": enhet.harRegistrertAntallAnsatte or False,
        # Utvidede naeringskoder
        "naeringskode2": naeringskode2,
        "naeringskode2_beskrivelse": naeringskode2_beskrivelse,
        "naeringskode3": naeringskode3,
        "naeringskode3_beskrivelse": naeringskode3_beskrivelse,
        # Klassifisering
        "sektorkode": sektorkode,
        "sektorkode_beskrivelse": sektorkode_beskrivelse,
        "maalform": enhet.maalform or "",
        "er_i_konsern": enhet.erIKonsern or False,
        # Hierarki
        "overordnet_enhet": enhet.overordnetEnhet or "",
        # Utvidede datoer
        "vedtektsdato": str(enhet.vedtektsdato) if enhet.vedtektsdato else "",
        "registreringsdato_foretaksregisteret": str(enhet.registreringsdatoForetaksregisteret) if enhet.registreringsdatoForetaksregisteret else "",
        "registreringsdato_mva": str(enhet.registreringsdatoMerverdiavgiftsregisteret) if enhet.registreringsdatoMerverdiavgiftsregisteret else "",
        "fravalg_revisjon_dato": str(enhet.fravalgRevisjonDato) if enhet.fravalgRevisjonDato else "",
        # Utenlandske enheter (NUF, UTLA)
        "registreringsnummer_i_hjemlandet": enhet.registreringsnummerIHjemlandet or "",
        "foretaksform_i_hjemlandet": utenlandsk_foretaksform,
        "utenlandsk_register_navn": enhet.utenlandskRegisterNavn or "",
        "utenlandsk_register_adresse": enhet.utenlandskRegisterAdresse.formatted() if enhet.utenlandskRegisterAdresse else "",
        "underlagt_lovgivning_land": enhet.underlagtLovgivningLand or "",
        "underlagt_lovgivning_landkode": enhet.underlagtLovgivningLandKode or "",
    }


def underenhet_to_dict(underenhet: Underenhet) -> dict:
    """Konverter en Underenhet til flat dict for eksport."""
    # Hent beliggenhetsadresse
    adresse = ""
    postnummer = ""
    poststed = ""
    kommune = ""
    kommunenummer = ""
    land = ""

    if underenhet.beliggenhetsadresse:
        addr = underenhet.beliggenhetsadresse
        if addr.adresse:
            adresse = ", ".join(addr.adresse)
        postnummer = addr.postnummer or ""
        poststed = addr.poststed or ""
        kommune = addr.kommune or ""
        kommunenummer = addr.kommunenummer or ""
        land = addr.land or ""
    elif underenhet.postadresse:
        addr = underenhet.postadresse
        if addr.adresse:
            adresse = ", ".join(addr.adresse)
        postnummer = addr.postnummer or ""
        poststed = addr.poststed or ""
        kommune = addr.kommune or ""
        kommunenummer = addr.kommunenummer or ""
        land = addr.land or ""

    # Naeringskode
    naeringskode = ""
    naeringskode_beskrivelse = ""
    if underenhet.naeringskode1:
        naeringskode = underenhet.naeringskode1.get("kode", "")
        naeringskode_beskrivelse = underenhet.naeringskode1.get("beskrivelse", "")

    return {
        "organisasjonsnummer": underenhet.organisasjonsnummer,
        "navn": underenhet.navn,
        "organisasjonsform": underenhet.organisasjonsform.kode,
        "organisasjonsform_beskrivelse": underenhet.organisasjonsform.beskrivelse or "",
        "overordnet_enhet": underenhet.overordnetEnhet,
        # Kontaktinfo
        "epostadresse": underenhet.epostadresse or "",
        "telefon": underenhet.telefon or "",
        "mobil": underenhet.mobil or "",
        "hjemmeside": underenhet.hjemmeside or "",
        # Beliggenhetsadresse
        "adresse": adresse,
        "postnummer": postnummer,
        "poststed": poststed,
        "kommune": kommune,
        "kommunenummer": kommunenummer,
        "land": land,
        # Naeringskode
        "naeringskode": naeringskode,
        "naeringskode_beskrivelse": naeringskode_beskrivelse,
        # Datoer
        "oppstartsdato": str(underenhet.oppstartsdato) if underenhet.oppstartsdato else "",
        "nedleggelsesdato": str(underenhet.nedleggelsesdato) if underenhet.nedleggelsesdato else "",
        "registreringsdato": str(underenhet.registreringsdatoEnhetsregisteret) if underenhet.registreringsdatoEnhetsregisteret else "",
        # Ansatte
        "antall_ansatte": underenhet.antallAnsatte if underenhet.antallAnsatte is not None else "",
        # Registreringer
        "registrert_i_mva": underenhet.registrertIMvaregisteret or False,
    }


def to_dataframe(
    enheter: Sequence[Enhet | Underenhet],
    columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Konverter liste med Enhet eller Underenhet til pandas DataFrame.

    Args:
        enheter: Liste med Enhet- eller Underenhet-objekter
        columns: Liste med kolonner som skal inkluderes (None = alle)

    Returns:
        pandas DataFrame
    """
    if not enheter:
        return pd.DataFrame()

    # Sjekk type basert pa forste element
    if isinstance(enheter[0], Underenhet):
        data = [underenhet_to_dict(e) for e in enheter]  # type: ignore
    else:
        data = [enhet_to_dict(e) for e in enheter]  # type: ignore

    df = pd.DataFrame(data)

    if columns:
        # Filtrer kun kolonner som finnes
        available_cols = [c for c in columns if c in df.columns]
        df = df[available_cols]

    return df


def to_excel(
    enheter: Sequence[Enhet | Underenhet],
    path: str | Path,
    columns: Optional[list[str]] = None,
    sheet_name: str = "Enheter",
) -> Path:
    """
    Eksporter enheter til Excel-fil.

    Args:
        enheter: Liste med Enhet-objekter
        path: Filsti for Excel-filen
        columns: Liste med kolonner som skal inkluderes (None = alle)
        sheet_name: Navn pa arket

    Returns:
        Path til opprettet fil
    """
    df = to_dataframe(enheter, columns)
    path = Path(path)

    # Juster kolonnebredder for bedre lesbarhet
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Auto-juster kolonnebredder
        worksheet = writer.sheets[sheet_name]
        from openpyxl.utils import get_column_letter
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).map(len).max(),
                len(col)
            )
            # Begrens maks bredde
            adjusted_width = min(max_length + 2, 50)
            col_letter = get_column_letter(idx + 1)
            worksheet.column_dimensions[col_letter].width = adjusted_width

    return path


def to_csv(
    enheter: Sequence[Enhet | Underenhet],
    path: str | Path,
    columns: Optional[list[str]] = None,
    encoding: str = "utf-8-sig",
    separator: str = ";",
) -> Path:
    """
    Eksporter enheter til CSV-fil.

    Args:
        enheter: Liste med Enhet-objekter
        path: Filsti for CSV-filen
        columns: Liste med kolonner som skal inkluderes (None = alle)
        encoding: Tegnkoding (utf-8-sig for Excel-kompatibilitet)
        separator: Feltseparator

    Returns:
        Path til opprettet fil
    """
    df = to_dataframe(enheter, columns)
    path = Path(path)

    df.to_csv(path, index=False, encoding=encoding, sep=separator)

    return path


def get_stats(enheter: Sequence[Enhet]) -> dict:
    """
    Beregn statistikk for en liste med enheter.

    Args:
        enheter: Liste med Enhet-objekter

    Returns:
        Dict med statistikk
    """
    total = len(enheter)
    if total == 0:
        return {
            "total": 0,
            "med_epost": 0,
            "med_telefon": 0,
            "med_hjemmeside": 0,
            "epost_dekning": 0.0,
            "telefon_dekning": 0.0,
            "per_orgform": {},
            "per_kommune": {},
        }

    med_epost = sum(1 for e in enheter if e.epostadresse)
    med_telefon = sum(1 for e in enheter if e.telefon or e.mobil)  # Inkluder mobil!
    med_hjemmeside = sum(1 for e in enheter if e.hjemmeside)

    per_orgform: dict[str, int] = {}
    per_kommune: dict[str, int] = {}

    for e in enheter:
        orgform = e.organisasjonsform.kode
        per_orgform[orgform] = per_orgform.get(orgform, 0) + 1

        kommune = e.kommune_navn() or "Ukjent"
        per_kommune[kommune] = per_kommune.get(kommune, 0) + 1

    return {
        "total": total,
        "med_epost": med_epost,
        "med_telefon": med_telefon,
        "med_hjemmeside": med_hjemmeside,
        "epost_dekning": round(med_epost / total * 100, 1),
        "telefon_dekning": round(med_telefon / total * 100, 1),
        "per_orgform": dict(sorted(per_orgform.items(), key=lambda x: -x[1])),
        "per_kommune": dict(sorted(per_kommune.items(), key=lambda x: -x[1])[:20]),
    }
