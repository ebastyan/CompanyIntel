# CompanyIntel Deployment Útmutató

## Áttekintés

Ez a projekt román cégek adatait integrálja különböző forrásokból:
- **Metadata fájlok** (15 db xlsx): COD FISCAL alapú cégadatok
- **Bilanturi fájlok** (12 db csv, 2013-2024): CIF alapú könyvelési adatok
- **Colectare dump** (xlsx): Hulladékgyűjtési extra információk

## Lokális Futtatás

### 1. Adatok Integrálása

```bash
# Python függőségek telepítése
pip install pandas openpyxl

# Adatintegráció futtatása
python3 integrate_company_data.py
```

**Kimenet:**
- `integrated_companies.json` - 11,917 cég integrált adatai (80+ MB)
- `integration_summary.txt` - Részletes statisztikák

### 2. Neon DB Feltöltés

```bash
# Postgres driver telepítése
pip install psycopg2-binary

# Környezeti változó beállítása
export DATABASE_URL='postgres://user:pass@host.neon.tech/db?sslmode=require'

# Feltöltés futtatása
python3 upload_to_neon.py
```

## Vercel Deployment

### 1. Neon DB Létrehozása

1. Hozzon létre Neon projektet: https://neon.tech
2. Másolja ki a CONNECTION STRING-et
3. Állítsa be Vercel-en környezeti változóként

### 2. Vercel Konfiguráció

Vercel Dashboard → Settings → Environment Variables:

```
DATABASE_URL = postgres://user:pass@host.neon.tech/companyintel?sslmode=require
```

### 3. Deployment

```bash
# Git commit és push
git add .
git commit -m "Add integrated company data"
git push origin claude/fix-existing-issues-01XfBT11ep658MwdRcNR1YTQ

# Vercel automatikusan deployal
```

## Adatstruktúra

### Companies Tábla (PostgreSQL)

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    cif VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(500),
    full_address TEXT,
    phone_number VARCHAR(100),
    email VARCHAR(255),

    -- Cég alapadatok
    forma_legala VARCHAR(50),
    data_inceperii_activitatii DATE,
    cod_caen VARCHAR(100),
    capitalul_subscris VARCHAR(100),

    -- Hulladékgyűjtési adatok
    waste_types TEXT,
    waste_descriptions TEXT,
    waste_city VARCHAR(200),

    -- 2023-2024 pénzügyi adatok
    cifra_de_afaceri_neta_2023 BIGINT,
    profit_net_2023 BIGINT,
    salariati_2023 INTEGER,
    -- ... további oszlopok
);
```

## Statisztikák

- **Összes cég:** 11,917
- **CIF lefedettség:** 100%
- **2023 pénzügyi adat:** 18.4% (2,189 cég)
- **Hulladékgyűjtési adat:** 7.5% (899 cég)
- **Telefonszám:** 40% (4,770 cég)
- **Email:** 1.4% (162 cég)

## Fontos Fájlok

```
CompanyIntel/
├── integrate_company_data.py      # Adatintegráció
├── upload_to_neon.py              # Neon DB feltöltés
├── integrated_companies.json      # Integrált adatok (80 MB)
├── integration_summary.txt        # Statisztikák
├── bilant_2013.csv ... 2024.csv   # Könyvelési adatok
├── metale.xlsx, neferoase.xlsx    # Metadata fájlok
└── colectare deseuri...xlsx       # Hulladékgyűjtés
```

## Troubleshooting

### "DATABASE_URL nincs beállítva"
```bash
export DATABASE_URL='postgres://...'
```

### "Module not found: pandas"
```bash
pip install pandas openpyxl psycopg2-binary
```

### "Permission denied: integrated_companies.json"
```bash
chmod 644 integrated_companies.json
```

## API Példák (későbbi használatra)

### Cég keresése CIF alapján
```python
cursor.execute("SELECT * FROM companies WHERE cif = %s", ('29036053',))
```

### Top cégek árbevétel alapján (2023)
```python
cursor.execute("""
    SELECT company_name, cifra_de_afaceri_neta_2023
    FROM companies
    WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
    ORDER BY cifra_de_afaceri_neta_2023 DESC
    LIMIT 10
""")
```

### Hulladékgyűjtő cégek
```python
cursor.execute("""
    SELECT company_name, waste_types
    FROM companies
    WHERE waste_types IS NOT NULL
""")
```

## Támogatás

Kérdések esetén:
- GitHub Issues: https://github.com/yourusername/CompanyIntel/issues
- Email: your@email.com

---

**Utolsó frissítés:** 2025-11-14
**Verzió:** 1.0
