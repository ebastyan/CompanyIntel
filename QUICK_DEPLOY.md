# 🚀 GYORS DEPLOYMENT - 3 LÉPÉSBEN

## ⚡ 1. Neon DB Feltöltés

```bash
# Vercel-en keresztül (ajánlott)
export DATABASE_URL='postgresql://neondb_owner:npg_otTyEmd6lAH9@ep-tiny-sunset-a4gek1az-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

pip3 install psycopg2-binary

python3 upload_bilanturi_to_neon.py
```

**Eredmény:** 8,390 cég feltöltve a `companii` táblába! ✅

---

## 🌐 2. Vercel Environment Variable

Vercel Dashboard → Settings → Environment Variables:

```
DATABASE_URL = postgresql://neondb_owner:npg_otTyEmd6lAH9@ep-tiny-sunset-a4gek1az-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
```

Mentsd el! ✅

---

## 🎉 3. Deploy

Vercel automatikusan deployolja a push-olt változtatásokat!

Vagy manuálisan:
```bash
vercel --prod
```

Kész! 🎊

---

## 🧪 Tesztelés

### Lokális:
```bash
cd api
export DATABASE_URL='postgresql://...'
pip install -r ../requirements.txt
python app.py
```

Frontend: http://localhost:5000

### Éles:
https://your-project.vercel.app

---

## 📋 Adatbázis Ellenőrzés

```sql
-- Összes cég
SELECT COUNT(*) FROM companii;
-- Eredmény: 8390

-- Top 5 cég 2023
SELECT cif, cifra_de_afaceri_neta_2023
FROM companii
WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
ORDER BY cifra_de_afaceri_neta_2023 DESC
LIMIT 5;
```

---

## ✅ Checklist

- [ ] DATABASE_URL beállítva Vercel-en
- [ ] `python3 upload_bilanturi_to_neon.py` lefutott sikeresen
- [ ] Vercel deployment sikeres
- [ ] Frontend működik (CIF keresés)
- [ ] API endpoints válaszolnak

---

**Minden kész!** 🎉
