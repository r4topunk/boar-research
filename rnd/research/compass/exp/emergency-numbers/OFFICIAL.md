# Emergency numbers: official-source check (2026-10-03)

**TL;DR.** I checked all 9 regions against government pages: AR, CO, CL, PE, ES, MX, BR, PT and EU. Each page was fetched raw with curl, and every quote is an exact substring of its local text snapshot. There is no Wikipedia and no news source. Nothing is NOT FOUND. Mexico has one extra federal quote that only WebFetch could read, so it is marked † (check it by hand). The main fix to the content is Argentina: **107 is not national**. The Health Ministry's per-province list gives 911 for Provincia de Buenos Aires and 106 for Neuquén.

```fish
cd rnd/research/compass/exp/emergency-numbers
node check_official.mjs                            # quotes ⊂ snapshots, numbers ⊂ quotes, alias tests
python3 fetch_official.py <slug> <url>             # re-snapshot one page
```

Data: `official-2026-10-03.json` holds the quotes, URLs, proposed EN/PT/ES lines and alias regexes with test cases. The snapshots are in `snapshots-official/` as `*.raw.html` and `*.txt`.

| ISO | Numbers (official) | Status | Source org |
|---|---|---|---|
| AR | ambulance 107 (CABA + 21 provinces; **911** Prov. Buenos Aires; **106** Neuquén), police 911, fire 100 | VERIFIED | argentina.gob.ar (national portal) + Ministerio de Salud (DINESA) + GCBA |
| CO | 123 (single national line) | VERIFIED | Departamento Administrativo de la Función Pública |
| CL | SAMU 131, fire 132, Carabineros 133 | VERIFIED | Ministerio de Relaciones Exteriores (chile.gob.cl) |
| PE | SAMU 106, fire 116, police 105 | VERIFIED | MINSA (gob.pe) + PNP (gob.pe) |
| ES | 112 | VERIFIED | Punto de Acceso General, Gobierno de España |
| MX | 911 | VERIFIED (+ federal gob.mx quote †) | Gobierno de la Ciudad de México; gob.mx/911 † |
| BR | police 190, SAMU 192, fire 193 | VERIFIED | Ministério das Comunicações (gov.br, 11/09/2026) |
| PT | 112 | VERIFIED | gov.pt + European Commission (112 is PT's only national number) |
| EU | 112 | VERIFIED (was PARTIAL) | European Commission (digital-strategy) + Your Europe (europa.eu) |

## Proposed ES lines (EN/PT in JSON)

- `Argentina: ambulancia 107 (provincia de Buenos Aires: 911; Neuquén: 106), policía 911, bomberos 100.`
- `Colombia: 123 (todas las emergencias).`
- `Chile: ambulancia (SAMU) 131, bomberos 132, policía (Carabineros) 133.`
- `Perú: ambulancia (SAMU) 106, bomberos 116, policía 105.`
- `Unión Europea: 112 funciona en todos los países de la UE (policía, ambulancia, bomberos).`: put this row last.
- ES, MX, BR and PT: the current engine lines are correct and need no change.

## Not found / gaps (UNKNOWN)

- Nothing is NOT FOUND.
- †: the gob.mx/911 federal definition. gob.mx sends curl a JS challenge page, so only WebFetch could read it.
- AR: I found no official source on whether 911 is answered in every province, and the 101 police number is unverified. Two official pages conflict: the national portal lists 106 as "Emergencia náutica", while the Health Ministry page (undated) gives 106 as Neuquén's medical number.
- CO: the per-service numbers (ambulance, fire, police) are not verified, so only 123 is proposed.
- CL: minsal.cl returns 403 to curl, so there is no Health Ministry snapshot. The Foreign Ministry page is the only source.

## Alias notes (bugs in the current engine table)

- `\b` fails after a final accented letter. As a result, `Canadá` and the proposed `Bogotá` or `Perú` would not match. The proposed regexes use explicit lookarounds over the letter class `[A-Za-zÀ-ÖØ-öø-ÿ]` instead, with no `\p{L}`, so they also work on Hermes.
- The Spain row lacks `España`, so ES-language users asking about Spain get no answer. The proposed regex adds it.
- Food words collide with country names:
  - `turkey` (current table).
  - PT `peru` (turkey).
  - ES/EN `chile` (chili).
  - PT/ES `lima` (lime).
  - Because of this, the Peru and Chile aliases are case-sensitive (`Peru`/`Perú`, `Chile`) and exclude `Lima`.
  - Residual risk: a sentence that starts with the capitalised word still matches.
