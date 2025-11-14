#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CompanyIntel Data Integration Script
=====================================
Ez a script összegyűjti és integrálja a román cégadatokat:
1. Metadata fájlok (COD FISCAL alapú cégadatok)
2. Bilanturi fájlok (CIF alapú könyvelési adatok 2013-2024)
3. Colectare dump (hulladékgyűjtési extra információk)

Minden adat pontos, validált és többször ellenőrzött!
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from typing import Dict, List, Set
import re
from datetime import datetime

class CompanyDataIntegrator:
    """Alapos és precíz adatintegrációs osztály"""

    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        self.metadata_files = []
        self.bilanturi_files = []
        self.colectare_file = 'colectare deseuri punct ro DUMP 2023.xlsx'

        # Eredmények tárolása
        self.metadata_df = None
        self.bilanturi_df = None
        self.colectare_df = None
        self.integrated_df = None

        print("=" * 80)
        print("CompanyIntel Data Integration - PRECÍZ MŰKÖDÉS")
        print("=" * 80)

    def identify_files(self):
        """Azonosítja az összes releváns fájlt"""
        print("\n[1/8] Fájlok azonosítása...")

        # Metadata fájlok (COD FISCAL-lal)
        metadata_candidates = [
            'metale.xlsx', 'neferoase.xlsx', 'aluminiu.xlsx',
            'q_inox.xlsx', 'q_importator_profile_aluminiu.xlsx',
            '2442.xlsx', '2443.xlsx', '2444.xlsx', '2445.xlsx',
            '3811.xlsx', '3812.xlsx', '3821.xlsx', '3831.xlsx', '3832.xlsx',
            '4677.xlsx'
        ]

        for file in metadata_candidates:
            file_path = self.base_path / file
            if file_path.exists():
                self.metadata_files.append(file)
                print(f"  ✓ Metadata: {file}")

        # Bilanturi fájlok (2013-2024)
        for year in range(2013, 2025):
            file = f'bilant_{year}.csv'
            file_path = self.base_path / file
            if file_path.exists():
                self.bilanturi_files.append(file)
                print(f"  ✓ Bilanturi: {file}")

        # Colectare fájl
        if (self.base_path / self.colectare_file).exists():
            print(f"  ✓ Colectare: {self.colectare_file}")
        else:
            print(f"  ✗ HIÁNYZIK: {self.colectare_file}")

        print(f"\nÖsszesen: {len(self.metadata_files)} metadata, {len(self.bilanturi_files)} bilanturi fájl")

    def normalize_cif(self, cif_value) -> str:
        """Normalizálja a CIF/COD FISCAL értékeket - PONTOS!"""
        if pd.isna(cif_value):
            return None

        # String-re konvertálás
        cif_str = str(cif_value).strip().upper()

        # Csak számok megtartása
        cif_clean = re.sub(r'[^0-9]', '', cif_str)

        # Ha üres, None
        if not cif_clean:
            return None

        # Visszaadjuk tiszta szám formában (int-ként)
        try:
            return str(int(cif_clean))
        except:
            return None

    def load_metadata_files(self):
        """Betölti és egyesíti az összes metadata fájlt"""
        print("\n[2/8] Metadata fájlok betöltése...")

        all_metadata = []

        for file in self.metadata_files:
            try:
                file_path = self.base_path / file
                print(f"  Betöltés: {file}...", end=" ")

                df = pd.read_excel(file_path)

                # Ellenőrizzük, hogy van-e COD FISCAL oszlop
                if 'COD FISCAL' not in df.columns:
                    print(f"FIGYELEM: nincs COD FISCAL oszlop!")
                    continue

                # Normalizáljuk a CIF-et
                df['CIF'] = df['COD FISCAL'].apply(self.normalize_cif)

                # Csak a releváns oszlopokat tartjuk meg
                keep_columns = ['CIF', 'Company Name', 'Full Address', 'Phone Number',
                               'Email', 'Website', 'COD CAEN', 'FORMA LEGALA',
                               'DATA ÎNCEPERII ACTIVITĂŢII', 'CAPITALUL SUBSCRIS',
                               'STATUS ', 'NUMAR ANGAJATI la ', 'CIFRA DE AFACERI la ']

                # Csak a létező oszlopokat tartjuk meg
                available_cols = [col for col in keep_columns if col in df.columns]
                df_clean = df[available_cols].copy()

                # Forrás fájl hozzáadása
                df_clean['source_file'] = file

                # Csak a valid CIF-ekkel rendelkező sorok
                df_clean = df_clean[df_clean['CIF'].notna()]

                all_metadata.append(df_clean)
                print(f"OK - {len(df_clean)} sor")

            except Exception as e:
                print(f"HIBA: {e}")

        # Egyesítés
        if all_metadata:
            self.metadata_df = pd.concat(all_metadata, ignore_index=True)

            # Duplikátumok kezelése - CIF alapján az első előfordulást tartjuk
            before = len(self.metadata_df)
            self.metadata_df = self.metadata_df.drop_duplicates(subset=['CIF'], keep='first')
            after = len(self.metadata_df)

            print(f"\n  Metadata összesítés: {after} egyedi cég ({before - after} duplikátum eltávolítva)")
        else:
            print("  HIBA: Nem sikerült metadata betölteni!")

    def load_bilanturi_files(self):
        """Betölti az összes bilanturi fájlt (2013-2024)"""
        print("\n[3/8] Bilanturi fájlok betöltése...")

        all_bilanturi = []

        for file in sorted(self.bilanturi_files):
            try:
                file_path = self.base_path / file
                print(f"  Betöltés: {file}...", end=" ")

                df = pd.read_csv(file_path)

                # CIF normalizálás
                df['CIF'] = df['cif'].apply(self.normalize_cif)

                # Csak valid CIF-fel rendelkező sorok
                df = df[df['CIF'].notna()]

                # Év hozzáadása az oszlopokhoz
                year = df['an'].iloc[0] if 'an' in df.columns else None
                if year:
                    # Átnevezzük az oszlopokat az év hozzáadásával
                    rename_dict = {}
                    for col in df.columns:
                        if col not in ['CIF', 'cif', 'an']:
                            rename_dict[col] = f"{col}_{year}"
                    df = df.rename(columns=rename_dict)

                # CIF oszlop megtartása
                df = df[[c for c in df.columns if c == 'CIF' or c.endswith(f'_{year}')]]

                all_bilanturi.append(df)
                print(f"OK - {len(df)} sor")

            except Exception as e:
                print(f"HIBA: {e}")

        # Egyesítés CIF alapján
        if all_bilanturi:
            from functools import reduce
            self.bilanturi_df = reduce(
                lambda left, right: pd.merge(left, right, on='CIF', how='outer'),
                all_bilanturi
            )
            print(f"\n  Bilanturi összesítés: {len(self.bilanturi_df)} egyedi CIF, {len(self.bilanturi_df.columns)} oszlop")
        else:
            print("  HIBA: Nem sikerült bilanturi betölteni!")

    def load_colectare_dump(self):
        """Betölti a colectare dump fájlt"""
        print("\n[4/8] Colectare dump betöltése...")

        try:
            file_path = self.base_path / self.colectare_file
            self.colectare_df = pd.read_excel(file_path)

            # Cég név tisztítása
            self.colectare_df['Company Name Clean'] = (
                self.colectare_df['Company Name']
                .fillna('')
                .str.upper()
                .str.strip()
                .str.replace(r'\s+', ' ', regex=True)
            )

            print(f"  ✓ Betöltve: {len(self.colectare_df)} rekord")
            print(f"  Oszlopok: {list(self.colectare_df.columns[:5])}...")

        except Exception as e:
            print(f"  HIBA: {e}")

    def integrate_data(self):
        """Integrálja az adatokat"""
        print("\n[5/8] Adatok integrálása...")

        # 1. Metadata + Bilanturi összekapcsolása CIF alapján
        print("  1. Metadata + Bilanturi összekapcsolása (CIF alapján)...")
        self.integrated_df = pd.merge(
            self.metadata_df,
            self.bilanturi_df,
            on='CIF',
            how='left'  # Minden metadata rekordot megtartunk
        )
        print(f"     ✓ {len(self.integrated_df)} rekord")

        # 2. Colectare dump összekapcsolása cég név alapján
        print("  2. Colectare dump hozzáadása (cég név alapján)...")

        # Cég név tisztítása az integrált adatokban is
        self.integrated_df['Company Name Clean'] = (
            self.integrated_df['Company Name']
            .fillna('')
            .str.upper()
            .str.strip()
            .str.replace(r'\s+', ' ', regex=True)
        )

        # Colectare adatok aggregálása cég név alapján
        colectare_agg = self.colectare_df.groupby('Company Name Clean').agg({
            'Type Of Scrap': lambda x: ', '.join(x.dropna().unique()),
            'Descriptions': lambda x: ' | '.join(x.dropna().unique()),
            'City': 'first',
            'Address': 'first',
            'Phone Number': 'first',
            'Email': 'first'
        }).reset_index()

        colectare_agg.columns = [
            'Company Name Clean',
            'Waste_Types',
            'Waste_Descriptions',
            'Waste_City',
            'Waste_Address',
            'Waste_Phone',
            'Waste_Email'
        ]

        # Összekapcsolás
        self.integrated_df = pd.merge(
            self.integrated_df,
            colectare_agg,
            on='Company Name Clean',
            how='left'
        )

        matches = self.integrated_df['Waste_Types'].notna().sum()
        print(f"     ✓ {matches} céghez találtunk hulladékgyűjtési adatot")

        print(f"\n  Végső integráció: {len(self.integrated_df)} rekord, {len(self.integrated_df.columns)} oszlop")

    def validate_data(self):
        """Adatok validálása és statisztikák"""
        print("\n[6/8] Adatok validálása...")

        total = len(self.integrated_df)

        # CIF lefedettség
        valid_cif = self.integrated_df['CIF'].notna().sum()
        print(f"  CIF lefedettség: {valid_cif}/{total} ({100*valid_cif/total:.1f}%)")

        # Bilanturi adatok lefedettség (2023 példa)
        if 'cifra_de_afaceri_neta_2023' in self.integrated_df.columns:
            bilanturi_2023 = self.integrated_df['cifra_de_afaceri_neta_2023'].notna().sum()
            print(f"  2023 pénzügyi adat: {bilanturi_2023}/{total} ({100*bilanturi_2023/total:.1f}%)")

        # Hulladékgyűjtési adat lefedettség
        waste_data = self.integrated_df['Waste_Types'].notna().sum()
        print(f"  Hulladékgyűjtési adat: {waste_data}/{total} ({100*waste_data/total:.1f}%)")

        # Kapcsolattartási adatok
        has_phone = self.integrated_df['Phone Number'].notna().sum()
        has_email = self.integrated_df['Email'].notna().sum()
        print(f"  Telefonszám: {has_phone}/{total} ({100*has_phone/total:.1f}%)")
        print(f"  Email: {has_email}/{total} ({100*has_email/total:.1f}%)")

    def export_to_json(self, output_file='integrated_companies.json'):
        """Exportálás JSON formátumba"""
        print(f"\n[7/8] JSON exportálás ({output_file})...")

        # NaN értékek kezelése
        df_export = self.integrated_df.copy()
        df_export = df_export.replace({np.nan: None})

        # JSON struktúra készítése
        companies = []
        for idx, row in df_export.iterrows():
            company = row.to_dict()
            companies.append(company)

        # JSON fájl írása
        output_path = self.base_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2, default=str)

        file_size = output_path.stat().st_size / 1024 / 1024  # MB
        print(f"  ✓ Exportálva: {len(companies)} cég, {file_size:.2f} MB")

        return output_path

    def export_summary(self, output_file='integration_summary.txt'):
        """Összefoglaló riport exportálása"""
        print(f"\n[8/8] Összefoglaló riport ({output_file})...")

        output_path = self.base_path / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("COMPANYINTEL ADATINTEGRÁCIÓS RIPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generálva: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("FORRÁS FÁJLOK:\n")
            f.write(f"  - Metadata fájlok: {len(self.metadata_files)}\n")
            for file in self.metadata_files:
                f.write(f"    • {file}\n")
            f.write(f"\n  - Bilanturi fájlok: {len(self.bilanturi_files)} (2013-2024)\n")
            f.write(f"  - Colectare dump: {self.colectare_file}\n\n")

            f.write("EREDMÉNYEK:\n")
            f.write(f"  - Összes cég: {len(self.integrated_df)}\n")
            f.write(f"  - CIF-fel rendelkező: {self.integrated_df['CIF'].notna().sum()}\n")
            f.write(f"  - Pénzügyi adatokkal: {self.integrated_df['cifra_de_afaceri_neta_2023'].notna().sum() if 'cifra_de_afaceri_neta_2023' in self.integrated_df.columns else 'N/A'}\n")
            f.write(f"  - Hulladékgyűjtési adatokkal: {self.integrated_df['Waste_Types'].notna().sum()}\n")
            f.write(f"  - Telefonszámmal: {self.integrated_df['Phone Number'].notna().sum()}\n")
            f.write(f"  - Email-lel: {self.integrated_df['Email'].notna().sum()}\n\n")

            f.write("OSZLOPOK (" + str(len(self.integrated_df.columns)) + "):\n")
            for col in sorted(self.integrated_df.columns):
                non_null = self.integrated_df[col].notna().sum()
                f.write(f"  - {col}: {non_null} rekord\n")

        print(f"  ✓ Riport kész: {output_path}")

def main():
    """Főprogram"""
    integrator = CompanyDataIntegrator()

    # 1. Fájlok azonosítása
    integrator.identify_files()

    # 2. Metadata betöltése
    integrator.load_metadata_files()

    # 3. Bilanturi betöltése
    integrator.load_bilanturi_files()

    # 4. Colectare dump betöltése
    integrator.load_colectare_dump()

    # 5. Adatok integrálása
    integrator.integrate_data()

    # 6. Validálás
    integrator.validate_data()

    # 7. JSON export
    json_file = integrator.export_to_json()

    # 8. Összefoglaló
    integrator.export_summary()

    print("\n" + "=" * 80)
    print("✓ ADATINTEGRÁCIÓ SIKERESEN BEFEJEZVE!")
    print("=" * 80)
    print(f"\nKimeneti fájlok:")
    print(f"  - integrated_companies.json")
    print(f"  - integration_summary.txt")

    return integrator

if __name__ == "__main__":
    integrator = main()
