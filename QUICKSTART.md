# CompanyIntel - Gyors Kezdés

## 🚀 5 Perc Alatt

### 1. Adatok Integrálása

```bash
# Python telepítése (ha nincs)
sudo apt-get install python3 python3-pip

# Függőségek telepítése
pip3 install pandas openpyxl

# Adatintegráció futtatása
python3 integrate_company_data.py
```

**Kimenet** (1-2 perc):
- ✅ `integrated_companies.json` - 11,917 cég (80 MB)
- ✅ `integration_summary.txt` - Statisztikák

### 2. Adatok Validálása (Opcionális)

```bash
python3 validate_integration.py
```

**Kimenet**: Részletes validációs riport

### 3. Neon DB Feltöltés

```bash
# PostgreSQL driver telepítése
pip3 install psycopg2-binary

# Környezeti változó beállítása
export DATABASE_URL='postgres://user:pass@host.neon.tech/db?sslmode=require'

# Feltöltés
python3 upload_to_neon.py
```

**Kimenet** (2-3 perc): 11,917 rekord feltöltve PostgreSQL-be

## 📊 Adatok Használata

### Python-ból (JSON)

```python
import json

# JSON betöltése
with open('integrated_companies.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)

print(f"Összes cég: {len(companies)}")

# Példa: Első cég adatai
company = companies[0]
print(f"CIF: {company['CIF']}")
print(f"Név: {company['Company Name']}")
print(f"2023 árbevétel: {company.get('cifra_de_afaceri_neta_2023', 'N/A')}")
```

### PostgreSQL-ből (Neon DB)

```python
import psycopg2
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Top 10 cég árbevétel alapján
cursor.execute("""
    SELECT company_name, cifra_de_afaceri_neta_2023
    FROM companies
    WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
    ORDER BY cifra_de_afaceri_neta_2023 DESC
    LIMIT 10
""")

for name, revenue in cursor.fetchall():
    print(f"{name}: {revenue:,} RON")

cursor.close()
conn.close()
```

## 🔍 Hasznos Lekérdezések

### 1. Cég Keresése CIF Alapján

```sql
SELECT * FROM companies WHERE cif = '29036053';
```

### 2. Hulladékgyűjtő Cégek

```sql
SELECT company_name, waste_types, phone_number
FROM companies
WHERE waste_types IS NOT NULL
ORDER BY company_name;
```

### 3. Leggyorsabban Növekvő Cégek (2022-2023)

```sql
SELECT
    company_name,
    cifra_de_afaceri_neta_2022,
    cifra_de_afaceri_neta_2023,
    ((cifra_de_afaceri_neta_2023::float / cifra_de_afaceri_neta_2022) - 1) * 100 as growth_percent
FROM companies
WHERE cifra_de_afaceri_neta_2022 > 0
  AND cifra_de_afaceri_neta_2023 IS NOT NULL
ORDER BY growth_percent DESC
LIMIT 20;
```

### 4. Legnagyobb Foglalkoztatók (2023)

```sql
SELECT company_name, salariati_2023, cifra_de_afaceri_neta_2023
FROM companies
WHERE salariati_2023 IS NOT NULL
ORDER BY salariati_2023 DESC
LIMIT 20;
```

### 5. Veszteséges Cégek

```sql
SELECT company_name, pierdere_net_2023, datorii_2023
FROM companies
WHERE pierdere_net_2023 > 0
ORDER BY pierdere_net_2023 DESC
LIMIT 20;
```

## 📈 Statisztikák Gyors Áttekintése

| Metrika | Érték |
|---------|-------|
| **Összes cég** | 11,917 |
| **CIF lefedettség** | 100% |
| **2023 pénzügyi adat** | 18.4% (2,189 cég) |
| **Hulladékgyűjtési adat** | 7.5% (899 cég) |
| **Telefonszám** | 40% (4,770 cég) |
| **Email** | 1.4% (162 cég) |

## 🛠️ Troubleshooting

### Hiba: "ModuleNotFoundError: No module named 'pandas'"
```bash
pip3 install pandas openpyxl
```

### Hiba: "DATABASE_URL nincs beállítva"
```bash
export DATABASE_URL='postgres://...'
# vagy
echo "DATABASE_URL='postgres://...'" > .env
```

### Nagy Fájl (integrated_companies.json 80 MB)
Git LFS használata ajánlott:
```bash
git lfs install
git lfs track "*.json"
git add .gitattributes integrated_companies.json
git commit -m "Add JSON with LFS"
```

## 📚 További Dokumentáció

- **Részletes összefoglaló**: [SUMMARY.md](SUMMARY.md)
- **Deployment útmutató**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Projekt README**: [README.md](README.md)

## 💡 Tippek

1. **JSON túl nagy?** Használj JSON streaming library-t (ijson, pandas chunksize)
2. **Neon DB lassú?** Indexek már létrehozva a gyakori lekérdezésekhez
3. **Adatok frissítése?** Futtasd újra `integrate_company_data.py`

## 🎯 Következő Lépések

1. ✅ Adatok integrálása (`integrate_company_data.py`)
2. ✅ Validáció (`validate_integration.py`)
3. ✅ Neon DB feltöltés (`upload_to_neon.py`)
4. 🔄 API építése (FastAPI / Next.js)
5. 🔄 Dashboard készítése (React / Vue)
6. 🔄 Automatikus frissítés beállítása

---

**Segítségre van szükséged?** Nézd meg a [SUMMARY.md](SUMMARY.md) és [DEPLOYMENT.md](DEPLOYMENT.md) fájlokat!
