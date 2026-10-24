# Storingen in je buurt — Home Assistant-integratie

Home Assistant-integratie die actuele storingen (stroom, gas, water, weg en meer) uit
jouw omgeving binnenhaalt via de open API van een **Storingen in je buurt**-hub.

Een dun schilletje: het leest alleen `GET /api/disruptions` van je hub en maakt daar
sensoren van. Geen scraping, geen externe Python-afhankelijkheden, geen account.

## Wat je nodig hebt

Een draaiende *Storingen in je buurt*-hub waarvan de open API bereikbaar is vanaf Home
Assistant (bijvoorbeeld `http://192.168.1.50:3032`). De hub bundelt openbare bronnen —
o.a. Liander (stroom/gas) en NDW (wegincidenten) — en biedt `/api/disruptions` en
`/api/health`.

## Installatie via HACS (aanbevolen)

1. HACS → ⋮ (rechtsboven) → **Custom repositories**.
2. Repository: `https://github.com/boonstraworks/ha-storingen-in-je-buurt`, type: **Integration**.
3. Installeer **Storingen in je buurt** en herstart Home Assistant.
4. **Instellingen → Apparaten & services → Integratie toevoegen** → "Storingen in je buurt".

## Handmatige installatie

Kopieer de map `custom_components/storingen_in_je_buurt` naar je `config/custom_components/`
en herstart Home Assistant.

## Configureren

- **Hub-URL** — het adres van je hub, bijvoorbeeld `http://192.168.1.50:3032`.
- **Postcode** (optioneel) — beperk tot een buurt (bijvoorbeeld `1791`). Leeg = heel Nederland.

Postcode en verversinterval pas je later aan via **Configureren** bij de integratie.

## Entiteiten

Onder één apparaat verschijnen:

- **Storing in de buurt** — binary sensor (device class *problem*), aan zodra er minstens
  één storing is. Attributen: totaal en aantal per categorie.
- **Totaal** — sensor met het totaal aantal storingen. Attributen: tijdstip van bijwerken,
  aantal per categorie, en een lijst met de storingen.
- Een teller per categorie: **Stroom, Gas, Water, Internet, Telefonie, Spoor, Weg, Weer,
  Overig** — met de storingen in die categorie als attribuut.

### Voorbeeld-automatisering

```yaml
automation:
  - alias: Melding bij stroomstoring in de buurt
    trigger:
      - platform: numeric_state
        entity_id: sensor.storingen_in_nederland_stroom
        above: 0
    action:
      - service: notify.mobile_app_telefoon
        data:
          message: "Er is een stroomstoring in de buurt gemeld."
```

> De exacte `entity_id` hangt af van de naam die je de integratie geeft; kijk in
> **Ontwikkelhulpmiddelen → Statussen**.

## Let op

Dit is een onafhankelijk project en **geen officiële overheids- of netbeheerderstoepassing**.
Aan de getoonde gegevens kunnen geen rechten worden ontleend; raadpleeg voor de officiële
status altijd je netbeheerder. Databronnen onder andere Liander en NDW; kaart en geocoding
via PDOK (Kadaster).

## Licentie

MIT — © BoonstraWorks
