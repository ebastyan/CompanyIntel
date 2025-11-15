# 📊 CompanyIntel Romania

Platformă de analiză financiară pentru 8,390 companii din sectorul gestiunii deșeurilor din România.

## 🚀 Features

### 🏠 Pagina Principală (`index.html`)
- **Căutare CIF**: Caută companii după Codul de Identificare Fiscală
- **Filtrare avansată**: Filtrare după Județ, Oraș, COD CAEN
- **Vizualizare date**: 17 indicatori financiari pentru fiecare companie
- **Istoric 12 ani**: Date de la 2013 până în 2024
- **Warning sistem**: Identificare companii potențial închise

### 📊 Analytics Dashboard (`analitica.html`)

Dashboard-ul de analiză oferă 5 tipuri de analize comprehensive:

#### 1️⃣ Tendințe & Creștere
- Top 50 companii cu cea mai rapidă creștere (CAGR 2020-2024)
- Analiza impactului COVID-19
- Cele mai profitabile companii
- Graficonuri interactive

#### 2️⃣ Sănătate Financiară
- Scoring sistem (0-100 puncte) pentru fiecare companie
- Categorii: EXCELENT, BUN, MODERAT, SLAB, RISC ÎNALT
- Top 50 companii cu cea mai bună sănătate financiară
- Distribuție scoruri și categorii de risc

#### 3️⃣ Segmentare
- **Mărime**: MICRO, MIC, MEDIU, MARE
- **Specializare CAEN**: Deșeuri nepericuloase, periculoase, demolări, etc.
- **Model de business** (BCG Matrix):
  - ⭐ STARS: Profit înalt + Creștere înaltă
  - 🐮 CASH COWS: Profit înalt + Creștere moderată
  - ❓ QUESTION MARKS: Profit scăzut + Creștere înaltă
  - 🐕 DOGS: Profit scăzut + Creștere scăzută

#### 4️⃣ Analiză Geografică
- Statistici per județ (79 județe)
- Top 15 județe după cifră de afaceri
- Piețe monopolizate vs. fragmentate
- Total angajați per regiune

#### 5️⃣ Predicții & Risc
- **Predicții venituri 2025** (top 100 companii)
- **Risc faliment**: 534 companii identificate
  - 232 risc ÎNALT
  - 302 risc MEDIU
- Detectare anomalii (salturi/scăderi >100%)

## 📈 Statistici

```
✅ 8,390 companii în baza de date
✅ 5,306 companii cu date complete (nume, adresă, telefon)
✅ 3,651 companii analizate (cu date financiare 2023)
✅ 79 județe acoperite
✅ 12 ani istoric (2013-2024)
✅ 17 indicatori financiari per companie
```

## 🛠️ Tehnologii

### Frontend
- **HTML5/CSS3**: Design responsive
- **Chart.js**: Graficonuri interactive
- **Vanilla JavaScript**: Fără dependențe externe

### Backend
- **Python 3.x**: Analiza datelor
- **PostgreSQL (Neon)**: Baza de date cloud
- **psycopg2**: PostgreSQL adapter

## 📦 Deployment pe Vercel

### Setup
1. Conectează repository-ul GitHub la Vercel
2. Vercel va detecta automat fișierele HTML statice
3. Deploy automat la fiecare push pe `main`

### Environment Variables (pentru API)
```bash
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

## 🔧 Local Development

### Rulare Analytics Engine
```bash
python analytics_engine.py
```

Generează `analytics_results.json` cu toate cele 5 analize.

### Pornire Server Local
```bash
python -m http.server 8000
```

Accesează:
- http://localhost:8000/index.html
- http://localhost:8000/analitica.html

## 📊 Indicatori Financiari

Fiecare companie are 17 indicatori × 12 ani:

1. **Cifra de Afaceri Netă**
2. **Venituri Totale**
3. **Cheltuieli Totale**
4. **Profit Brut**
5. **Pierdere Brut**
6. **Profit Net**
7. **Pierdere Net**
8. **Active Imobilizate**
9. **Active Circulante**
10. **Stocuri**
11. **Creanțe**
12. **Datorii**
13. **Provizioane**
14. **Capitaluri Total**
15. **Patrimoniul Regiei**
16. **Salariați**
17. **COD CAEN**

## 🎨 Design

- **Culori principale**: 
  - Albastru `#0F7CC0` (primar)
  - Portocaliu `#f78153` (accent)
- **Inspirație**: listafirme.ro, termene.ro
- **Layout**: 3 taburi pentru date financiare
- **Responsive**: Mobile-friendly

## 📝 License

© 2024 CompanyIntel Romania. All rights reserved.

---

🤖 Built with [Claude Code](https://claude.com/claude-code)
