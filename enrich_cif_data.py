#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CIF Enrichment - Metadata Matching
===================================
Összehasonlítja a 8,390 CIF-et a metadata fájlok COD FISCAL-jaival.
Kinyeri: cégnév, strukturált cím, kontakt info, jogi adatok.
"""

import json
import pandas as pd
import re
from pathlib import Path
from collections import defaultdict

class CIFEnricher:
    """CIF adatok bővítése metadata fájlokból"""

    def __init__(self, base_path='.'):
        self.base_path = Path(base_path)
        self.bilanturi_cifs = set()
        self.metadata_files = []
        self.colectare_file = 'colectare deseuri punct ro DUMP 2023.xlsx'

        self.enriched_data = {}
        self.stats = defaultdict(int)

        print("=" * 80)
        print("CIF ENRICHMENT - METADATA MATCHING")
        print("=" * 80)

    def normalize_cif(self, cif_value):
        """CIF normalizálás - FIXED: float → int → str (nem extra 0-k!)"""
        if pd.isna(cif_value):
            return None
        try:
            # HELYES: 29036053.0 → 29036053 (NEM 290360530!)
            return str(int(float(cif_value)))
        except:
            return None

    def parse_address(self, address):
        """Cím strukturálása: megye, város, utca+szám"""
        if pd.isna(address) or not address:
            return {'judet': None, 'oras': None, 'strada': None}

        address = str(address).strip()

        # Megye (Jud. vagy județ)
        judet = None
        judet_match = re.search(r'Jud\.?\s+([A-ZĂÂÎȘȚ][A-ZĂÂÎȘȚa-zăâîșț\s]+)', address, re.IGNORECASE)
        if judet_match:
            judet = judet_match.group(1).strip()

        # Város/Localitate
        oras = None
        # Keresünk "ORAȘ, Jud." vagy "Nr. X, ORAȘ" mintát
        oras_patterns = [
            r',\s*([A-ZĂÂÎȘȚ][A-ZĂÂÎȘȚa-zăâîșț\s]+),\s*(?:Cod\s*Postal|Jud\.)',
            r'(?:STR\.|BD\.|CAL\.)\s+[^,]+,\s*([A-ZĂÂÎȘȚ][A-ZĂÂÎȘȚa-zăâîșț\s]+),',
            r'Nr\.\s*\d+[^,]*,\s*([A-ZĂÂÎȘȚ][A-ZĂÂÎȘȚa-zăâîșț\s]+)',
        ]

        for pattern in oras_patterns:
            match = re.search(pattern, address, re.IGNORECASE)
            if match:
                oras = match.group(1).strip()
                break

        # Ha nincs város, próbáljuk meg a Jud. előtti részt
        if not oras and judet:
            before_jud = address.split('Jud.')[0].strip()
            parts = before_jud.split(',')
            if len(parts) >= 2:
                oras = parts[-1].strip()

        # Utca + szám
        strada = None
        strada_match = re.search(r'((?:STR\.|BD\.|CAL\.|STRADA|BULEVARDUL)\s+[^,]+(?:,\s*Nr\.\s*\d+[^,]*)?)', address, re.IGNORECASE)
        if strada_match:
            strada = strada_match.group(1).strip()
        else:
            # Ha nincs STR/BD/CAL prefix, keresünk "Nr. X" mintát
            nr_match = re.search(r'(Nr\.\s*\d+[^,]*)', address, re.IGNORECASE)
            if nr_match:
                strada = nr_match.group(1).strip()

        return {
            'judet': judet,
            'oras': oras,
            'strada': strada
        }

    def extract_phones(self, phone_str):
        """Telefonszámok kinyerése (több is lehet)"""
        if pd.isna(phone_str) or not phone_str:
            return []

        phone_str = str(phone_str)
        # Keresünk telefonszám mintákat
        phones = re.findall(r'0\d{3}[-\s]?\d{3}[-\s]?\d{3}', phone_str)
        return list(set(phones))

    def extract_emails(self, email_str):
        """Email-ek kinyerése (több is lehet)"""
        if pd.isna(email_str) or not email_str:
            return []

        email_str = str(email_str)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email_str)
        return list(set(emails))

    def load_bilanturi_cifs(self):
        """8,390 CIF betöltése"""
        print("\n[1/6] Bilanturi CIF-ek betöltése...")

        try:
            with open(self.base_path / 'bilanturi_integrated.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            for company in data:
                cif = company.get('CIF')
                if cif:
                    self.bilanturi_cifs.add(cif)
                    # Inicializáljuk az enriched adatot
                    self.enriched_data[cif] = {
                        'cif': cif,
                        'company_names': set(),
                        'addresses': [],
                        'phones': set(),
                        'emails': set(),
                        'j_numbers': set(),
                        'cod_caen': set(),
                        'capital_subscris': set(),
                        'coordinates': set(),
                        'sources': set()
                    }

            print(f"  ✓ {len(self.bilanturi_cifs):,} CIF betöltve")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")

    def identify_metadata_files(self):
        """Metadata fájlok azonosítása"""
        print("\n[2/6] Metadata fájlok azonosítása...")

        candidates = [
            'metale.xlsx', 'neferoase.xlsx', 'aluminiu.xlsx',
            'q_inox.xlsx', 'q_importator_profile_aluminiu.xlsx',
            '2442.xlsx', '2443.xlsx', '2444.xlsx', '2445.xlsx',
            '3811.xlsx', '3812.xlsx', '3821.xlsx', '3831.xlsx', '3832.xlsx',
            '4677.xlsx'
        ]

        for file in candidates:
            if (self.base_path / file).exists():
                self.metadata_files.append(file)
                print(f"  ✓ {file}")

        print(f"\n  Összesen: {len(self.metadata_files)} metadata fájl")

    def process_metadata_files(self):
        """Metadata fájlok feldolgozása"""
        print("\n[3/6] Metadata fájlok feldolgozása...")

        for file in self.metadata_files:
            print(f"\n  Feldolgozás: {file}...")

            try:
                df = pd.read_excel(self.base_path / file)

                if 'COD FISCAL' not in df.columns:
                    print(f"    ⚠ Nincs COD FISCAL oszlop, skip")
                    continue

                df['CIF_normalized'] = df['COD FISCAL'].apply(self.normalize_cif)

                matches = 0
                for idx, row in df.iterrows():
                    cif = row['CIF_normalized']

                    if not cif or cif not in self.bilanturi_cifs:
                        continue

                    matches += 1
                    enriched = self.enriched_data[cif]

                    # Company name
                    if pd.notna(row.get('Company Name')):
                        enriched['company_names'].add(str(row['Company Name']).strip())

                    # Address (strukturált)
                    if pd.notna(row.get('Full Address')):
                        address_str = str(row['Full Address'])
                        parsed = self.parse_address(address_str)
                        enriched['addresses'].append({
                            'full': address_str,
                            'parsed': parsed
                        })

                    # Phones
                    if pd.notna(row.get('Phone Number')):
                        phones = self.extract_phones(str(row['Phone Number']))
                        enriched['phones'].update(phones)

                    # Emails
                    if pd.notna(row.get('Email')):
                        emails = self.extract_emails(str(row['Email']))
                        enriched['emails'].update(emails)

                    # J number (NUMĂR DE ÎNREGISTRARE)
                    if pd.notna(row.get('NUMĂR DE ÎNREGISTRARE')):
                        enriched['j_numbers'].add(str(row['NUMĂR DE ÎNREGISTRARE']).strip())

                    # COD CAEN
                    if pd.notna(row.get('COD CAEN')):
                        enriched['cod_caen'].add(str(row['COD CAEN']).strip())

                    # Capital Subscris
                    if pd.notna(row.get('CAPITALUL SUBSCRIS')):
                        enriched['capital_subscris'].add(str(row['CAPITALUL SUBSCRIS']).strip())

                    # Coordinates
                    if pd.notna(row.get('Co-ordinates')):
                        enriched['coordinates'].add(str(row['Co-ordinates']).strip())

                    # Source
                    enriched['sources'].add(file)

                print(f"    ✓ {matches} CIF match találva")
                self.stats[f'matches_{file}'] = matches

            except Exception as e:
                print(f"    ❌ HIBA: {e}")

    def process_colectare_dump(self):
        """Colectare dump feldolgozása"""
        print("\n[4/6] Colectare dump feldolgozása...")

        try:
            df = pd.read_excel(self.base_path / self.colectare_file)

            # Colectare-ben nincs COD FISCAL, de van Company Name
            # Ezt company name alapján próbáljuk match-elni

            print(f"  ⚠ Colectare dump-ban nincs COD FISCAL")
            print(f"  → Cégnév alapú matching később implementálható")

            # TODO: Fuzzy matching by company name

        except Exception as e:
            print(f"  ❌ HIBA: {e}")

    def calculate_statistics(self):
        """Statisztikák számítása"""
        print("\n[5/6] Statisztikák számítása...")

        total_enriched = 0
        total_with_name = 0
        total_with_address = 0
        total_with_phone = 0
        total_with_email = 0
        total_with_j = 0
        total_with_caen = 0
        total_with_capital = 0
        total_with_coords = 0

        for cif, data in self.enriched_data.items():
            has_any = (
                len(data['company_names']) > 0 or
                len(data['addresses']) > 0 or
                len(data['phones']) > 0 or
                len(data['emails']) > 0 or
                len(data['j_numbers']) > 0 or
                len(data['cod_caen']) > 0 or
                len(data['capital_subscris']) > 0 or
                len(data['coordinates']) > 0
            )

            if has_any:
                total_enriched += 1

            if len(data['company_names']) > 0:
                total_with_name += 1
            if len(data['addresses']) > 0:
                total_with_address += 1
            if len(data['phones']) > 0:
                total_with_phone += 1
            if len(data['emails']) > 0:
                total_with_email += 1
            if len(data['j_numbers']) > 0:
                total_with_j += 1
            if len(data['cod_caen']) > 0:
                total_with_caen += 1
            if len(data['capital_subscris']) > 0:
                total_with_capital += 1
            if len(data['coordinates']) > 0:
                total_with_coords += 1

        self.stats['total_cifs'] = len(self.bilanturi_cifs)
        self.stats['enriched_cifs'] = total_enriched
        self.stats['with_company_name'] = total_with_name
        self.stats['with_address'] = total_with_address
        self.stats['with_phone'] = total_with_phone
        self.stats['with_email'] = total_with_email
        self.stats['with_j_number'] = total_with_j
        self.stats['with_cod_caen'] = total_with_caen
        self.stats['with_capital'] = total_with_capital
        self.stats['with_coordinates'] = total_with_coords

        print(f"\n  📊 STATISZTIKÁK:")
        print(f"  ═══════════════════════════════════════")
        print(f"  Összes CIF: {self.stats['total_cifs']:,}")
        print(f"  Bővített CIF-ek: {total_enriched:,} ({100*total_enriched/self.stats['total_cifs']:.1f}%)")
        print(f"")
        print(f"  Cégnévvel: {total_with_name:,} ({100*total_with_name/total_enriched:.1f}%)")
        print(f"  Címmel: {total_with_address:,} ({100*total_with_address/total_enriched:.1f}%)")
        print(f"  Telefonnal: {total_with_phone:,} ({100*total_with_phone/total_enriched:.1f}%)")
        print(f"  Email-lel: {total_with_email:,} ({100*total_with_email/total_enriched:.1f}%)")
        print(f"  J számmal: {total_with_j:,} ({100*total_with_j/total_enriched:.1f}%)")
        print(f"  COD CAEN-nel: {total_with_caen:,} ({100*total_with_caen/total_enriched:.1f}%)")
        print(f"  Tőkével: {total_with_capital:,} ({100*total_with_capital/total_enriched:.1f}%)")
        print(f"  Koordinátákkal: {total_with_coords:,} ({100*total_with_coords/total_enriched:.1f}%)")

    def export_enriched_data(self, output_file='cif_enriched.json'):
        """Bővített adatok exportálása"""
        print(f"\n[6/6] Export ({output_file})...")

        # Set-eket listára konvertálás
        export_data = []

        for cif, data in self.enriched_data.items():
            # Csak azok amiknek van legalább egy új adata
            if (len(data['company_names']) == 0 and
                len(data['addresses']) == 0 and
                len(data['phones']) == 0 and
                len(data['emails']) == 0 and
                len(data['j_numbers']) == 0 and
                len(data['cod_caen']) == 0 and
                len(data['capital_subscris']) == 0 and
                len(data['coordinates']) == 0):
                continue

            export_record = {
                'cif': cif,
                'company_names': list(data['company_names']),
                'addresses': data['addresses'],
                'phones': list(data['phones']),
                'emails': list(data['emails']),
                'j_numbers': list(data['j_numbers']),
                'cod_caen': list(data['cod_caen']),
                'capital_subscris': list(data['capital_subscris']),
                'coordinates': list(data['coordinates']),
                'sources': list(data['sources'])
            }

            export_data.append(export_record)

        # JSON mentés
        with open(self.base_path / output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        file_size = (self.base_path / output_file).stat().st_size / 1024 / 1024
        print(f"  ✓ Exportálva: {len(export_data):,} bővített CIF, {file_size:.2f} MB")

        # Statisztikák is
        stats_file = output_file.replace('.json', '_stats.txt')
        with open(self.base_path / stats_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CIF ENRICHMENT STATISTICS\n")
            f.write("=" * 80 + "\n\n")

            for key, value in sorted(self.stats.items()):
                f.write(f"{key}: {value:,}\n")

        print(f"  ✓ Statisztikák: {stats_file}")

def main():
    """Főprogram"""
    enricher = CIFEnricher()

    enricher.load_bilanturi_cifs()
    enricher.identify_metadata_files()
    enricher.process_metadata_files()
    enricher.process_colectare_dump()
    enricher.calculate_statistics()
    enricher.export_enriched_data('cif_enriched_fixed.json')  # FIXED VERSION!

    print("\n" + "=" * 80)
    print("✓ CIF ENRICHMENT KÉSZ! (FIXED VERSION)")
    print("=" * 80)
    print("\nKimeneti fájlok:")
    print("  - cif_enriched_fixed.json")
    print("  - cif_enriched_fixed_stats.txt")

if __name__ == "__main__":
    main()
