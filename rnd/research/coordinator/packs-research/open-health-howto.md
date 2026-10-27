# Open health / first-aid / how-to / facts corpora for BOAR Knowledge Packs

Status: research note, as of 2026-10-12. Read-only web research (no downloads). Items marked **UNVERIFIED** were not confirmed on a primary page. "Fetched" = primary page read; "search" = only search snippets.

## TL;DR (5 best candidates: value x licence clarity x size)

1. **MedlinePlus Health Topic XML** (US federal summaries = public domain). Topic XML ~29.4 MB, zip ~4.7 MB. Filter out A.D.A.M.-licensed text before shipping. Licence on the XML page is not stated. [medlineplus.gov/xml.html](https://medlineplus.gov/xml.html) (fetched)
2. **US Army FM 4-25.11 First Aid** (federal work, public release, superseded 2016 by TC 4-02.1). Small PDF, clear provenance. [irp.fas.org/doddir/milmed/first.pdf](https://irp.fas.org/doddir/milmed/first.pdf) (search)
3. **USDA FoodData Central** (CC0 1.0). Full CSV ~458 MB zipped / 3.1 GB unzipped; subsets possible. [fdc.nal.usda.gov/download-datasets](https://fdc.nal.usda.gov/download-datasets) (search)
4. **WikiMed / MDWiki (Kiwix ZIM)** (medical Wikipedia subset, text CC BY-SA). ~1.2-1.7 GB EN, exact current size UNVERIFIED. Share-alike applies. [library.kiwix.org](https://library.kiwix.org), [meta.wikimedia.org/wiki/Wiki_Project_Med/App](https://meta.wikimedia.org/wiki/Wiki_Project_Med/App) (search)
5. **Simple English Wikipedia dump** (CC BY-SA + GFDL). Multistream bz2 = 387.9 MB (listing 2026-10-01). General knowledge, not health-specific. [dumps.wikimedia.org/simplewiki/latest/](https://dumps.wikimedia.org/simplewiki/latest/) (fetched)

Headline risk: the **CIA World Factbook was discontinued 2026-02-04**; the live site is gone. Only archives and third-party copies remain (section 3).

## 1. Health and first aid

| Source | Licence | Attribution | Bulk URL / format | Size | Last update | Notes |
|---|---|---|---|---|---|---|
| MedlinePlus Health Topic XML | Federal summaries PD; A.D.A.M. encyclopedia, ASHP drug monographs and most images are licensed to NLM, not PD. XML page states no licence. Data.gov lists ODbL, ODI cert lists CC0 (conflict). [copyright](https://medlineplus.gov/copyright.html) (fetched), [data.gov](https://catalog.data.gov/dataset/medlineplus) (search) | "Courtesy of MedlinePlus from the National Library of Medicine" or "Source: MedlinePlus, National Library of Medicine" [copyright](https://medlineplus.gov/copyright.html) | XML (topic, zip, group, definitions, schema) at [medlineplus.gov/xml.html](https://medlineplus.gov/xml.html) | Topic XML ~29.4 MB; zip ~4.7 MB; group 11 KB | Daily Tue-Sat; page showed Oct 3-10 2026 files | Contains EN + ES topics in one file (no Spanish-only download). Does not say whether A.D.A.M. text is in the XML: **UNVERIFIED, must check before shipping**. |
| MedlinePlus Web service (API) | Free, no registration; credit required [web services](https://www.nlm.nih.gov/medlineplus/webservices.html) (search) | Credit MedlinePlus; no logo/endorsement | REST search, Spanish queries via db=healthTopicsSpanish | n/a | live | Query-based, not bulk. Good for live links only. |
| MedlinePlus Connect | Explicitly prohibits ingesting/branding copyrighted drug and A.D.A.M. content in EHR/health IT [copyright](https://medlineplus.gov/copyright.html) (fetched) | n/a | n/a | n/a | n/a | Not a path for BOAR unless licensed from vendor. |
| MedlinePlus Encyclopedia (A.D.A.M.) | Copyrighted, Ebix; personal non-commercial viewing only; no scraping or derivatives [medlineplus.gov/copyright.html](https://medlineplus.gov/copyright.html) (fetched, search snippet on the A.D.A.M. notice) | - | none | - | - | **Do not ship.** Written consent from Ebix needed. |
| MedlinePlus Spanish | Same XML as above; no separate bulk | As above | in topic XML | in topic XML | as above | - |
| NHS (UK) nhs.uk content | Copyright and database rights released under OGL v3, except third-party material, logos, images (stock-licensed), trademarks [nhs.uk terms](https://www.nhs.uk/our-policies/terms-and-conditions/) (search), [content not licensed](https://www.nhs.uk/our-policies/terms-and-conditions/content-not-licensed-for-re-use/) (search) | "Information from the NHS website" + "as at DDMMYY" if not refreshed; separate from own content | Web pages only in this search. API/widgets: separate syndication licence agreement (free, but binding) (search) | UNVERIFIED | UNVERIFIED | API terms NOT retrieved. Check syndication terms before any NHS pull. Scraping pages for a pack is a licence question, not just a copyright one. |
| WHO publications | CC BY-NC-SA 3.0 IGO; commercial use needs written permission; adaptations must carry same/similar licence; WHO logo barred [WHO copyright](https://www.who.int/about/policies/publishing/copyright) (fetched) | Citation: title, place, "World Health Organization; [year]", "Licence: CC BY-NC-SA 3.0 IGO" | PDF per publication, no bulk found | UNVERIFIED | - | **NC = unusable** for a sold or bounty-prize app without a WHO permission. |
| CDC content | Most CDC/ATSDR web content PD; exceptions: contractor/grantee, third-party and stock images; CDC logo not PD (trademark) [use of agency materials](https://cdc.gov/other/agencymaterials.html) (search) | Attribute to CDC/ATSDR/HHS; add "no endorsement" disclaimer | No bulk web-page dump found. Datasets (NCHS, cancer statistics) carry their own use limits, e.g. statistical use only | - | - | Use CDC web text by hand-picked pages with attribution. Check each image. |
| FEMA / ready.gov | Publications free to reproduce unaltered, no endorsement implied; photos per item [ready.gov publications](https://www.ready.gov/ar/node/213) (search, archived 2022) | Credit; no alteration | Downloadable PDFs per publication, no bulk | - | - | Terms are from a search snippet, not fetched. EMI course materials have a stricter policy. |
| US Army FM 4-25.11 First Aid (2002, joint FM 21-11 / NTRP 4-02.1 / AFMAN 44-163(I)) | Federal work (17 USC 105; general knowledge); "approved for public release; distribution unlimited" [FAS PDF](https://irp.fas.org/doddir/milmed/first.pdf) (search) | Not required, but credit good practice | PDF | UNVERIFIED (roughly a few MB) | Dec 2002; superseded by TC 4-02.1 (Jan 2016) (search, [ciehub](https://ciehub.info/ref/FM/4-25x11.html)) | Copies sold by publishers are typeset, may carry copyright: use the government PDF. |
| US Army FM 21-76 Survival (1957) | Scan on archive.org carries a copyright notice; PD not guaranteed for every page [archive.org](https://archive.org/download/FM21-76Survival1957/FM21-76Survival1957.pdf) (search) | - | PDF | UNVERIFIED | 1957 text; current doctrine is FM 3-05.70 (search) | Old text. Re-check the notice. Avoid aggregator "free download" sites. |
| WikiMed / MDWiki (Kiwix) | Text CC BY-SA; media terms vary; app GPL [Kiwix archive](https://kiwix.lema.org/mdwiki_en_all_2024-03) (search) | Wikipedia-style attribution + share-alike | ZIM via [library.kiwix.org](https://library.kiwix.org) | ~1.2 GB EN (2015-era Meta figure); MS Store lists 1.4-1.7 GB. Current: UNVERIFIED | Kiwix release tag 2024-03 seen; newer UNVERIFIED | 55k-67k articles (counts disagree). Best medical-only text corpus with clear licence. |
| Wikibooks First Aid | Mixed: GFDL 1.2+ and CC BY-SA on the PoD PDF [Commons](https://download.osmand.net/wiki/File:First_Aid.pdf) (search); Canadian derivative CC BY-SA 4.0 [Ontario repo](https://openlibrary-repo.ecampusontario.ca/xmlui/handle/123456789/433?show=full) (search) | Share-alike (SA) | Wikibooks dumps via dumps.wikimedia.org | UNVERIFIED | - | Check each book page licence. No NC. |
| Wikipedia medical subsets via dump filtering | CC BY-SA 4.0 + GFDL 1.3 for text; images per-file [dumps legal](https://dumps.wikimedia.org/legal.html) (fetched) | Credit, link, same licence, mark changes | dumps.wikimedia.org (monthly) | enwiki 42 GB with images / 12 GB no images (2014, old) | monthly | Filter by WikiProject Medicine categories ourselves. |

## 2. Open how-to and general reference

| Source | Licence | Attribution | Bulk URL / format | Size | Last update | Notes |
|---|---|---|---|---|---|---|
| Simple English Wikipedia | CC BY-SA 4.0 + GFDL [dumps legal](https://dumps.wikimedia.org/legal.html) (fetched) | Wikipedia-style | [simplewiki/latest](https://dumps.wikimedia.org/simplewiki/latest/): pages-articles.xml.bz2 358.3 MB; multistream 387.9 MB (fetched) | 388 MB bz2 | monthly; listing 2026-10-01 | ~180k pages per old XOWA guide (search). Good for plain-language how-to. |
| Wiktionary | CC BY-SA + GFDL (general knowledge; UNVERIFIED on this search) | As Wikipedia | dumps.wikimedia.org | UNVERIFIED | monthly | Not researched in depth. |
| wikiHow | Search results: CC BY-NC-SA 3.0 for content before 2025 [CC post](https://creativecommons.org/2009/01/30/wikihow-reaches-50000-articles/) (search). A wiki infobox claims a change to "proprietary" after 2025-03-24: **UNVERIFIED**. [terms](https://www.wikihow.com/wikiHow:Terms-of-Use) blocked from fetch. | Credit + NC + SA | No dump found | - | - | **Treat as unusable.** NC blocks sale or prize use; licence status post-2025 unknown. |
| Wikibooks (Cookbook, Survival) | Mixed (see above) | SA | dumps | UNVERIFIED | - | Check per book. |
| Appropedia | CC BY-SA unless an "Open Access" notice says otherwise [CC wiki](https://wiki.creativecommons.org/wiki/Appropedia) (search) | SA | No dump found | - | - | Check per page. |
| iFixit | CC BY-NC-SA (per brief; UNVERIFIED here) | - | - | - | - | NC: exclude. |
| Instructables, CK-12 (CC BY-NC), Khan Academy (CC BY-NC-SA) | per brief; not researched | - | - | - | - | Exclude (NC). |
| OpenStax | Official help centre: **CC BY-NC-SA** for the library (fetched). Older books were CC BY: check each edition. [licensing](https://help.openstax.org/s/article/Licensing-information-of-OpenStax-textbooks) (fetched) | Credit, title, link; SA | Free PDF/web; source files UNVERIFIED | - | - | The brief assumed CC BY; the current page says NC. Exclude current editions. |
| LibreTexts | Mixed CC (UNVERIFIED) | varies | - | - | - | Not researched. |

## 3. Public-domain facts and government data

| Source | Licence | Attribution | Bulk URL / format | Size | Last update | Notes |
|---|---|---|---|---|---|---|
| CIA World Factbook | Text PD; CIA seal not (CIA Act 1949, search). **Site discontinued 2026-02-04** ([WTOP](https://wtop.com/government/2026/02/cia-ends-publication-of-its-popular-world-factbook-reference-tool/), search) | - | GitHub factbook/factbook.json, CC0 [repo](https://github.com/factbook/factbook.json) (fetched); Mozilla Data Collective final snapshot (Jan 2026, CC0) [dataset](https://datacollective.mozillafoundation.org/datasets/cmll4w0ln00nemn07axe7mj09) (search) | JSON | UNVERIFIED | Repo: auto-updated weekly until 2026; no release date shown (fetched) | Use the Mozilla snapshot or the repo snapshot. Frozen, not live. |
| USDA FoodData Central | CC0 1.0; credit requested [download page](https://fdc.nal.usda.gov/download-datasets) (search) | Credit FDC | CSV and JSON, per data type, plus full download | Full CSV: 458 MB zip / 3.1 GB unzipped (Dec 2025) | Dec 2025 release listed | Community SQLite build 430 MB (search, MenuLogistics/USDASQLite). |
| openFDA | Public domain / CC0 1.0, but some data flagged non-PD (copyrighted works supplied by companies) [terms](https://open.fda.gov/terms) (search) | Per dataset docs | API + raw downloads per about page [about](https://open.fda.gov/about) (search); older thread says no bulk | - | - | Check each dataset warning. |
| DailyMed (NLM) | Third-party scraper says PD (secondary). UNVERIFIED on DailyMed itself. | - | SPL XML files | UNVERIFIED | - | Nested XML, harder than JSON. |
| NWS / weather.gov | Open data, free for any purpose; rate-limited; PD status not stated in source [API docs](https://www.weather.gov/documentation/services-web-API) (search) | Credit NWS | REST API (alerts, forecasts) with OpenAPI spec at api.weather.gov/openapi.json; NODD bulk model output on cloud | - | live | API, not bulk. Alerts are useful but must be cached and credited. |
| USGS | US government products PD, credit requested [FAQ](https://www.usgs.gov/faqs/what-usgs-products-are-already-publicly-available) (search); ANSS data policy marked Public Domain [policy](https://www.usgs.gov/media/files/anss-data-and-products-policy) (search) | Credit USGS | GeoJSON feeds (hour/day/week/month) and catalog | - | live | Earthquake feed PD statement: third-party only. Third-party images excluded. |
| NASA | Imagery usable with credit; not blanket PD; logos and third-party/people excluded [media guidelines](https://nasa.gov/nasa-brand-center/images-and-media) (search) | NASA as source; no endorsement | per-image download | - | - | Check each image. Mission sites set own terms. |
| NOAA / NCEI | Official US gov works; token needed for NCEI API (search) | Credit | api.weather.gov, tides, NODD | - | - | Mostly for hazard/tide data. |
| NIST | UNVERIFIED (not researched) | - | - | - | - | - |
| data.gov | Catalog; licences per dataset | per dataset | catalog.data.gov | - | - | Check per dataset (see MedlinePlus conflict). |

## Licence traps

- **NC (non-commercial):** wikiHow (BY-NC-SA 3.0 pre-2025), WHO (BY-NC-SA 3.0 IGO, commercial needs permission [WHO](https://www.who.int/about/policies/publishing/copyright)), OpenStax current books (BY-NC-SA [OpenStax](https://help.openstax.org/s/article/Licensing-information-of-OpenStax-textbooks)), iFixit, CK-12, Khan Academy. A sold app or bounty prize is commercial use. Exclude.
- **SA (share-alike):** Wikipedia/Wiktionary/Simple English/WikiMed/Appropedia/Wikibooks. Any derived pack must carry the same licence. Attribution per article, not just per pack. Decide early whether the pack is a "derivative" (it is, if we transform text).
- **GFDL mixing:** Wikipedia dumps offer GFDL 1.3 and CC BY-SA 4.0; Wikibooks First Aid also cites GFDL 1.2+. Pick one (CC BY-SA) and state it.
- **A.D.A.M. inside MedlinePlus:** Encyclopedia articles, videos, ASHP drug monographs, and most images are licensed to NLM. Not PD. Shipping them needs Ebix or ASHP licence. Filter the XML by source before building. [copyright](https://medlineplus.gov/copyright.html)
- **MedlinePlus Connect / EHR use:** prohibited for copyrighted drug content without vendor licence.
- **Logos and marks:** CDC, WHO, NASA, NHS, FEMA marks are not PD. Do not use logos or imply endorsement (CDC, MedlinePlus, WHO, NASA all say so).
- **Third-party images:** most government sites carry stock or contractor images. Check each.
- **Dump "contains infringement" warning:** Wikimedia says dumps may contain undetected infringements; use at own risk. [dumps legal](https://dumps.wikimedia.org/legal.html)
- **NHS syndication:** a binding licence agreement for API/widget use, even though it is free. [NHS terms](https://www.nhs.uk/our-policies/terms-and-conditions/) (search)

## Open questions

1. Does the MedlinePlus Health Topic XML contain A.D.A.M. encyclopedia text, or only the PD summaries? Test by diffing a sample against encyclopedia URLs. Ask NLM if unsure. UNVERIFIED.
2. Which MedlinePlus licence governs the XML: ODbL (data.gov), CC0 (ODI), or "NLM copyright page" only? Contact NLM for a written answer before redistribution.
3. NHS API syndication terms (refresh rate, licence fee, restrictions): not retrieved. Read nhs.uk syndication terms before any NHS source.
4. wikiHow: did the licence change on or around 2025-03-24? Needs wikihow.com terms (blocked from our fetcher). Irrelevant if we exclude wikiHow anyway.
5. Current WikiMed/MDWiki ZIM size and version: check library.kiwix.org.
6. Is there a bulk export of the Wikibooks First Aid text and its exact licence? Check the book page.
7. Does the CIA Factbook "discontinued" claim hold on primary CIA pages? Only news and third-party sources confirm it. Treat as likely.
8. ready.gov and FEMA publications: confirm the reuse terms on the current ready.gov page (only an archived search snippet was seen).
9. CDC web-page reuse for a pack: scope per page, or ask CDC? Not settled.
10. Mayo Clinic, Red Cross, St John Ambulance, PubMed abstracts (NLM says some copyright applies, not checked here): not researched in this pass. Brief says not open; PubMed licence remains UNVERIFIED.
11. Attribution format for a multi-source pack (one notice per source, plus per-article for SA content): decide before the first build.
