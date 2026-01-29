# brreg-scraper

Kraftig scraper for Bronnøysundregistrene. Hent data om alle norske organisasjoner med epost, telefon, adresse og mer.

## Features

- Hent alle typer organisasjoner (AS, ENK, NUF, BRL, osv.)
- Filtrer pa region/fylke og organisasjonsform
- Sok pa navn
- Eksporter til Excel eller CSV
- Inkluderer kontaktinfo (e-post, telefon, hjemmeside)
- Robust retry-logikk og progress bar
- Paginering handteres automatisk

## Installasjon

```bash
cd brreg-scraper
pip install -e .
```

## CLI-bruk

### Hent data

```bash
# Hent alle aksjeselskaper i Oslo
brreg fetch --region oslo --type AS -o oslo_as.xlsx

# Hent enkeltpersonforetak i flere regioner
brreg fetch --region oslo --region akershus --type ENK -o enk.xlsx

# Hent borettslag i Oslo
brreg fetch --region oslo --type BRL -o borettslag.xlsx

# Hent med begrensning
brreg fetch --type AS --limit 1000 -o sample.xlsx

# Sok pa navn
brreg fetch --navn "Equinor" -o equinor.xlsx

# Eksporter til CSV
brreg fetch --region oslo --type AS -o data.csv
```

### Tell organisasjoner

```bash
# Tell aksjeselskaper i Oslo
brreg count --region oslo --type AS

# Tell alle enheter i Norge
brreg count
```

### List regioner

```bash
brreg regions
```

### Sla opp organisasjon

```bash
brreg lookup 923609016
```

## Python API

```python
from brreg_scraper import BrregClient, to_excel, to_csv

with BrregClient() as client:
    # Hent enkelt organisasjon
    enhet = client.get("923609016")
    print(enhet.navn, enhet.epostadresse)

    # Sok etter aksjeselskaper i Oslo
    enheter = list(client.search(
        organisasjonsform=["AS"],
        kommunenummer=["0301"],
    ))

    # Hent alle med en type i en region
    enheter = client.fetch_all(
        organisasjonsform=["ENK"],
        regions=["oslo", "akershus"]
    )

# Eksporter
to_excel(enheter, "data.xlsx")
to_csv(enheter, "data.csv")
```

### Avansert bruk

```python
from brreg_scraper import BrregClient
from brreg_scraper.regions import get_kommunenummer_list

with BrregClient(timeout=60.0, max_retries=5) as client:
    # Tell enheter
    count = client.count(organisasjonsform=["AS"])
    print(f"Totalt {count} aksjeselskaper")

    # Iterator med progress callback
    def on_progress(current, total):
        print(f"{current}/{total}")

    for enhet in client.search(
        organisasjonsform=["AS", "ASA"],
        progress_callback=on_progress
    ):
        print(enhet.organisasjonsnummer, enhet.navn)
```

## Vanlige organisasjonsformer

| Kode | Beskrivelse |
|------|-------------|
| AS | Aksjeselskap |
| ASA | Allmennaksjeselskap |
| ENK | Enkeltpersonforetak |
| NUF | Norskregistrert utenlandsk foretak |
| ANS | Ansvarlig selskap |
| DA | Selskap med delt ansvar |
| BA | Selskap med begrenset ansvar |
| STI | Stiftelse |
| FLI | Forening/lag/innretning |
| BRL | Borettslag |
| ESEK | Eierseksjonssameie |
| KF | Kommunalt foretak |

Se komplett liste: https://www.brreg.no/om-oss/registrene-vare/om-enhetsregisteret/organisasjonsformer/

## Tilgjengelige regioner

| Alias | Fylke |
|-------|-------|
| oslo | Oslo |
| akershus | Akershus |
| buskerud | Buskerud |
| ostfold | Ostfold |
| vestfold | Vestfold |
| telemark | Telemark |
| innlandet | Innlandet |
| agder | Agder |
| rogaland | Rogaland |
| vestland | Vestland |
| trondelag | Trondelag |
| more_og_romsdal | More og Romsdal |
| nordland | Nordland |
| troms | Troms |
| finnmark | Finnmark |

## API-respons felter

Hver enhet inneholder:
- `organisasjonsnummer` - 9-sifret orgnr
- `navn` - Organisasjonens navn
- `organisasjonsform` - Kode og beskrivelse
- `epostadresse` - E-post (hvis registrert)
- `telefon` - Telefonnummer (hvis registrert)
- `hjemmeside` - Nettside (hvis registrert)
- `forretningsadresse` - Gate, postnr, poststed, kommune
- `postadresse` - Postadresse
- `stiftelsesdato` - Dato organisasjonen ble stiftet
- `antallAnsatte` - Antall ansatte
- `konkurs` - Om organisasjonen er under konkurs
- `underAvvikling` - Om organisasjonen er under avvikling

## Lisens

MIT
