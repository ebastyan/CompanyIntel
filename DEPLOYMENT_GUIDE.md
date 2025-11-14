# 🚀 CompanyIntel Deployment Guide

## Ami Elkészült

### 1. **Neon DB Struktúra** ✅
- Tábla neve: `companii`
- **8,390 CIF** egyedi cég
- **205 oszlop** - uniformizált ROMÁN nevek
- **12 év** adat (2013-2024)
- **17 könyvelési mező** évente

### 2. **Flask API** ✅
- `/api/search?cif=XXXXX` - CIF keresés
- `/api/stats` - Statisztikák
- `/api/health` - Health check

### 3. **Frontend** ✅
- Modern, responsive HTML/CSS/JS
- CIF keresés
- Évenkénti táblázat
- Román nyelvű

---

## 📋 Deployment Lépések (Vercel)

### 1. Neon DB Feltöltés

**Lokálisan (ha működik a hálózat):**
```bash
export DATABASE_URL='postgresql://neondb_owner:npg_otTyEmd6lAH9@ep-tiny-sunset-a4gek1az-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

python3 upload_bilanturi_to_neon.py
```

**Eredmény:**
- 8,390 rekord feltöltve
- `companii` tábla létrehozva
- Indexek létrehozva (cif, cifra_2023, cifra_2024)

---

### 2. Vercel Environment Variables

Menj a Vercel Dashboard → Settings → Environment Variables:

```
DATABASE_URL = postgresql://neondb_owner:npg_otTyEmd6lAH9@ep-tiny-sunset-a4gek1az-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**VAGY** használd a Neon integráció-t:
- Vercel Dashboard → Integrations → Neon
- Automatikusan beállítja a `DATABASE_URL`-t

---

### 3. Git Push és Deploy

```bash
# Fájlok hozzáadása
git add api/ frontend/ upload_bilanturi_to_neon.py requirements.txt vercel.json

# Commit
git commit -m "Add Flask API and frontend for CIF search"

# Push
git push origin claude/fix-existing-issues-01XfBT11ep658MwdRcNR1YTQ
```

Vercel automatikusan deployol!

---

### 4. Adatbázis Feltöltés Vercel-ről (ha lokálisan nem működött)

**Opció A - Vercel CLI:**
```bash
vercel env pull .env.local
python3 upload_bilanturi_to_neon.py
```

**Opció B - GitHub Actions:** (opcionális)
Hozz létre `.github/workflows/upload-db.yml`:

```yaml
name: Upload to Neon DB

on:
  workflow_dispatch:

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install psycopg2-binary
      - run: python upload_bilanturi_to_neon.py
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

Secrets beállítása:
- GitHub Repo → Settings → Secrets → New repository secret
- Név: `DATABASE_URL`
- Érték: a Neon connection string

---

## 🧪 Tesztelés

### Lokális Tesztelés (Flask)

```bash
# Függőségek
pip install -r requirements.txt

# Environment
export DATABASE_URL='postgresql://...'

# Indítás
cd api
python app.py
```

Frontend: http://localhost:5000

### API Tesztelés

```bash
# Health check
curl http://localhost:5000/api/health

# Keresés
curl http://localhost:5000/api/search?cif=27820

# Stats
curl http://localhost:5000/api/stats
```

---

## 📊 Adatbázis Struktúra

### Tábla: `companii`

| Oszlop | Típus | Leírás |
|--------|-------|--------|
| `id` | SERIAL | Primary key |
| `cif` | VARCHAR(50) | **UNIQUE** - CIF szám |
| | | |
| **2013-2024 (minden évre):** | | |
| `an_YYYY` | INTEGER | Év |
| `active_imobilizate_YYYY` | BIGINT | Befektetett eszközök |
| `active_circulante_YYYY` | BIGINT | Forgóeszközök |
| `stocuri_YYYY` | BIGINT | Készletek |
| `creante_YYYY` | BIGINT | Követelések |
| `datorii_YYYY` | BIGINT | Tartozások |
| `provizioane_YYYY` | BIGINT | Céltartalékok |
| `capitaluri_total_YYYY` | BIGINT | Saját tőke |
| `patrimoniul_regiei_YYYY` | BIGINT | Önkormányzati vagyon |
| `cifra_de_afaceri_neta_YYYY` | BIGINT | **Nettó árbevétel** |
| `venituri_totale_YYYY` | BIGINT | Összes bevétel |
| `cheltuieli_totale_YYYY` | BIGINT | Összes költség |
| `profit_brut_YYYY` | BIGINT | Bruttó profit |
| `pierdere_brut_YYYY` | BIGINT | Bruttó veszteség |
| `profit_net_YYYY` | BIGINT | **Nettó profit** |
| `pierdere_net_YYYY` | BIGINT | Nettó veszteség |
| `salariati_YYYY` | INTEGER | **Alkalmazottak száma** |

**Indexek:**
- `idx_companii_cif` - CIF gyors keresés
- `idx_companii_cifra_2023` - 2023 árbevétel rendezés
- `idx_companii_cifra_2024` - 2024 árbevétel rendezés

---

## 🌐 Frontend Funkciók

1. **CIF Keresés**
   - Input mező CIF-hez
   - Real-time keresés

2. **Eredmény Táblázat**
   - Minden év külön sor
   - 8 fő oszlop:
     - Év
     - Cifra de Afaceri Netă
     - Profit Net
     - Pierdere Net
     - Salariați
     - Active Imobilizate
     - Active Circulante
     - Datorii

3. **Statisztikák**
   - Összes cég száma
   - Évek száma
   - Indikátorok száma

---

## 🔧 Troubleshooting

### "could not translate host name"
- Sandbox környezetben normális
- Vercel-en működni fog

### "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "relation companii does not exist"
```bash
python3 upload_bilanturi_to_neon.py
```

### Vercel deployment hiba
- Ellenőrizd: `vercel.json` helyes-e
- Environment variables beállítva?
- `requirements.txt` létezik?

---

## 📝 Következő Lépések

1. ✅ Adatbázis feltöltése (`upload_bilanturi_to_neon.py`)
2. ✅ Git push
3. ✅ Vercel environment variables beállítása
4. ✅ Frontend tesztelése
5. 🔄 További adatok hozzáadása (cégnév, email, cím, stb.)

---

## 🎯 API Endpoints

### GET `/api/search?cif=XXXXX`

**Response:**
```json
{
  "cif": "27820",
  "years": [
    {
      "an": 2024,
      "cifra_de_afaceri_neta": 19701875,
      "profit_net": 5680385,
      "salariati": 39,
      ...
    },
    ...
  ]
}
```

### GET `/api/stats`

**Response:**
```json
{
  "total_companies": 8390,
  "top_companies_2023": [
    {"cif": "18992904", "revenue": 1381211345},
    ...
  ]
}
```

### GET `/api/health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "companies": 8390
}
```

---

**Készítette:** Claude
**Dátum:** 2025-11-14
**Projekt:** CompanyIntel - Baza de Date Financiară
