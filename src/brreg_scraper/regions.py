"""Kommune- og fylkeskoder for Norge (oppdatert 2024)."""

from typing import Optional

FYLKER = {
    "03": "Oslo",
    "11": "Rogaland",
    "15": "More og Romsdal",
    "18": "Nordland",
    "31": "Ostfold",
    "32": "Akershus",
    "33": "Buskerud",
    "34": "Innlandet",
    "39": "Vestfold",
    "40": "Telemark",
    "42": "Agder",
    "46": "Vestland",
    "50": "Trondelag",
    "55": "Troms",
    "56": "Finnmark",
}

KOMMUNER = {
    "03": {"0301": "Oslo"},
    "32": {
        "3201": "Baerum", "3203": "Asker", "3205": "Lillestrom",
        "3207": "Nordre Follo", "3209": "Ullensaker", "3212": "Nesodden",
        "3214": "Frogn", "3216": "Vestby", "3218": "As",
        "3220": "Enebakk", "3222": "Lorenskog", "3224": "Raelingen",
        "3226": "Aurskog-Holand", "3228": "Nes", "3230": "Gjerdrum",
        "3232": "Nittedal", "3234": "Lunner", "3236": "Jevnaker",
        "3238": "Nannestad", "3240": "Eidsvoll", "3242": "Hurdal",
    },
    "33": {
        "3301": "Drammen", "3303": "Kongsberg", "3305": "Ringerike",
        "3310": "Hole", "3312": "Lier", "3314": "Ovre Eiker",
        "3316": "Modum", "3318": "Krodsherad", "3320": "Fla",
        "3322": "Nesbyen", "3324": "Gol", "3326": "Hemsedal",
        "3328": "Al", "3330": "Hol", "3332": "Sigdal",
        "3334": "Flesberg", "3336": "Rollag", "3338": "Nore og Uvdal",
    },
    "11": {
        "1101": "Eigersund", "1103": "Stavanger", "1106": "Haugesund",
        "1108": "Sandnes", "1111": "Sokndal", "1112": "Lund",
        "1114": "Bjerkreim", "1119": "Ha", "1120": "Klepp",
        "1121": "Time", "1122": "Gjesdal", "1124": "Sola",
        "1127": "Randaberg", "1130": "Strand", "1133": "Hjelmeland",
        "1134": "Suldal", "1135": "Sauda", "1144": "Kvitsoy",
        "1145": "Bokn", "1146": "Tysvaer", "1149": "Karmoy",
        "1151": "Utsira", "1160": "Vindafjord",
    },
    "15": {
        "1505": "Kristiansund", "1506": "Molde", "1508": "Alesund",
        "1511": "Vanylven", "1514": "Sande", "1515": "Heroy",
        "1516": "Ulstein", "1517": "Hareid", "1520": "Orsta",
        "1525": "Stranda", "1528": "Sykkylven", "1531": "Sula",
        "1532": "Giske", "1535": "Vestnes", "1539": "Rauma",
        "1547": "Aukra", "1554": "Averoy", "1557": "Gjemnes",
        "1560": "Tingvoll", "1563": "Sunndal", "1566": "Surnadal",
        "1573": "Smola", "1576": "Aure", "1577": "Volda",
        "1578": "Fjord", "1579": "Hustadvika",
    },
    "18": {
        "1804": "Bodo", "1806": "Narvik", "1811": "Bindal",
        "1812": "Somna", "1813": "Bronnoy", "1815": "Vega",
        "1816": "Vevelstad", "1818": "Heroy", "1820": "Alstahaug",
        "1822": "Leirfjord", "1824": "Vefsn", "1825": "Grane",
        "1826": "Hattfjelldal", "1827": "Donna", "1828": "Nesna",
        "1832": "Hemnes", "1833": "Rana", "1834": "Luroy",
        "1835": "Traena", "1836": "Rodoy", "1837": "Meloy",
        "1838": "Gildeskal", "1839": "Beiarn", "1840": "Saltdal",
        "1841": "Fauske", "1845": "Sorfold", "1848": "Steigen",
        "1851": "Lodingen", "1853": "Evenes", "1856": "Rost",
        "1857": "Vaeroy", "1859": "Flakstad", "1860": "Vestvagoy",
        "1865": "Vagan", "1866": "Hadsel", "1867": "Bo",
        "1868": "Oksnes", "1870": "Sortland", "1871": "Andoy",
        "1874": "Moskenes", "1875": "Hamaroy",
    },
    "31": {
        "3101": "Halden", "3103": "Moss", "3105": "Sarpsborg",
        "3107": "Fredrikstad", "3110": "Hvaler", "3112": "Rade",
        "3114": "Valer", "3116": "Skiptvet", "3118": "Indre Ostfold",
        "3120": "Rakkestad", "3122": "Marker", "3124": "Aremark",
    },
    "34": {
        "3401": "Kongsvinger", "3403": "Hamar", "3405": "Lillehammer",
        "3407": "Gjovik", "3411": "Ringsaker", "3412": "Loten",
        "3413": "Stange", "3414": "Nord-Odal", "3415": "Sor-Odal",
        "3416": "Eidskog", "3417": "Grue", "3418": "Asnes",
        "3419": "Valer", "3420": "Elverum", "3421": "Trysil",
        "3422": "Amot", "3423": "Stor-Elvdal", "3424": "Rendalen",
        "3425": "Engerdal", "3426": "Tolga", "3427": "Tynset",
        "3428": "Alvdal", "3429": "Folldal", "3430": "Os",
        "3431": "Dovre", "3432": "Lesja", "3433": "Skjak",
        "3434": "Lom", "3435": "Vaga", "3436": "Nord-Fron",
        "3437": "Sel", "3438": "Sor-Fron", "3439": "Ringebu",
        "3440": "Oyer", "3441": "Gausdal", "3442": "Ostre Toten",
        "3443": "Vestre Toten", "3446": "Gran", "3447": "Sondre Land",
        "3448": "Nordre Land", "3449": "Sor-Aurdal", "3450": "Etnedal",
        "3451": "Nord-Aurdal", "3452": "Vestre Slidre", "3453": "Oystre Slidre",
        "3454": "Vang",
    },
    "39": {
        "3901": "Horten", "3903": "Holmestrand", "3905": "Tonsberg",
        "3907": "Sandefjord", "3909": "Larvik", "3911": "Faerder",
    },
    "40": {
        "4001": "Porsgrunn", "4003": "Skien", "4005": "Notodden",
        "4010": "Siljan", "4012": "Bamble", "4014": "Kragero",
        "4016": "Drangedal", "4018": "Nome", "4020": "Midt-Telemark",
        "4022": "Seljord", "4024": "Hjartdal", "4026": "Tinn",
        "4028": "Kviteseid", "4030": "Nissedal", "4032": "Fyresdal",
        "4034": "Tokke", "4036": "Vinje",
    },
    "42": {
        "4201": "Risor", "4203": "Arendal", "4204": "Grimstad",
        "4205": "Kristiansand", "4206": "Farsund", "4207": "Flekkefjord",
        "4211": "Gjerstad", "4212": "Vegarshei", "4213": "Tvedestrand",
        "4214": "Froland", "4215": "Lillesand", "4216": "Birkenes",
        "4217": "Amli", "4218": "Iveland", "4219": "Evje og Hornnes",
        "4220": "Bygland", "4221": "Valle", "4222": "Bykle",
        "4223": "Vennesla", "4224": "Aseral", "4225": "Lyngdal",
        "4226": "Haegebostad", "4227": "Kvinesdal", "4228": "Sirdal",
        "4229": "Lindesnes",
    },
    "46": {
        "4601": "Bergen", "4602": "Kinn", "4611": "Etne",
        "4612": "Sveio", "4613": "Bomlo", "4614": "Stord",
        "4615": "Fitjar", "4616": "Tysnes", "4617": "Kvinnherad",
        "4618": "Ullensvang", "4619": "Eidfjord", "4620": "Ulvik",
        "4621": "Voss", "4622": "Kvam", "4623": "Samnanger",
        "4624": "Bjornafjorden", "4625": "Austevoll", "4626": "Oygarden",
        "4627": "Askoy", "4628": "Vaksdal", "4629": "Modalen",
        "4630": "Osteroy", "4631": "Alver", "4632": "Austrheim",
        "4633": "Fedje", "4634": "Masfjorden", "4635": "Gulen",
        "4636": "Solund", "4637": "Hyllestad", "4638": "Hoyanger",
        "4639": "Vik", "4640": "Sogndal", "4641": "Aurland",
        "4642": "Laerdal", "4643": "Ardal", "4644": "Luster",
        "4645": "Askvoll", "4646": "Fjaler", "4647": "Sunnfjord",
        "4648": "Bremanger", "4649": "Stad", "4650": "Gloppen",
        "4651": "Stryn",
    },
    "50": {
        "5001": "Trondheim", "5006": "Steinkjer", "5007": "Namsos",
        "5014": "Froya", "5020": "Osen", "5021": "Oppdal",
        "5022": "Rennebu", "5025": "Roros", "5026": "Holtalen",
        "5027": "Midtre Gauldal", "5028": "Melhus", "5029": "Skaun",
        "5031": "Malvik", "5032": "Selbu", "5033": "Tydal",
        "5034": "Meraker", "5035": "Stjordal", "5036": "Frosta",
        "5037": "Levanger", "5038": "Verdal", "5041": "Snasa",
        "5042": "Lierne", "5043": "Royrvik", "5044": "Namsskogan",
        "5045": "Grong", "5046": "Hoylandet", "5047": "Overhalla",
        "5049": "Flatanger", "5052": "Leka", "5053": "Inderoy",
        "5054": "Indre Fosen", "5055": "Heim", "5056": "Hitra",
        "5057": "Orland", "5058": "Afjord", "5059": "Orkland",
        "5060": "Naeroysund", "5061": "Rindal",
    },
    "55": {
        "5501": "Tromso", "5503": "Harstad", "5510": "Kvaefjord",
        "5512": "Tjeldsund", "5514": "Ibestad", "5516": "Gratangen",
        "5518": "Lavangen", "5520": "Bardu", "5522": "Salangen",
        "5524": "Malselv", "5526": "Sorreisa", "5528": "Dyroy",
        "5530": "Senja", "5532": "Balsfjord", "5534": "Karlsoy",
        "5536": "Lyngen", "5538": "Storfjord", "5540": "Kafjord",
        "5542": "Skjervoy", "5544": "Nordreisa", "5546": "Kvaenangen",
    },
    "56": {
        "5601": "Alta", "5603": "Hammerfest", "5605": "Sor-Varanger",
        "5607": "Vadso", "5610": "Karasjok", "5612": "Kautokeino",
        "5614": "Loppa", "5616": "Hasvik", "5618": "Masoy",
        "5620": "Nordkapp", "5622": "Porsanger", "5624": "Lebesby",
        "5626": "Gamvik", "5628": "Tana", "5630": "Berlevag",
        "5632": "Batsfjord", "5634": "Vardo", "5636": "Nesseby",
    },
}

REGION_ALIASES = {
    "oslo": "03",
    "rogaland": "11",
    "more_og_romsdal": "15",
    "nordland": "18",
    "ostfold": "31",
    "akershus": "32",
    "buskerud": "33",
    "innlandet": "34",
    "vestfold": "39",
    "telemark": "40",
    "agder": "42",
    "vestland": "46",
    "trondelag": "50",
    "troms": "55",
    "finnmark": "56",
}


def get_fylke_kode(navn_eller_kode: str) -> Optional[str]:
    """Hent fylkeskode fra navn eller alias."""
    navn_lower = navn_eller_kode.lower().replace(" ", "_")
    if navn_lower in REGION_ALIASES:
        return REGION_ALIASES[navn_lower]
    if navn_eller_kode in FYLKER:
        return navn_eller_kode
    return None


def get_kommuner_for_fylke(fylke_kode: str) -> dict[str, str]:
    """Hent alle kommuner i et fylke."""
    return KOMMUNER.get(fylke_kode, {})


def get_kommunenummer_list(fylke_koder: list[str]) -> list[str]:
    """Hent liste av kommunenummer for gitte fylker."""
    result = []
    for fylke in fylke_koder:
        kommuner = KOMMUNER.get(fylke, {})
        result.extend(kommuner.keys())
    return result


def list_regions() -> list[tuple[str, str, int]]:
    """List alle regioner med kode, navn og antall kommuner."""
    return [
        (kode, navn, len(KOMMUNER.get(kode, {})))
        for kode, navn in sorted(FYLKER.items())
    ]


# Bakoverkompatibilitet
def get_kommune_codes(regions: list[str] | None = None) -> list[str]:
    """Hent kommunekoder for gitte regioner (bakoverkompatibel)."""
    if regions is None:
        return get_kommunenummer_list(list(FYLKER.keys()))

    fylke_koder = []
    for region in regions:
        kode = get_fylke_kode(region)
        if kode:
            fylke_koder.append(kode)
    return get_kommunenummer_list(fylke_koder)


def get_fylke_codes(regions: list[str] | None = None) -> list[str]:
    """Hent fylkeskoder for gitte regioner (bakoverkompatibel)."""
    if regions is None:
        return list(FYLKER.keys())

    codes = []
    for region in regions:
        kode = get_fylke_kode(region)
        if kode:
            codes.append(kode)
    return codes
