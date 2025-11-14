#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilanturi Csak Integráció
==========================
CSAK a bilanturi fájlokat (2013-2024) integrálja CIF alapján.
Minden egyedi CIF-hez minden év összes könyvelési adata.
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

class BilanturiIntegrator:
    """Bilanturi adatok integrálása"""

    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        self.bilanturi_files = []
        self.integrated_df = None

        print("=" * 80)
        print("BILANTURI CSAK INTEGRÁCIÓ - PRECÍZ MŰKÖDÉS")
        print("=" * 80)

    def identify_bilanturi_files(self):
        """Bilanturi fájlok azonosítása (2013-2024)"""
        print("\n[1/6] Bilanturi fájlok azonosítása...")

        for year in range(2013, 2025):
            file = f'bilant_{year}.csv'
            file_path = self.base_path / file
            if file_path.exists():
                self.bilanturi_files.append(file)
                print(f"  ✓ {file}")

        print(f"\nÖsszesen: {len(self.bilanturi_files)} bilanturi fájl")

    def normalize_cif(self, cif_value) -> str:
        """CIF normalizálás - tiszta szám formátum"""
        if pd.isna(cif_value):
            return None

        # String konverzió
        cif_str = str(cif_value).strip().upper()

        # Csak számok
        cif_clean = re.sub(r'[^0-9]', '', cif_str)

        if not cif_clean:
            return None

        # Int-ként visszaadjuk (string formában)
        try:
            return str(int(cif_clean))
        except:
            return None

    def load_and_integrate_bilanturi(self):
        """Bilanturi fájlok betöltése és integrálása"""
        print("\n[2/6] Bilanturi fájlok betöltése és integrálása...")

        all_data = {}  # CIF -> {year -> data}

        for file in sorted(self.bilanturi_files):
            file_path = self.base_path / file
            print(f"\n  Betöltés: {file}...", end=" ")

            try:
                # CSV betöltése
                df = pd.read_csv(file_path)

                # CIF normalizálás
                df['CIF'] = df['cif'].apply(self.normalize_cif)

                # Csak valid CIF-ek
                df = df[df['CIF'].notna()]

                # Év meghatározása
                year = df['an'].iloc[0] if 'an' in df.columns and len(df) > 0 else None

                if not year:
                    print(f"HIBA: nincs év adat!")
                    continue

                print(f"OK - {len(df)} sor, {year} év")

                # Minden CIF-hez hozzáadjuk az adott év adatait
                for idx, row in df.iterrows():
                    cif = row['CIF']

                    if cif not in all_data:
                        all_data[cif] = {}

                    # Év adatainak mentése
                    year_data = {}
                    for col in df.columns:
                        if col not in ['cif', 'CIF']:
                            year_data[f"{col}_{year}"] = row[col]

                    all_data[cif][year] = year_data

            except Exception as e:
                print(f"HIBA: {e}")

        print(f"\n  ✓ Összesen {len(all_data)} egyedi CIF betöltve")

        # DataFrame készítése
        print("\n[3/6] Integrált DataFrame készítése...")

        rows = []
        for cif, years_data in all_data.items():
            row = {'CIF': cif}

            # Minden év adatainak hozzáadása
            for year, year_data in years_data.items():
                row.update(year_data)

            rows.append(row)

        self.integrated_df = pd.DataFrame(rows)

        print(f"  ✓ {len(self.integrated_df)} rekord, {len(self.integrated_df.columns)} oszlop")

        return all_data

    def calculate_statistics(self):
        """Statisztikák számítása"""
        print("\n[4/6] Statisztikák számítása...")

        total_companies = len(self.integrated_df)

        print(f"\n  📊 ÖSSZES EGYEDI CIF: {total_companies:,}")

        # Évenkénti lefedettség
        print("\n  📅 ÉVENKÉNTI LEFEDETTSÉG:")
        print("  " + "-" * 76)

        yearly_coverage = {}

        for year in range(2013, 2025):
            # Árbevétel oszlop jelenléte
            revenue_col = f'cifra_de_afaceri_neta_{year}'

            if revenue_col in self.integrated_df.columns:
                count = self.integrated_df[revenue_col].notna().sum()
                yearly_coverage[year] = count
                print(f"  {year}: {count:5,} cég ({100*count/total_companies:5.2f}%)")
            else:
                yearly_coverage[year] = 0
                print(f"  {year}: NINCS ADAT")

        # Hány cégnek van hány évnyi adata
        print("\n  📈 CÉGEK MEGOSZLÁSA (hány évnyi adat van):")
        print("  " + "-" * 76)

        years_per_company = {}

        for idx, row in self.integrated_df.iterrows():
            cif = row['CIF']
            years_count = 0

            for year in range(2013, 2025):
                revenue_col = f'cifra_de_afaceri_neta_{year}'
                if revenue_col in self.integrated_df.columns and pd.notna(row[revenue_col]):
                    years_count += 1

            if years_count not in years_per_company:
                years_per_company[years_count] = 0
            years_per_company[years_count] += 1

        # Fordított sorrendben (12-től 0-ig)
        for year_count in sorted(years_per_company.keys(), reverse=True):
            company_count = years_per_company[year_count]
            print(f"  {year_count:2d} év adat: {company_count:5,} cég ({100*company_count/total_companies:6.2f}%)")

        # Összesítés
        companies_with_data = sum(count for year_count, count in years_per_company.items() if year_count > 0)
        companies_without_data = years_per_company.get(0, 0)

        print(f"\n  ✓ Legalább 1 év adattal: {companies_with_data:,} cég ({100*companies_with_data/total_companies:.2f}%)")
        print(f"  ✗ Nincs egyetlen év sem: {companies_without_data:,} cég ({100*companies_without_data/total_companies:.2f}%)")

        return {
            'total_companies': total_companies,
            'yearly_coverage': yearly_coverage,
            'years_per_company': years_per_company
        }

    def export_to_json(self, output_file='bilanturi_integrated.json'):
        """JSON export"""
        print(f"\n[5/6] JSON exportálás ({output_file})...")

        # NaN -> None
        df_export = self.integrated_df.copy()
        df_export = df_export.replace({pd.NA: None, float('nan'): None})

        # JSON struktúra
        companies = []
        for idx, row in df_export.iterrows():
            company = row.to_dict()
            companies.append(company)

        # JSON fájl írása
        output_path = self.base_path / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2, default=str)

        file_size = output_path.stat().st_size / 1024 / 1024  # MB
        print(f"  ✓ Exportálva: {len(companies):,} cég, {file_size:.2f} MB")

        return output_path

    def export_summary(self, stats, output_file='bilanturi_summary.txt'):
        """Összefoglaló riport"""
        print(f"\n[6/6] Összefoglaló riport ({output_file})...")

        output_path = self.base_path / output_file

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BILANTURI INTEGRÁCIÓ - ÖSSZEFOGLALÓ RIPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generálva: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("FORRÁS FÁJLOK:\n")
            for file in self.bilanturi_files:
                f.write(f"  - {file}\n")

            f.write(f"\nEREDMÉNYEK:\n")
            f.write(f"  - Összes egyedi CIF: {stats['total_companies']:,}\n")
            f.write(f"  - Oszlopok: {len(self.integrated_df.columns)}\n\n")

            f.write("ÉVENKÉNTI LEFEDETTSÉG:\n")
            for year, count in sorted(stats['yearly_coverage'].items()):
                pct = 100 * count / stats['total_companies']
                f.write(f"  {year}: {count:5,} cég ({pct:5.2f}%)\n")

            f.write("\nCÉGEK MEGOSZLÁSA (évek száma szerint):\n")
            for year_count in sorted(stats['years_per_company'].keys(), reverse=True):
                company_count = stats['years_per_company'][year_count]
                pct = 100 * company_count / stats['total_companies']
                f.write(f"  {year_count:2d} év adat: {company_count:5,} cég ({pct:6.2f}%)\n")

            f.write("\nOSZLOPOK (" + str(len(self.integrated_df.columns)) + "):\n")
            for col in sorted(self.integrated_df.columns):
                if col != 'CIF':
                    non_null = self.integrated_df[col].notna().sum()
                    f.write(f"  - {col}: {non_null:,} rekord\n")

        print(f"  ✓ Riport kész: {output_path}")

def main():
    """Főprogram"""
    integrator = BilanturiIntegrator()

    # 1. Fájlok azonosítása
    integrator.identify_bilanturi_files()

    # 2-3. Betöltés és integráció
    integrator.load_and_integrate_bilanturi()

    # 4. Statisztikák
    stats = integrator.calculate_statistics()

    # 5. JSON export
    integrator.export_to_json()

    # 6. Összefoglaló
    integrator.export_summary(stats)

    print("\n" + "=" * 80)
    print("✓ BILANTURI INTEGRÁCIÓ SIKERESEN BEFEJEZVE!")
    print("=" * 80)
    print("\nKimeneti fájlok:")
    print("  - bilanturi_integrated.json")
    print("  - bilanturi_summary.txt")

    return integrator

if __name__ == "__main__":
    integrator = main()
