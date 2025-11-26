# Ballbar CNC – kalibracja, diagnostyka i raportowanie

Repozytorium zawiera dokumentację oraz skrypty wspierające:
- kalibrację maszyn CNC na podstawie testów ballbar,
- analizę wyników przed i po kalibracji,
- diagnostykę typowych usterek,
- optymalizację nastaw,
- generowanie raportów końcowych.

## Struktura repozytorium

```text
.
├─ docs/
│  ├─ calibration/
│  │  └─ calibration_procedure.md
│  ├─ diagnostics/
│  │  └─ diagnostics_guide.md
│  ├─ optimization/
│  │  └─ optimization_guide.md
│  └─ final_report_template.md
├─ scripts/
│  ├─ ballbar_pipeline.py
│  ├─ post_calib_analysis.py
│  ├─ diagnostics_tools.py
│  └─ optimization_tools.py
├─ data/
│  ├─ raw/
│  ├─ processed/
│  ├─ meta/
│  ├─ analysis/
│  └─ reports/
├─ .gitignore
└─ README.md
```

## Konwencja gałęzi i commitów

### Gałęzie

- `main` – stabilny, przeglądnięty stan repozytorium.
- `feature/post-calib-analysis` – analizy po kalibracji.
- `diagnostics/...` – gałęzie związane z diagnostyką (np. `diagnostics/hysteresis-study`).
- `optimization/...` – gałęzie związane z optymalizacją (np. `optimization/feedrates-tuning`).

### Przykładowa konwencja wiadomości commit

Format:

```text
<typ>: <krótki opis>
```

Przykłady:

- `feat: add basic ballbar data pipeline`
- `fix: correct axis naming in calibration script`
- `docs: update calibration procedure`
- `refactor: split diagnostics tools into separate module`

## Tagowanie wersji

- `v0.1-pre-calib`
- `v0.2-post-calib`
- `v1.0-final-report`

## Podstawowy przepływ pracy

1. Zbieranie danych ballbar do `data/raw/`.
2. Uruchomienie `scripts/ballbar_pipeline.py`.
3. Kalibracja CNC w oparciu o wyniki i praca na gałęzi `feature/post-calib-analysis`.
4. Dalsza diagnostyka (`diagnostics/...`) i optymalizacja (`optimization/...`).
5. Opracowanie końcowego raportu (`docs/final_report_template.md`) i tag `v1.0-final-report`.

## Wymagania

- Python 3.10+
- `pandas`, `matplotlib`