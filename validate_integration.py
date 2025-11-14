#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adatintegráció Validációs Script
=================================
Ellenőrzi az integrált adatok minőségét és konzisztenciáját.
"""

import json
import pandas as pd
from collections import defaultdict

class DataValidator:
    """Adatvalidátor osztály"""

    def __init__(self, json_file='integrated_companies.json'):
        self.json_file = json_file
        self.data = None

        print("=" * 80)
        print("ADATVALIDÁCIÓ - MINŐSÉGELLENŐRZÉS")
        print("=" * 80)

    def load_data(self):
        """JSON adatok betöltése"""
        print(f"\n[1/6] JSON betöltése ({self.json_file})...")
        with open(self.json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"  ✓ {len(self.data)} rekord betöltve")

    def validate_cif(self):
        """CIF validáció"""
        print("\n[2/6] CIF validáció...")

        cif_stats = {
            'total': len(self.data),
            'with_cif': 0,
            'unique_cif': set(),
            'duplicates': []
        }

        for company in self.data:
            cif = company.get('CIF')
            if cif:
                cif_stats['with_cif'] += 1
                if cif in cif_stats['unique_cif']:
                    cif_stats['duplicates'].append(cif)
                cif_stats['unique_cif'].add(cif)

        print(f"  Összes rekord: {cif_stats['total']}")
        print(f"  CIF-fel rendelkező: {cif_stats['with_cif']} ({100*cif_stats['with_cif']/cif_stats['total']:.1f}%)")
        print(f"  Egyedi CIF: {len(cif_stats['unique_cif'])}")

        if cif_stats['duplicates']:
            print(f"  ⚠ Duplikált CIF-ek: {len(cif_stats['duplicates'])}")
            print(f"    Példák: {cif_stats['duplicates'][:5]}")
        else:
            print(f"  ✓ Nincs duplikáció")

    def validate_financials(self):
        """Pénzügyi adatok validációja"""
        print("\n[3/6] Pénzügyi adatok validációja...")

        years = range(2013, 2025)
        financial_coverage = defaultdict(int)

        for company in self.data:
            for year in years:
                key = f'cifra_de_afaceri_neta_{year}'
                if company.get(key):
                    financial_coverage[year] += 1

        print("  Éves lefedettség (árbevétel):")
        for year in years:
            count = financial_coverage[year]
            print(f"    {year}: {count} cég ({100*count/len(self.data):.1f}%)")

        # Top 5 cég 2023-ban
        companies_2023 = [
            (c.get('Company Name'), c.get('cifra_de_afaceri_neta_2023'))
            for c in self.data
            if c.get('cifra_de_afaceri_neta_2023')
        ]
        companies_2023.sort(key=lambda x: x[1], reverse=True)

        print("\n  Top 5 cég (2023 árbevétel):")
        for i, (name, revenue) in enumerate(companies_2023[:5], 1):
            print(f"    {i}. {name}: {revenue:,} RON")

    def validate_waste_data(self):
        """Hulladékgyűjtési adatok validációja"""
        print("\n[4/6] Hulladékgyűjtési adatok validációja...")

        waste_stats = {
            'with_waste': 0,
            'waste_types': defaultdict(int)
        }

        for company in self.data:
            if company.get('Waste_Types'):
                waste_stats['with_waste'] += 1

                # Típusok számolása
                types = company.get('Waste_Types', '').split(',')
                for waste_type in types:
                    waste_type = waste_type.strip()
                    if waste_type:
                        waste_stats['waste_types'][waste_type] += 1

        print(f"  Hulladékgyűjtési adattal: {waste_stats['with_waste']} cég ({100*waste_stats['with_waste']/len(self.data):.1f}%)")

        print("\n  Top 10 hulladék típus:")
        sorted_types = sorted(waste_stats['waste_types'].items(), key=lambda x: x[1], reverse=True)
        for i, (waste_type, count) in enumerate(sorted_types[:10], 1):
            print(f"    {i}. {waste_type}: {count} cég")

    def validate_contact_info(self):
        """Kapcsolattartási adatok validációja"""
        print("\n[5/6] Kapcsolattartási adatok validációja...")

        contact_stats = {
            'phone': 0,
            'email': 0,
            'website': 0,
            'waste_phone': 0,
            'waste_email': 0
        }

        for company in self.data:
            if company.get('Phone Number'):
                contact_stats['phone'] += 1
            if company.get('Email'):
                contact_stats['email'] += 1
            if company.get('Website'):
                contact_stats['website'] += 1
            if company.get('Waste_Phone'):
                contact_stats['waste_phone'] += 1
            if company.get('Waste_Email'):
                contact_stats['waste_email'] += 1

        total = len(self.data)
        print(f"  Telefonszám: {contact_stats['phone']} ({100*contact_stats['phone']/total:.1f}%)")
        print(f"  Email: {contact_stats['email']} ({100*contact_stats['email']/total:.1f}%)")
        print(f"  Website: {contact_stats['website']} ({100*contact_stats['website']/total:.1f}%)")
        print(f"  Hulladék telefon: {contact_stats['waste_phone']} ({100*contact_stats['waste_phone']/total:.1f}%)")
        print(f"  Hulladék email: {contact_stats['waste_email']} ({100*contact_stats['waste_email']/total:.1f}%)")

    def generate_sample_records(self, count=5):
        """Mintarekordok generálása"""
        print(f"\n[6/6] {count} teljes mintarekord generálása...")

        # Keressünk cégeket, amelyeknek van pénzügyi és hulladék adatuk is
        full_records = [
            c for c in self.data
            if c.get('cifra_de_afaceri_neta_2023') and c.get('Waste_Types')
        ]

        if not full_records:
            # Ha nincs teljesen feltöltött, akkor bármilyent
            full_records = self.data[:count]

        print(f"\n  Talált {len(full_records)} teljes rekord (pénzügy + hulladék)\n")
        print("=" * 80)

        for i, company in enumerate(full_records[:count], 1):
            print(f"\n[MINTA {i}]")
            print(f"  CIF: {company.get('CIF', 'N/A')}")
            print(f"  Név: {company.get('Company Name', 'N/A')}")
            print(f"  Cím: {company.get('Full Address', 'N/A')}")
            print(f"  Telefon: {company.get('Phone Number', 'N/A')}")
            print(f"  Email: {company.get('Email', 'N/A')}")
            print(f"  Forma legala: {company.get('FORMA LEGALA', 'N/A')}")
            print(f"  COD CAEN: {company.get('COD CAEN', 'N/A')}")
            print(f"  Forrás: {company.get('source_file', 'N/A')}")
            print(f"\n  Pénzügyi adatok (2023):")
            print(f"    Árbevétel: {company.get('cifra_de_afaceri_neta_2023', 'N/A')}")
            print(f"    Profit: {company.get('profit_net_2023', 'N/A')}")
            print(f"    Alkalmazottak: {company.get('salariati_2023', 'N/A')}")
            print(f"    Vagyon (imobilizált): {company.get('active_imobilizante_total_2023', 'N/A')}")
            print(f"    Vagyon (forgóeszköz): {company.get('active_circulante_total_2023', 'N/A')}")
            print(f"\n  Hulladékgyűjtési adatok:")
            print(f"    Típusok: {company.get('Waste_Types', 'N/A')}")
            print(f"    Város: {company.get('Waste_City', 'N/A')}")
            print(f"    Cím: {company.get('Waste_Address', 'N/A')}")
            print(f"    Telefon: {company.get('Waste_Phone', 'N/A')}")
            print("-" * 80)

def main():
    """Főprogram"""
    validator = DataValidator()

    validator.load_data()
    validator.validate_cif()
    validator.validate_financials()
    validator.validate_waste_data()
    validator.validate_contact_info()
    validator.generate_sample_records(count=3)

    print("\n" + "=" * 80)
    print("✓ VALIDÁCIÓ BEFEJEZVE")
    print("=" * 80)

if __name__ == "__main__":
    main()
