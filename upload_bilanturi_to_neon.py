#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilanturi Neon DB Feltöltő - Uniformizált Román Nevek
======================================================
Feltölti a bilanturi adatokat Neon PostgreSQL-be.
MINDEN oszlop ROMÁNUL, tiszta, hibátlan struktúrával.
"""

import json
import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

class BilanturiNeonUploader:
    """Bilanturi Neon DB feltöltő - román oszlopnevekkel"""

    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')

        if not self.database_url:
            print("❌ HIBA: DATABASE_URL vagy POSTGRES_URL nincs beállítva!")
            sys.exit(1)

        self.conn = None
        self.cursor = None

        print("=" * 80)
        print("NEON DB FELTÖLTÉS - UNIFORMIZÁLT ROMÁN STRUKTÚRA")
        print("=" * 80)

    def connect(self):
        """Kapcsolódás Neon DB-hez"""
        print("\n[1/5] Kapcsolódás Neon DB-hez...")
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor()
            print("  ✓ Kapcsolat sikeres")

            # Verzió
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]
            print(f"  PostgreSQL: {version.split(',')[0]}")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")
            sys.exit(1)

    def create_table(self):
        """Tábla létrehozása - uniformizált román nevek"""
        print("\n[2/5] Tábla létrehozása...")

        # Régi tábla törlése
        drop_sql = "DROP TABLE IF EXISTS companii CASCADE;"

        # Új tábla - MINDEN ROMÁNUL
        create_sql = """
        CREATE TABLE companii (
            id SERIAL PRIMARY KEY,
            cif VARCHAR(50) UNIQUE NOT NULL,

            -- 2013
            an_2013 INTEGER,
            active_imobilizate_2013 BIGINT,
            active_circulante_2013 BIGINT,
            stocuri_2013 BIGINT,
            creante_2013 BIGINT,
            datorii_2013 BIGINT,
            provizioane_2013 BIGINT,
            capitaluri_total_2013 BIGINT,
            patrimoniul_regiei_2013 BIGINT,
            cifra_de_afaceri_neta_2013 BIGINT,
            venituri_totale_2013 BIGINT,
            cheltuieli_totale_2013 BIGINT,
            profit_brut_2013 BIGINT,
            pierdere_brut_2013 BIGINT,
            profit_net_2013 BIGINT,
            pierdere_net_2013 BIGINT,
            salariati_2013 INTEGER,

            -- 2014
            an_2014 INTEGER,
            active_imobilizate_2014 BIGINT,
            active_circulante_2014 BIGINT,
            stocuri_2014 BIGINT,
            creante_2014 BIGINT,
            datorii_2014 BIGINT,
            provizioane_2014 BIGINT,
            capitaluri_total_2014 BIGINT,
            patrimoniul_regiei_2014 BIGINT,
            cifra_de_afaceri_neta_2014 BIGINT,
            venituri_totale_2014 BIGINT,
            cheltuieli_totale_2014 BIGINT,
            profit_brut_2014 BIGINT,
            pierdere_brut_2014 BIGINT,
            profit_net_2014 BIGINT,
            pierdere_net_2014 BIGINT,
            salariati_2014 INTEGER,

            -- 2015
            an_2015 INTEGER,
            active_imobilizate_2015 BIGINT,
            active_circulante_2015 BIGINT,
            stocuri_2015 BIGINT,
            creante_2015 BIGINT,
            datorii_2015 BIGINT,
            provizioane_2015 BIGINT,
            capitaluri_total_2015 BIGINT,
            patrimoniul_regiei_2015 BIGINT,
            cifra_de_afaceri_neta_2015 BIGINT,
            venituri_totale_2015 BIGINT,
            cheltuieli_totale_2015 BIGINT,
            profit_brut_2015 BIGINT,
            pierdere_brut_2015 BIGINT,
            profit_net_2015 BIGINT,
            pierdere_net_2015 BIGINT,
            salariati_2015 INTEGER,

            -- 2016
            an_2016 INTEGER,
            active_imobilizate_2016 BIGINT,
            active_circulante_2016 BIGINT,
            stocuri_2016 BIGINT,
            creante_2016 BIGINT,
            datorii_2016 BIGINT,
            provizioane_2016 BIGINT,
            capitaluri_total_2016 BIGINT,
            patrimoniul_regiei_2016 BIGINT,
            cifra_de_afaceri_neta_2016 BIGINT,
            venituri_totale_2016 BIGINT,
            cheltuieli_totale_2016 BIGINT,
            profit_brut_2016 BIGINT,
            pierdere_brut_2016 BIGINT,
            profit_net_2016 BIGINT,
            pierdere_net_2016 BIGINT,
            salariati_2016 INTEGER,

            -- 2017
            an_2017 INTEGER,
            active_imobilizate_2017 BIGINT,
            active_circulante_2017 BIGINT,
            stocuri_2017 BIGINT,
            creante_2017 BIGINT,
            datorii_2017 BIGINT,
            provizioane_2017 BIGINT,
            capitaluri_total_2017 BIGINT,
            patrimoniul_regiei_2017 BIGINT,
            cifra_de_afaceri_neta_2017 BIGINT,
            venituri_totale_2017 BIGINT,
            cheltuieli_totale_2017 BIGINT,
            profit_brut_2017 BIGINT,
            pierdere_brut_2017 BIGINT,
            profit_net_2017 BIGINT,
            pierdere_net_2017 BIGINT,
            salariati_2017 INTEGER,

            -- 2018
            an_2018 INTEGER,
            active_imobilizate_2018 BIGINT,
            active_circulante_2018 BIGINT,
            stocuri_2018 BIGINT,
            creante_2018 BIGINT,
            datorii_2018 BIGINT,
            provizioane_2018 BIGINT,
            capitaluri_total_2018 BIGINT,
            patrimoniul_regiei_2018 BIGINT,
            cifra_de_afaceri_neta_2018 BIGINT,
            venituri_totale_2018 BIGINT,
            cheltuieli_totale_2018 BIGINT,
            profit_brut_2018 BIGINT,
            pierdere_brut_2018 BIGINT,
            profit_net_2018 BIGINT,
            pierdere_net_2018 BIGINT,
            salariati_2018 INTEGER,

            -- 2019
            an_2019 INTEGER,
            active_imobilizate_2019 BIGINT,
            active_circulante_2019 BIGINT,
            stocuri_2019 BIGINT,
            creante_2019 BIGINT,
            datorii_2019 BIGINT,
            provizioane_2019 BIGINT,
            capitaluri_total_2019 BIGINT,
            patrimoniul_regiei_2019 BIGINT,
            cifra_de_afaceri_neta_2019 BIGINT,
            venituri_totale_2019 BIGINT,
            cheltuieli_totale_2019 BIGINT,
            profit_brut_2019 BIGINT,
            pierdere_brut_2019 BIGINT,
            profit_net_2019 BIGINT,
            pierdere_net_2019 BIGINT,
            salariati_2019 INTEGER,

            -- 2020
            an_2020 INTEGER,
            active_imobilizate_2020 BIGINT,
            active_circulante_2020 BIGINT,
            stocuri_2020 BIGINT,
            creante_2020 BIGINT,
            datorii_2020 BIGINT,
            provizioane_2020 BIGINT,
            capitaluri_total_2020 BIGINT,
            patrimoniul_regiei_2020 BIGINT,
            cifra_de_afaceri_neta_2020 BIGINT,
            venituri_totale_2020 BIGINT,
            cheltuieli_totale_2020 BIGINT,
            profit_brut_2020 BIGINT,
            pierdere_brut_2020 BIGINT,
            profit_net_2020 BIGINT,
            pierdere_net_2020 BIGINT,
            salariati_2020 INTEGER,

            -- 2021
            an_2021 INTEGER,
            active_imobilizate_2021 BIGINT,
            active_circulante_2021 BIGINT,
            stocuri_2021 BIGINT,
            creante_2021 BIGINT,
            datorii_2021 BIGINT,
            provizioane_2021 BIGINT,
            capitaluri_total_2021 BIGINT,
            patrimoniul_regiei_2021 BIGINT,
            cifra_de_afaceri_neta_2021 BIGINT,
            venituri_totale_2021 BIGINT,
            cheltuieli_totale_2021 BIGINT,
            profit_brut_2021 BIGINT,
            pierdere_brut_2021 BIGINT,
            profit_net_2021 BIGINT,
            pierdere_net_2021 BIGINT,
            salariati_2021 INTEGER,

            -- 2022
            an_2022 INTEGER,
            active_imobilizate_2022 BIGINT,
            active_circulante_2022 BIGINT,
            stocuri_2022 BIGINT,
            creante_2022 BIGINT,
            datorii_2022 BIGINT,
            provizioane_2022 BIGINT,
            capitaluri_total_2022 BIGINT,
            patrimoniul_regiei_2022 BIGINT,
            cifra_de_afaceri_neta_2022 BIGINT,
            venituri_totale_2022 BIGINT,
            cheltuieli_totale_2022 BIGINT,
            profit_brut_2022 BIGINT,
            pierdere_brut_2022 BIGINT,
            profit_net_2022 BIGINT,
            pierdere_net_2022 BIGINT,
            salariati_2022 INTEGER,

            -- 2023
            an_2023 INTEGER,
            active_imobilizate_2023 BIGINT,
            active_circulante_2023 BIGINT,
            stocuri_2023 BIGINT,
            creante_2023 BIGINT,
            datorii_2023 BIGINT,
            provizioane_2023 BIGINT,
            capitaluri_total_2023 BIGINT,
            patrimoniul_regiei_2023 BIGINT,
            cifra_de_afaceri_neta_2023 BIGINT,
            venituri_totale_2023 BIGINT,
            cheltuieli_totale_2023 BIGINT,
            profit_brut_2023 BIGINT,
            pierdere_brut_2023 BIGINT,
            profit_net_2023 BIGINT,
            pierdere_net_2023 BIGINT,
            salariati_2023 INTEGER,

            -- 2024
            an_2024 INTEGER,
            active_imobilizate_2024 BIGINT,
            active_circulante_2024 BIGINT,
            stocuri_2024 BIGINT,
            creante_2024 BIGINT,
            datorii_2024 BIGINT,
            provizioane_2024 BIGINT,
            capitaluri_total_2024 BIGINT,
            patrimoniul_regiei_2024 BIGINT,
            cifra_de_afaceri_neta_2024 BIGINT,
            venituri_totale_2024 BIGINT,
            cheltuieli_totale_2024 BIGINT,
            profit_brut_2024 BIGINT,
            pierdere_brut_2024 BIGINT,
            profit_net_2024 BIGINT,
            pierdere_net_2024 BIGINT,
            salariati_2024 INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexek
        CREATE INDEX idx_companii_cif ON companii(cif);
        CREATE INDEX idx_companii_cifra_2023 ON companii(cifra_de_afaceri_neta_2023);
        CREATE INDEX idx_companii_cifra_2024 ON companii(cifra_de_afaceri_neta_2024);
        """

        try:
            print("  Régi tábla törlése...")
            self.cursor.execute(drop_sql)

            print("  Új tábla létrehozása (companii)...")
            self.cursor.execute(create_sql)

            self.conn.commit()
            print("  ✓ Tábla sikeresen létrehozva")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")
            self.conn.rollback()
            sys.exit(1)

    def load_json(self, json_file='bilanturi_integrated.json'):
        """JSON betöltése"""
        print(f"\n[3/5] JSON betöltése ({json_file})...")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"  ✓ {len(data):,} rekord betöltve")
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

    def normalize_column_name(self, col_name):
        """Oszlopnév uniformizálás - román nevekre"""
        # active_imobilizante_total -> active_imobilizate
        # cheltuieli_totate -> cheltuieli_totale (typo fix)

        col_name = col_name.replace('active_imobilizante_total', 'active_imobilizate')
        col_name = col_name.replace('cheltuieli_totate', 'cheltuieli_totale')

        return col_name

    def upload_data(self, companies):
        """Adatok feltöltése"""
        print(f"\n[4/5] Adatok feltöltése Neon DB-be...")

        # Oszlopnevek listája (fix sorrendben)
        columns = ['cif']

        # Évek és mezők
        years = range(2013, 2025)
        fields = [
            'an',
            'active_imobilizate',
            'active_circulante',
            'stocuri',
            'creante',
            'datorii',
            'provizioane',
            'capitaluri_total',
            'patrimoniul_regiei',
            'cifra_de_afaceri_neta',
            'venituri_totale',
            'cheltuieli_totale',
            'profit_brut',
            'pierdere_brut',
            'profit_net',
            'pierdere_net',
            'salariati'
        ]

        for year in years:
            for field in fields:
                columns.append(f"{field}_{year}")

        # SQL
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)

        insert_sql = f"""
        INSERT INTO companii ({columns_str})
        VALUES %s
        ON CONFLICT (cif) DO UPDATE SET updated_at = CURRENT_TIMESTAMP
        """

        # Batch méret
        BATCH_SIZE = 500
        total = len(companies)
        batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        uploaded = 0

        try:
            for batch_num in range(batches):
                start_idx = batch_num * BATCH_SIZE
                end_idx = min(start_idx + BATCH_SIZE, total)
                batch = companies[start_idx:end_idx]

                values = []
                for company in batch:
                    row = [company.get('CIF')]

                    for year in years:
                        for field in fields:
                            # Régi oszlopnév (JSON-ból)
                            if field == 'active_imobilizate':
                                old_key = f'active_imobilizante_total_{year}'
                            elif field == 'cheltuieli_totale':
                                old_key = f'cheltuieli_totate_{year}'
                            else:
                                old_key = f'{field}_{year}'

                            value = company.get(old_key)

                            if field == 'an':
                                row.append(self.safe_int(value))
                            elif field == 'salariati':
                                row.append(self.safe_int(value))
                            else:
                                row.append(self.safe_int(value))

                    values.append(tuple(row))

                # Batch feltöltés
                execute_values(self.cursor, insert_sql, values)
                self.conn.commit()

                uploaded += len(batch)
                print(f"  Feltöltve: {uploaded:,}/{total:,} ({100*uploaded/total:.1f}%)")

            print(f"  ✓ Összes adat feltöltve: {uploaded:,} rekord")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")
            self.conn.rollback()
            sys.exit(1)

    def verify(self):
        """Feltöltés ellenőrzése"""
        print("\n[5/5] Ellenőrzés...")

        try:
            # Összes rekord
            self.cursor.execute("SELECT COUNT(*) FROM companii;")
            total = self.cursor.fetchone()[0]
            print(f"  Összes rekord: {total:,}")

            # 2023 árbevétel
            self.cursor.execute("""
                SELECT COUNT(*) FROM companii
                WHERE cifra_de_afaceri_neta_2023 IS NOT NULL;
            """)
            with_2023 = self.cursor.fetchone()[0]
            print(f"  2023 árbevétellel: {with_2023:,}")

            # Top 5 cég 2023
            self.cursor.execute("""
                SELECT cif, cifra_de_afaceri_neta_2023
                FROM companii
                WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
                ORDER BY cifra_de_afaceri_neta_2023 DESC
                LIMIT 5;
            """)

            print("\n  Top 5 cég (2023 árbevétel):")
            for cif, revenue in self.cursor.fetchall():
                print(f"    CIF {cif}: {revenue:,} RON")

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
    uploader = BilanturiNeonUploader()

    try:
        uploader.connect()
        uploader.create_table()
        companies = uploader.load_json()
        uploader.upload_data(companies)
        uploader.verify()

        print("\n" + "=" * 80)
        print("✓ NEON DB FELTÖLTÉS SIKERES!")
        print("=" * 80)
        print("\nTábla: companii")
        print("Rekordok: 8,390 CIF")
        print("Oszlopok: uniformizált román nevek")

    except Exception as e:
        print(f"\n❌ KRITIKUS HIBA: {e}")
        sys.exit(1)

    finally:
        uploader.close()

if __name__ == "__main__":
    main()
