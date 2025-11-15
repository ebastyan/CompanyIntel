#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colectare Dump Company Name Matching
=====================================
Összehasonlítja a colectare dump cégneveit a bővített CIF adatbázissal.
CSAK ELEMZÉS - nem módosít semmit!
"""

import json
import pandas as pd
import re
from difflib import SequenceMatcher

class ColectareNameMatcher:
    """Cégnév matching a colectare dump és CIF enriched között"""

    def __init__(self):
        self.cif_enriched = []
        self.colectare_dump = []

        self.cif_names = {}  # CIF -> normalized names
        self.colectare_names = []  # [(original, normalized), ...]

        self.exact_matches = []
        self.fuzzy_matches = []

        print("=" * 80)
        print("COLECTARE DUMP - CÉGNÉV MATCHING ELEMZÉS")
        print("=" * 80)

    def normalize_company_name(self, name):
        """Cégnév normalizálás összehasonlításhoz"""
        if pd.isna(name) or not name:
            return None

        name = str(name).strip().upper()

        # Formátumok standardizálása
        name = re.sub(r'\s+', ' ', name)  # Többszörös space -> 1 space
        name = re.sub(r'\.', '', name)  # Pontok eltávolítása
        name = re.sub(r'S\s*R\s*L', 'SRL', name)  # S.R.L. / S R L -> SRL
        name = re.sub(r'S\s*A', 'SA', name)  # S.A. / S A -> SA
        name = re.sub(r'S\s*C\s*S', 'SCS', name)  # S.C.S -> SCS
        name = re.sub(r'S\s*C\s*A', 'SCA', name)  # S.C.A -> SCA
        name = re.sub(r'P\s*F\s*A', 'PFA', name)  # P.F.A -> PFA

        # Felesleges szavak eltávolítása
        name = name.replace('SOCIETATE COMERCIALA', '')
        name = name.replace('SOCIETATE', '')
        name = name.replace('COMERCIALA', '')
        name = name.replace('SC', '', 1)  # Első SC eltávolítása

        name = name.strip()

        return name if name else None

    def load_cif_enriched(self):
        """CIF enriched adatok betöltése"""
        print("\n[1/5] CIF enriched betöltése...")

        try:
            with open('cif_enriched.json', 'r', encoding='utf-8') as f:
                self.cif_enriched = json.load(f)

            # CIF -> cégnevek mapping
            for record in self.cif_enriched:
                cif = record['cif']
                names = record.get('company_names', [])

                normalized_names = set()
                for name in names:
                    normalized = self.normalize_company_name(name)
                    if normalized:
                        normalized_names.add(normalized)

                if normalized_names:
                    self.cif_names[cif] = {
                        'original': names,
                        'normalized': normalized_names
                    }

            print(f"  ✓ {len(self.cif_enriched):,} CIF betöltve")
            print(f"  ✓ {len(self.cif_names):,} CIF cégnevekkel")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")

    def load_colectare_dump(self):
        """Colectare dump betöltése"""
        print("\n[2/5] Colectare dump betöltése...")

        try:
            df = pd.read_excel('colectare deseuri punct ro DUMP 2023.xlsx')

            print(f"  ✓ {len(df):,} rekord betöltve")

            # Cégnevek kinyerése és normalizálása
            for idx, row in df.iterrows():
                original_name = row.get('Company Name')

                if pd.notna(original_name):
                    normalized = self.normalize_company_name(original_name)

                    if normalized:
                        self.colectare_names.append({
                            'original': str(original_name).strip(),
                            'normalized': normalized
                        })

            print(f"  ✓ {len(self.colectare_names):,} cégnév kinyerve")

        except Exception as e:
            print(f"  ❌ HIBA: {e}")

    def find_exact_matches(self):
        """Pontos egyezések keresése"""
        print("\n[3/5] Pontos egyezések keresése...")

        # CIF normalized names halmaz
        all_cif_normalized = set()
        for cif, data in self.cif_names.items():
            all_cif_normalized.update(data['normalized'])

        print(f"  CIF adatbázis egyedi cégnevek: {len(all_cif_normalized):,}")

        # Colectare normalized names halmaz
        colectare_normalized = set(c['normalized'] for c in self.colectare_names)
        print(f"  Colectare dump egyedi cégnevek: {len(colectare_normalized):,}")

        # Pontos egyezések
        exact_match_names = all_cif_normalized.intersection(colectare_normalized)

        print(f"\n  🎯 PONTOS EGYEZÉSEK: {len(exact_match_names):,} cégnév")

        # Részletes egyezések
        for colectare_record in self.colectare_names:
            normalized = colectare_record['normalized']

            if normalized in exact_match_names:
                # Keresés melyik CIF-hez tartozik
                matching_cifs = []
                for cif, data in self.cif_names.items():
                    if normalized in data['normalized']:
                        matching_cifs.append(cif)

                self.exact_matches.append({
                    'colectare_name': colectare_record['original'],
                    'normalized': normalized,
                    'matching_cifs': matching_cifs,
                    'cif_count': len(matching_cifs)
                })

        print(f"  ✓ {len(self.exact_matches):,} colectare rekord match-elt")

    def find_fuzzy_matches(self, threshold=0.85):
        """Fuzzy egyezések keresése (hasonló nevek)"""
        print(f"\n[4/5] Fuzzy egyezések keresése (threshold: {threshold})...")

        # Csak azok amik nem exact match
        exact_normalized = set(m['normalized'] for m in self.exact_matches)

        remaining_colectare = [
            c for c in self.colectare_names
            if c['normalized'] not in exact_normalized
        ]

        print(f"  Maradt colectare nevek: {len(remaining_colectare):,}")

        # CIF nevek listája
        all_cif_normalized = []
        for cif, data in self.cif_names.items():
            all_cif_normalized.extend(data['normalized'])

        fuzzy_count = 0

        # Csak az első 1000-et nézem meg (gyorsaság miatt)
        sample_size = min(1000, len(remaining_colectare))

        print(f"  Minta: {sample_size} colectare név vizsgálata...")

        for i, colectare_record in enumerate(remaining_colectare[:sample_size]):
            if i % 200 == 0:
                print(f"    Progress: {i}/{sample_size}...")

            colectare_norm = colectare_record['normalized']

            best_match = None
            best_ratio = 0

            for cif_norm in all_cif_normalized:
                ratio = SequenceMatcher(None, colectare_norm, cif_norm).ratio()

                if ratio > best_ratio and ratio >= threshold:
                    best_ratio = ratio
                    best_match = cif_norm

            if best_match:
                fuzzy_count += 1

                # Ha kevés találat, tároljuk
                if len(self.fuzzy_matches) < 100:
                    self.fuzzy_matches.append({
                        'colectare_name': colectare_record['original'],
                        'colectare_normalized': colectare_norm,
                        'matched_cif_name': best_match,
                        'similarity': best_ratio
                    })

        print(f"\n  🔍 FUZZY EGYEZÉSEK (mintában): {fuzzy_count}/{sample_size} ({100*fuzzy_count/sample_size:.1f}%)")

    def generate_statistics(self):
        """Statisztikák generálása"""
        print("\n[5/5] Statisztikák generálása...")

        total_colectare = len(self.colectare_names)
        total_cif = len(self.cif_names)
        exact_matches = len(self.exact_matches)

        print(f"\n  📊 VÉGSŐ STATISZTIKÁK:")
        print(f"  ═══════════════════════════════════════")
        print(f"  CIF adatbázis (enriched): {total_cif:,} CIF")
        print(f"  Colectare dump: {total_colectare:,} cégnév")
        print(f"")
        print(f"  ✅ PONTOS EGYEZÉSEK: {exact_matches:,} ({100*exact_matches/total_colectare:.2f}%)")

        # Több CIF ugyanarra a névre
        multiple_cif = sum(1 for m in self.exact_matches if m['cif_count'] > 1)
        print(f"  ⚠ Több CIF ugyanarra a névre: {multiple_cif:,}")

        # Top 10 egyező név
        if self.exact_matches:
            print(f"\n  🏆 TOP 10 EGYEZŐ CÉGNÉV:")
            for i, match in enumerate(self.exact_matches[:10], 1):
                print(f"    {i}. {match['colectare_name'][:60]}")
                print(f"       CIF-ek: {', '.join(match['matching_cifs'][:3])}")

        # Fuzzy példák
        if self.fuzzy_matches:
            print(f"\n  🔍 FUZZY MATCH PÉLDÁK (hasonló nevek):")
            for i, match in enumerate(self.fuzzy_matches[:5], 1):
                print(f"    {i}. Colectare: {match['colectare_name'][:50]}")
                print(f"       CIF DB:     {match['matched_cif_name'][:50]}")
                print(f"       Hasonlóság: {match['similarity']:.2%}")

        # Export
        output = {
            'total_colectare_names': total_colectare,
            'total_cif_enriched': total_cif,
            'exact_matches_count': exact_matches,
            'exact_matches_percentage': 100 * exact_matches / total_colectare,
            'exact_matches': self.exact_matches,
            'fuzzy_matches_sample': self.fuzzy_matches
        }

        with open('colectare_matching_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"\n  ✓ Eredmények exportálva: colectare_matching_results.json")

def main():
    """Főprogram"""
    matcher = ColectareNameMatcher()

    matcher.load_cif_enriched()
    matcher.load_colectare_dump()
    matcher.find_exact_matches()
    matcher.find_fuzzy_matches(threshold=0.85)
    matcher.generate_statistics()

    print("\n" + "=" * 80)
    print("✓ ELEMZÉS KÉSZ!")
    print("=" * 80)

if __name__ == "__main__":
    main()
