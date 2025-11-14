#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neon DB Feltöltő Script
========================
Feltölti az integrált cégadatokat Neon PostgreSQL adatbázisba.

Környezeti változó szükséges:
- DATABASE_URL: Neon DB kapcsolati string (postgres://...)
"""

import json
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import re

class NeonDBUploader:
    """Neon DB feltöltő osztály"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')

        if not self.database_url:
            print("❌ HIBA: DATABASE_URL környezeti változó nincs beállítva!")
            print("\nHasználat:")
            print("  export DATABASE_URL='postgres://user:pass@host/db'")
            print("  python3 upload_to_neon.py")
            sys.exit(1)

        self.conn = None
        self.cursor = None

        print("=" * 80)
        print("NEON DB FELTÖLTÉS - PRECÍZ MŰKÖDÉS")
        print("=" * 80)

    def connect(self):
        """Kapcsolódás az adatbázishoz"""
        print("\n[1/5] Kapcsolódás Neon DB-hez...")
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            print("  ✓ Kapcsolat sikeres")

            # Verzió ellenőrzés
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]
            print(f"  PostgreSQL verzió: {version.split(',')[0]}")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")
            sys.exit(1)

    def create_tables(self):
        """Tábla létrehozása vagy újra-létrehozása"""
        print("\n[2/5] Táblák létrehozása...")

        # Régi tábla törlése (ha van)
        drop_table_sql = """
        DROP TABLE IF EXISTS companies CASCADE;
        """

        # Új tábla létrehozása
        create_table_sql = """
        CREATE TABLE companies (
            id SERIAL PRIMARY KEY,
            cif VARCHAR(50) UNIQUE NOT NULL,
            company_name VARCHAR(500),
            full_address TEXT,
            phone_number VARCHAR(100),
            email VARCHAR(255),
            website VARCHAR(500),

            -- Cég alapadatok
            forma_legala VARCHAR(50),
            data_inceperii_activitatii DATE,
            cod_caen VARCHAR(100),
            capitalul_subscris VARCHAR(100),
            status VARCHAR(100),

            -- Metadata
            source_file VARCHAR(100),

            -- Hulladékgyűjtési adatok
            waste_types TEXT,
            waste_descriptions TEXT,
            waste_city VARCHAR(200),
            waste_address TEXT,
            waste_phone VARCHAR(100),
            waste_email VARCHAR(255),

            -- 2023 pénzügyi adatok (példa - legfrissebb)
            active_imobilizante_2023 BIGINT,
            active_circulante_2023 BIGINT,
            stocuri_2023 BIGINT,
            creante_2023 BIGINT,
            datorii_2023 BIGINT,
            provizioane_2023 BIGINT,
            capitaluri_total_2023 BIGINT,
            cifra_de_afaceri_neta_2023 BIGINT,
            venituri_totale_2023 BIGINT,
            cheltuieli_totale_2023 BIGINT,
            profit_brut_2023 BIGINT,
            profit_net_2023 BIGINT,
            pierdere_brut_2023 BIGINT,
            pierdere_net_2023 BIGINT,
            salariati_2023 INTEGER,

            -- 2024 pénzügyi adatok
            active_imobilizante_2024 BIGINT,
            active_circulante_2024 BIGINT,
            cifra_de_afaceri_neta_2024 BIGINT,
            profit_net_2024 BIGINT,
            salariati_2024 INTEGER,

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexek a gyorsabb kereséshez
        CREATE INDEX idx_companies_cif ON companies(cif);
        CREATE INDEX idx_companies_name ON companies(company_name);
        CREATE INDEX idx_companies_cod_caen ON companies(cod_caen);
        CREATE INDEX idx_companies_waste_types ON companies(waste_types);
        """

        try:
            print("  Régi tábla törlése...")
            self.cursor.execute(drop_table_sql)

            print("  Új tábla létrehozása...")
            self.cursor.execute(create_table_sql)

            self.conn.commit()
            print("  ✓ Táblák sikeresen létrehozva")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")
            self.conn.rollback()
            sys.exit(1)

    def load_json_data(self, json_file='integrated_companies.json'):
        """JSON adatok betöltése"""
        print(f"\n[3/5] JSON adatok betöltése ({json_file})...")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"  ✓ {len(data)} rekord betöltve")
            return data

        except Exception as e:
            print(f"  ❌ HIBA: {e}")
            sys.exit(1)

    def safe_int(self, value):
        """Biztonságos int konverzió"""
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except:
            return None

    def safe_date(self, value):
        """Biztonságos dátum konverzió"""
        if value is None or value == '':
            return None
        try:
            # Próbáljuk meg különböző formátumokkal
            if isinstance(value, str):
                # ISO formátum
                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                    return value[:10]
                # DD.MM.YYYY formátum
                elif re.match(r'\d{2}\.\d{2}\.\d{4}', value):
                    parts = value.split('.')
                    return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return None
        except:
            return None

    def upload_data(self, companies_data):
        """Adatok feltöltése batch-ekben"""
        print(f"\n[4/5] Adatok feltöltése Neon DB-be...")

        insert_sql = """
        INSERT INTO companies (
            cif, company_name, full_address, phone_number, email, website,
            forma_legala, data_inceperii_activitatii, cod_caen, capitalul_subscris, status,
            source_file,
            waste_types, waste_descriptions, waste_city, waste_address, waste_phone, waste_email,
            active_imobilizante_2023, active_circulante_2023, stocuri_2023, creante_2023,
            datorii_2023, provizioane_2023, capitaluri_total_2023,
            cifra_de_afaceri_neta_2023, venituri_totale_2023, cheltuieli_totale_2023,
            profit_brut_2023, profit_net_2023, pierdere_brut_2023, pierdere_net_2023,
            salariati_2023,
            active_imobilizante_2024, active_circulante_2024, cifra_de_afaceri_neta_2024,
            profit_net_2024, salariati_2024
        ) VALUES %s
        ON CONFLICT (cif) DO UPDATE SET
            company_name = EXCLUDED.company_name,
            full_address = EXCLUDED.full_address,
            phone_number = EXCLUDED.phone_number,
            email = EXCLUDED.email,
            updated_at = CURRENT_TIMESTAMP
        """

        # Batch méret
        BATCH_SIZE = 500

        total = len(companies_data)
        batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

        uploaded = 0

        try:
            for batch_num in range(batches):
                start_idx = batch_num * BATCH_SIZE
                end_idx = min(start_idx + BATCH_SIZE, total)
                batch = companies_data[start_idx:end_idx]

                # Rekordok előkészítése
                values = []
                for company in batch:
                    record = (
                        company.get('CIF'),
                        company.get('Company Name'),
                        company.get('Full Address'),
                        company.get('Phone Number'),
                        company.get('Email'),
                        company.get('Website'),
                        company.get('FORMA LEGALA'),
                        self.safe_date(company.get('DATA ÎNCEPERII ACTIVITĂŢII')),
                        company.get('COD CAEN'),
                        company.get('CAPITALUL SUBSCRIS'),
                        company.get('STATUS '),
                        company.get('source_file'),
                        company.get('Waste_Types'),
                        company.get('Waste_Descriptions'),
                        company.get('Waste_City'),
                        company.get('Waste_Address'),
                        company.get('Waste_Phone'),
                        company.get('Waste_Email'),
                        # 2023 adatok
                        self.safe_int(company.get('active_imobilizante_total_2023')),
                        self.safe_int(company.get('active_circulante_total_2023')),
                        self.safe_int(company.get('stocuri_2023')),
                        self.safe_int(company.get('creante_2023')),
                        self.safe_int(company.get('datorii_2023')),
                        self.safe_int(company.get('provizioane_2023')),
                        self.safe_int(company.get('capitaluri_total_2023')),
                        self.safe_int(company.get('cifra_de_afaceri_neta_2023')),
                        self.safe_int(company.get('venituri_totale_2023')),
                        self.safe_int(company.get('cheltuieli_totate_2023')),
                        self.safe_int(company.get('profit_brut_2023')),
                        self.safe_int(company.get('profit_net_2023')),
                        self.safe_int(company.get('pierdere_brut_2023')),
                        self.safe_int(company.get('pierdere_net_2023')),
                        self.safe_int(company.get('salariati_2023')),
                        # 2024 adatok
                        self.safe_int(company.get('active_imobilizante_total_2024')),
                        self.safe_int(company.get('active_circulante_total_2024')),
                        self.safe_int(company.get('cifra_de_afaceri_neta_2024')),
                        self.safe_int(company.get('profit_net_2024')),
                        self.safe_int(company.get('salariati_2024')),
                    )
                    values.append(record)

                # Batch feltöltés
                execute_values(self.cursor, insert_sql, values)
                self.conn.commit()

                uploaded += len(batch)
                print(f"  Feltöltve: {uploaded}/{total} rekord ({100*uploaded/total:.1f}%)")

            print(f"  ✓ Összes adat sikeresen feltöltve: {uploaded} rekord")

        except Exception as e:
            print(f"  ❌ HIBA a feltöltés során: {e}")
            self.conn.rollback()
            sys.exit(1)

    def verify_upload(self):
        """Feltöltés ellenőrzése"""
        print("\n[5/5] Feltöltés ellenőrzése...")

        try:
            # Összes rekord
            self.cursor.execute("SELECT COUNT(*) FROM companies;")
            total = self.cursor.fetchone()[0]
            print(f"  Összes rekord: {total}")

            # CIF-fel rendelkező
            self.cursor.execute("SELECT COUNT(*) FROM companies WHERE cif IS NOT NULL;")
            with_cif = self.cursor.fetchone()[0]
            print(f"  CIF-fel: {with_cif}")

            # Pénzügyi adatokkal (2023)
            self.cursor.execute("SELECT COUNT(*) FROM companies WHERE cifra_de_afaceri_neta_2023 IS NOT NULL;")
            with_financial = self.cursor.fetchone()[0]
            print(f"  2023 árbevétellel: {with_financial}")

            # Hulladékgyűjtési adatokkal
            self.cursor.execute("SELECT COUNT(*) FROM companies WHERE waste_types IS NOT NULL;")
            with_waste = self.cursor.fetchone()[0]
            print(f"  Hulladékgyűjtési adatokkal: {with_waste}")

            # Példa rekord
            self.cursor.execute("""
                SELECT cif, company_name, cifra_de_afaceri_neta_2023, waste_types
                FROM companies
                WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
                LIMIT 1;
            """)
            example = self.cursor.fetchone()
            if example:
                print(f"\n  Példa rekord:")
                print(f"    CIF: {example[0]}")
                print(f"    Név: {example[1]}")
                print(f"    2023 árbevétel: {example[2]}")
                print(f"    Hulladék: {example[3]}")

            print("\n  ✓ Ellenőrzés sikeres")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")

    def close(self):
        """Kapcsolat lezárása"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("\n✓ Kapcsolat lezárva")

def main():
    """Főprogram"""

    # Neon DB feltöltő inicializálása
    uploader = NeonDBUploader()

    try:
        # 1. Kapcsolódás
        uploader.connect()

        # 2. Táblák létrehozása
        uploader.create_tables()

        # 3. JSON betöltése
        companies_data = uploader.load_json_data()

        # 4. Feltöltés
        uploader.upload_data(companies_data)

        # 5. Ellenőrzés
        uploader.verify_upload()

        print("\n" + "=" * 80)
        print("✓ NEON DB FELTÖLTÉS SIKERESEN BEFEJEZVE!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ KRITIKUS HIBA: {e}")
        sys.exit(1)

    finally:
        uploader.close()

if __name__ == "__main__":
    main()
