# 📊 CompanyIntel Romania

**Platformă comprehensivă de analiză financiară pentru sectorul gestiunii deșeurilor din România**

Analizează 8,390 companii cu date financiare complete din ultimii 12 ani (2013-2024).

---

## 🚀 Caracteristici Principale

### 🏠 Homepage - Căutare și Filtrare

**Căutare CIF:**
- Caută instant orice companie după Codul de Identificare Fiscală
- **Exemplu**: CIF `29036053` → PAJURCA METAL GROUP S.R.L.
- Vizualizare: 17 indicatori × 12 ani = 204 puncte de date per companie

**Filtrare Avansată:**
- **După Județ**: 79 județe disponibile
- **După Oraș**: Sute de orașe
- **După COD CAEN**: 3811, 3812, 3831, 3832, 4677
- **Checkboxuri**: "Cu Nume", "Cu Adresă", "Cu Telefon"

**3 Taburi Organizate:**
1. **Prezentare Generală** - 5 indicatori principali
2. **Date Financiare Complete** - 7 indicatori detaliat
3. **Active și Pasive** - 9 indicatori

**Funcții Speciale:**
- ✅ Istoric Complet (12 ani)
- ✅ Warning pentru companii închise
- ✅ Graficoane interactive (Chart.js)
- ✅ Export CSV

---

## 📊 Analytics Dashboard - 5 Analize Profesionale

### 1️⃣ Tendințe & Creștere

**Analizează:**
- CAGR (Compound Annual Growth Rate) 2020-2024
- Impact COVID-19 (2019 vs 2020)
- Evoluție profitabilitate
- Creștere angajați

**Top Insights:**
```
🏆 Top Creștere: CIF 6845918 → CAGR 887.1%
📈 COVID Winner: CIF 24452968 → +78,371%
💰 Top Profitabil: 45M+ RON profit net (2023)
```

**Output:**
- Top 50 companii creștere rapidă
- Graficoane bar + line charts
- Tabele interactive sortabile

---

### 2️⃣ Sănătate Financiară - Scoring (0-100)

**7 Criterii:**
1. Marjă Profit (20 puncte)
2. Ratio Datorii (20 puncte)
3. Lichiditate (15 puncte)
4. Creștere 3 ani (15 puncte)
5. Capital pozitiv (10 puncte)
6. Creștere angajați (10 puncte)
7. Productivitate (10 puncte)

**Categorii:**
```
🌟 EXCELENT (80-100):    447 companii
✅ BUN (60-80):          823 companii
⚠️ MODERAT (40-60):    1,204 companii
❌ SLAB (20-40):         789 companii
🔴 RISC ÎNALT (<20):     388 companii
```

**Medie sector:** 49.3/100

---

### 3️⃣ Segmentare - BCG Matrix

**Mărime:**
- MICRO (58.8%): <10 angajați
- MIC (28.0%): 10-50 angajați
- MEDIU (10.9%): 50-250 angajați
- MARE (2.3%): 250+ angajați

**BCG Business Model:**
- ⭐ **STARS** (20): Profit înalt + Creștere înaltă
- 🐮 **CASH COWS** (20): Profit înalt + Creștere moderată
- ❓ **QUESTION MARKS** (845): Profit scăzut + Creștere înaltă
- 🐕 **DOGS** (2,766): Profit scăzut + Creștere scăzută

---

### 4️⃣ Analiză Geografică - 79 Județe

**Top 5 Județe (Cifră Afaceri):**
```
1. ARAD:       2.5B RON (48 companii)
2. CLUJ:       1.8B RON (156 companii)
3. TIMIȘ:      1.6B RON (127 companii)
4. BUCUREȘTI:  1.4B RON (289 companii)
5. IAȘI:       987M RON (94 companii)
```

**Analiză:**
- 30 județe monopolizate (1 jucător >50%)
- 12 județe fragmentate (>50 companii)
- Statistici complete per județ

---

### 5️⃣ Predicții & Risc Faliment

**Predicții 2025:**
- Time series analysis (CAGR)
- Top 100 companii cu creștere prognozată
- CIF 18309735: +167,075% (!)

**Risc Faliment:**
```
🔴 RISC ÎNALT (>70):     232 companii
🟠 RISC MEDIU (50-70):   302 companii
🟢 RISC SCĂZUT (<50):  3,117 companii
```

**Factori risc:**
- Pierderi consecutive 3 ani (40 pt)
- Capital negativ (30 pt)
- Datorii >80% venituri (20 pt)
- Scădere venituri -30% (10 pt)

---

## 📈 Statistici Globale

```
🏢 Total Companii:              8,390
✅ Cu Date Complete:            5,306 (63%)
📊 Analizate (fin. 2023):       3,651 (43%)
🗺️ Județe:                         79
📅 Ani Istoric:                    12
💼 Total Angajați (2023):    ~124,000
💰 Cifră Afaceri (2023):     ~45.6B RON
```

---

## 🛠️ Tehnologii

**Frontend:**
- HTML5/CSS3 + Vanilla JS
- Chart.js 4.4 (graficoane)
- Responsive design

**Backend:**
- Python 3.11+ (analytics)
- PostgreSQL 15 (Neon Cloud)
- Flask API

**Deployment:**
- Vercel (hosting)
- GitHub (CI/CD)

---

## 📦 Deployment Vercel

**Setup:**
1. Conectează GitHub la Vercel
2. Deploy automat la push
3. Set environment: `DATABASE_URL`

**URLs:**
- Homepage: `/`
- Analytics: `/analitica.html`
- API: `/api/search?cif=123`

---

## 🔧 Development Local

**Clone & Setup:**
```bash
git clone https://github.com/ebastyan/CompanyIntel.git
cd CompanyIntel
pip install psycopg2-binary
export DATABASE_URL="postgresql://..."
```

**Run Analytics:**
```bash
python analytics_engine.py
# Output: analytics_results.json
```

**Start Server:**
```bash
python -m http.server 8000
# http://localhost:8000
```

---

## 📊 Indicatori Financiari (17 total)

**Venituri:** Cifră Afaceri, Venituri Totale, Cheltuieli
**Profit:** Profit/Pierdere Brut, Profit/Pierdere Net
**Active:** Imobilizate, Circulante, Stocuri, Creanțe
**Pasive:** Datorii, Provizioane
**Capital:** Capitaluri Total, Patrimoniul Regiei
**Operațional:** Salariați, COD CAEN

---

## 🎨 Design System

**Culori:**
- Primary Blue: `#0F7CC0`
- Accent Orange: `#f78153`
- Success Green: `#2ecc71`
- Warning Yellow: `#f39c12`
- Danger Red: `#e74c3c`

**Components:**
- Cards: border-radius 8-12px
- Tables: sticky headers, sortable
- Charts: responsive Chart.js

---

## 📂 Structura Proiect

```
CompanyIntel/
├── index.html              # Homepage
├── analitica.html          # Analytics dashboard
├── analytics_engine.py     # Python analytics (5 types)
├── analytics_results.json  # Pre-generated data
├── api/
│   └── app.py             # Flask API
├── vercel.json            # Vercel config
└── README.md              # Documentation
```

---

## 📝 License

© 2024 CompanyIntel Romania. All rights reserved.

---

## 🙏 Credits

- **Ministerul Finanțelor** - Date publice
- **Neon Database** - PostgreSQL cloud
- **Vercel** - Deployment
- **Chart.js** - Visualizations

---

🤖 **Built with [Claude Code](https://claude.com/claude-code)**
