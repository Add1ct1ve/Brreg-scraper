"""CLI for brreg-scraper."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, MofNCompleteColumn
from rich.table import Table

from brreg_scraper.client import BrregClient
from brreg_scraper.exporter import (
    to_excel,
    to_csv,
    get_stats,
    get_columns_for_preset,
    list_presets,
    COLUMN_PRESETS,
)
from brreg_scraper.regions import (
    list_regions,
    get_fylke_kode,
    get_kommunenummer_list,
)


app = typer.Typer(
    name="brreg",
    help="Scraper for Bronnøysundregistrene - hent data om norske organisasjoner.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def fetch(
    region: Annotated[
        Optional[list[str]],
        typer.Option("--region", "-r", help="Filtrer pa region/fylke (f.eks. oslo, akershus)")
    ] = None,
    org_type: Annotated[
        Optional[list[str]],
        typer.Option("--type", "-t", help="Filtrer pa organisasjonsform (f.eks. AS, ENK, NUF, BRL)")
    ] = None,
    navn: Annotated[
        Optional[str],
        typer.Option("--navn", "-n", help="Sok pa navn")
    ] = None,
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output-fil (.xlsx eller .csv)")
    ] = Path("brreg_data.xlsx"),
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", "-l", help="Maks antall enheter a hente")
    ] = None,
    columns: Annotated[
        Optional[str],
        typer.Option("--columns", "-c", help="Kolonne-preset: minimal, basic, contact, financial, full")
    ] = None,
):
    """Hent organisasjoner fra Bronnøysundregistrene og eksporter til fil."""
    # Valider kolonne-preset
    export_columns: list[str] | None = None
    if columns:
        try:
            export_columns = get_columns_for_preset(columns)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            console.print("Bruk 'brreg columns' for a se gyldige presets.")
            raise typer.Exit(1)

    # Valider regioner
    if region:
        invalid_regions = [r for r in region if get_fylke_kode(r) is None]
        if invalid_regions:
            console.print(f"[red]Ukjente regioner: {', '.join(invalid_regions)}[/red]")
            console.print("Bruk 'brreg regions' for a se gyldige regioner.")
            raise typer.Exit(1)

    # Normaliser organisasjonstyper
    if org_type:
        org_type = [t.upper() for t in org_type]

    # Vis hva vi skal hente
    filters = []
    if org_type:
        filters.append(f"type={','.join(org_type)}")
    if region:
        filters.append(f"region={','.join(region)}")
    if navn:
        filters.append(f"navn={navn}")

    filter_text = ", ".join(filters) if filters else "ingen filter (alle enheter)"
    console.print(f"\nSoker med: [bold]{filter_text}[/bold]")

    # Hent data med progress
    enheter = []
    with BrregClient() as client:
        # Finn kommunenummer for regionene
        kommunenummer: Optional[list[str]] = None
        if region:
            fylke_koder = [get_fylke_kode(r) for r in region if get_fylke_kode(r)]
            kommunenummer = get_kommunenummer_list(fylke_koder)

        # Tell forst for progress bar
        total = client.count(organisasjonsform=org_type, kommunenummer=kommunenummer)

        if limit:
            total = min(total, limit)

        console.print(f"Fant [bold]{total}[/bold] enheter.\n")

        if total == 0:
            console.print("[yellow]Ingen enheter funnet med disse filtrene.[/yellow]")
            raise typer.Exit(0)

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Henter data...", total=total)

            def update_progress(current: int, _total: int) -> None:
                progress.update(task, completed=current)

            for enhet in client.search(
                organisasjonsform=org_type,
                kommunenummer=kommunenummer,
                navn=navn,
                progress_callback=update_progress,
            ):
                enheter.append(enhet)
                if limit and len(enheter) >= limit:
                    break

    # Eksporter
    output_path = Path(output)
    if output_path.suffix.lower() == ".csv":
        to_csv(enheter, output_path, columns=export_columns)
    else:
        to_excel(enheter, output_path, columns=export_columns)

    col_info = f" (preset: {columns})" if columns else ""
    console.print(f"\n[green]Eksportert {len(enheter)} enheter til {output_path}{col_info}[/green]")

    # Vis statistikk
    stats = get_stats(enheter)
    console.print(f"\n[bold]Statistikk:[/bold]")
    console.print(f"  E-post-dekning: {stats['epost_dekning']}%")
    console.print(f"  Telefon-dekning: {stats['telefon_dekning']}%")
    if stats['per_orgform']:
        console.print(f"  Organisasjonsformer: {stats['per_orgform']}")


@app.command()
def count(
    region: Annotated[
        Optional[list[str]],
        typer.Option("--region", "-r", help="Filtrer pa region/fylke")
    ] = None,
    org_type: Annotated[
        Optional[list[str]],
        typer.Option("--type", "-t", help="Filtrer pa organisasjonsform")
    ] = None,
):
    """Tell antall organisasjoner som matcher kriteriene."""
    if org_type:
        org_type = [t.upper() for t in org_type]

    with BrregClient() as client:
        kommunenummer: Optional[list[str]] = None
        if region:
            fylke_koder = [get_fylke_kode(r) for r in region if get_fylke_kode(r)]
            kommunenummer = get_kommunenummer_list(fylke_koder)

        total = client.count(organisasjonsform=org_type, kommunenummer=kommunenummer)

        filters = []
        if org_type:
            filters.append(f"type={','.join(org_type)}")
        if region:
            filters.append(f"region={','.join(region)}")

        filter_text = ", ".join(filters) if filters else "alle"
        console.print(f"Antall enheter ({filter_text}): [bold]{total}[/bold]")


@app.command()
def regions():
    """List tilgjengelige regioner/fylker."""
    table = Table(title="Tilgjengelige regioner")
    table.add_column("Alias", style="cyan")
    table.add_column("Fylkeskode")
    table.add_column("Navn")
    table.add_column("Kommuner", justify="right")

    for kode, navn, antall_kommuner in list_regions():
        from brreg_scraper.regions import REGION_ALIASES
        alias = next((a for a, k in REGION_ALIASES.items() if k == kode), kode)
        table.add_row(alias, kode, navn, str(antall_kommuner))

    console.print(table)


@app.command()
def lookup(
    orgnr: Annotated[str, typer.Argument(help="Organisasjonsnummer")],
    underenhet: Annotated[
        bool,
        typer.Option("--underenhet", "-u", help="Sla opp som underenhet/bedrift")
    ] = False,
):
    """Sla opp en enkelt organisasjon pa organisasjonsnummer."""
    with BrregClient() as client:
        if underenhet:
            enhet = client.get_underenhet(orgnr)
        else:
            enhet = client.get(orgnr)

        if not enhet:
            enhet_type = "underenhet" if underenhet else "enhet"
            console.print(f"[red]Fant ingen {enhet_type} med orgnr {orgnr}[/red]")
            raise typer.Exit(1)

        table = Table(title=f"{'Underenhet' if underenhet else 'Enhet'}: {enhet.navn}")
        table.add_column("Felt", style="cyan")
        table.add_column("Verdi")

        table.add_row("Organisasjonsnummer", enhet.organisasjonsnummer)
        table.add_row("Navn", enhet.navn)
        table.add_row("Type", f"{enhet.organisasjonsform.kode} - {enhet.organisasjonsform.beskrivelse or ''}")

        if underenhet and hasattr(enhet, 'overordnetEnhet'):
            table.add_row("Overordnet enhet", enhet.overordnetEnhet)

        table.add_row("E-post", enhet.epostadresse or "-")
        table.add_row("Telefon", enhet.telefon or "-")
        table.add_row("Hjemmeside", enhet.hjemmeside or "-")

        if not underenhet and enhet.forretningsadresse:
            addr = enhet.forretningsadresse
            adresse_str = addr.formatted()
            table.add_row("Adresse", adresse_str)
            table.add_row("Kommune", f"{addr.kommune} ({addr.kommunenummer})" if addr.kommune else "-")
        elif underenhet and hasattr(enhet, 'beliggenhetsadresse') and enhet.beliggenhetsadresse:
            addr = enhet.beliggenhetsadresse
            adresse_str = addr.formatted()
            table.add_row("Beliggenhetsadresse", adresse_str)
            table.add_row("Kommune", f"{addr.kommune} ({addr.kommunenummer})" if addr.kommune else "-")

        if not underenhet:
            table.add_row("Stiftelsesdato", str(enhet.stiftelsesdato) if enhet.stiftelsesdato else "-")
        else:
            table.add_row("Oppstartsdato", str(enhet.oppstartsdato) if hasattr(enhet, 'oppstartsdato') and enhet.oppstartsdato else "-")

        table.add_row("Antall ansatte", str(enhet.antallAnsatte) if enhet.antallAnsatte else "-")

        console.print(table)


@app.command()
def underenheter(
    overordnet: Annotated[
        Optional[str],
        typer.Option("--overordnet", "-p", help="Organisasjonsnummer til hovedenheten")
    ] = None,
    region: Annotated[
        Optional[list[str]],
        typer.Option("--region", "-r", help="Filtrer pa region/fylke")
    ] = None,
    naeringskode: Annotated[
        Optional[str],
        typer.Option("--naeringskode", "-k", help="Filtrer pa naeringskode (f.eks. 68.201)")
    ] = None,
    navn: Annotated[
        Optional[str],
        typer.Option("--navn", "-n", help="Sok pa navn")
    ] = None,
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output-fil (.xlsx eller .csv)")
    ] = Path("underenheter.xlsx"),
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", "-l", help="Maks antall underenheter a hente")
    ] = None,
    columns: Annotated[
        Optional[str],
        typer.Option("--columns", "-c", help="Kolonne-preset: minimal, basic, contact, financial, full")
    ] = None,
):
    """Hent underenheter/bedrifter fra Bronnøysundregistrene."""
    # Valider kolonne-preset
    export_columns: list[str] | None = None
    if columns:
        try:
            export_columns = get_columns_for_preset(columns)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            console.print("Bruk 'brreg columns' for a se gyldige presets.")
            raise typer.Exit(1)

    # Valider regioner
    if region:
        invalid_regions = [r for r in region if get_fylke_kode(r) is None]
        if invalid_regions:
            console.print(f"[red]Ukjente regioner: {', '.join(invalid_regions)}[/red]")
            raise typer.Exit(1)

    # Vis hva vi skal hente
    filters = []
    if overordnet:
        filters.append(f"overordnet={overordnet}")
    if region:
        filters.append(f"region={','.join(region)}")
    if naeringskode:
        filters.append(f"naeringskode={naeringskode}")
    if navn:
        filters.append(f"navn={navn}")

    filter_text = ", ".join(filters) if filters else "ingen filter"
    console.print(f"\nSoker underenheter med: [bold]{filter_text}[/bold]")

    # Hent data
    results = []
    with BrregClient() as client:
        kommunenummer: Optional[list[str]] = None
        if region:
            fylke_koder = [get_fylke_kode(r) for r in region if get_fylke_kode(r)]
            kommunenummer = get_kommunenummer_list(fylke_koder)

        total = client.count_underenheter(
            overordnetEnhet=overordnet,
            kommunenummer=kommunenummer
        )

        if limit:
            total = min(total, limit)

        console.print(f"Fant [bold]{total}[/bold] underenheter.\n")

        if total == 0:
            console.print("[yellow]Ingen underenheter funnet.[/yellow]")
            raise typer.Exit(0)

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Henter underenheter...", total=total)

            def update_progress(current: int, _total: int) -> None:
                progress.update(task, completed=current)

            for u in client.search_underenheter(
                overordnetEnhet=overordnet,
                kommunenummer=kommunenummer,
                naeringskode=naeringskode,
                navn=navn,
                progress_callback=update_progress,
            ):
                results.append(u)
                if limit and len(results) >= limit:
                    break

    # Eksporter
    output_path = Path(output)
    if output_path.suffix.lower() == ".csv":
        to_csv(results, output_path, columns=export_columns)
    else:
        to_excel(results, output_path, columns=export_columns, sheet_name="Underenheter")

    col_info = f" (preset: {columns})" if columns else ""
    console.print(f"\n[green]Eksportert {len(results)} underenheter til {output_path}{col_info}[/green]")


@app.command()
def columns():
    """Vis tilgjengelige kolonne-presets for eksport."""
    console.print("\n[bold]Tilgjengelige kolonne-presets:[/bold]\n")

    for preset_name, preset_columns in COLUMN_PRESETS.items():
        if preset_columns is None:
            col_count = "alle"
            col_list = "(eksporterer alle tilgjengelige kolonner)"
        else:
            col_count = str(len(preset_columns))
            col_list = ", ".join(preset_columns)

        table = Table(title=f"{preset_name} ({col_count} kolonner)", show_header=False, box=None)
        table.add_column("Kolonner", style="dim")
        table.add_row(col_list)
        console.print(table)
        console.print()

    console.print("[bold]Bruk:[/bold]")
    console.print("  brreg fetch --type AS --columns minimal -o as.xlsx")
    console.print("  brreg fetch --type BRL --columns contact -o brl.xlsx")
    console.print("  brreg underenheter --columns basic -o underenheter.xlsx\n")


def main():
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
