#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload Enriched CIF Data to Neon DB
====================================
Extends existing companii table with enriched metadata:
- Cégnév (company_name)
- Strukturált cím (judet, oras, strada, full_address)
- Telefonszám (phone)
- J szám (j_number)
- COD CAEN (cod_caen)
- Capital subscris (capital)
- Koordináták (latitude, longitude)
"""

import json
import os
import sys
import psycopg2
from psycopg2.extras import execute_values

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DATABASE_URL = os.getenv('DATABASE_URL') or 'postgresql://neondb_owner:npg_otTyEmd6lAH9@ep-tiny-sunset-a4gek1az-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

print("=" * 80)
print("NEON DB ENRICHED DATA UPLOAD")
print("=" * 80)

# Load enriched data
print("\n[1/5] Loading cif_enriched.json...")
with open('cif_enriched.json', 'r', encoding='utf-8') as f:
    enriched_data = json.load(f)

print(f"  ✓ Loaded {len(enriched_data):,} enriched CIF records")

# Connect to database
print("\n[2/5] Connecting to Neon DB...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
print("  ✓ Connected")

# Add new columns to existing table
print("\n[3/5] Adding new columns to companii table...")

new_columns = [
    ("company_name", "TEXT"),
    ("judet", "VARCHAR(100)"),
    ("oras", "VARCHAR(200)"),
    ("strada", "TEXT"),
    ("full_address", "TEXT"),
    ("phone", "VARCHAR(50)"),
    ("j_number", "VARCHAR(50)"),
    ("cod_caen", "TEXT"),
    ("capital", "VARCHAR(100)"),
    ("latitude", "DECIMAL(10, 7)"),
    ("longitude", "DECIMAL(10, 7)"),
]

for col_name, col_type in new_columns:
    try:
        cursor.execute(f"""
            ALTER TABLE companii
            ADD COLUMN IF NOT EXISTS {col_name} {col_type};
        """)
        print(f"  ✓ Added column: {col_name}")
    except Exception as e:
        print(f"  ⚠ Column {col_name} already exists or error: {e}")

conn.commit()
print("  ✓ Schema updated")

# Create indexes for filtering
print("\n[4/5] Creating indexes for filtering...")
indexes = [
    ("idx_companii_company_name", "company_name"),
    ("idx_companii_judet", "judet"),
    ("idx_companii_oras", "oras"),
    ("idx_companii_cod_caen", "cod_caen"),
    ("idx_companii_phone", "phone"),
]

for idx_name, col_name in indexes:
    try:
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS {idx_name} ON companii({col_name});
        """)
        print(f"  ✓ Created index: {idx_name}")
    except Exception as e:
        print(f"  ⚠ Index {idx_name} error: {e}")

conn.commit()

# Update enriched data
print("\n[5/5] Updating enriched data...")
print("  This may take a few minutes...")

BATCH_SIZE = 500
total = len(enriched_data)
updated = 0

for batch_num in range(0, total, BATCH_SIZE):
    batch = enriched_data[batch_num:min(batch_num + BATCH_SIZE, total)]

    for item in batch:
        cif = item['cif']

        # Extract data
        company_name = item['company_names'][0] if item['company_names'] else None

        # Address parsing
        judet = None
        oras = None
        strada = None
        full_address = None
        if item['addresses']:
            addr = item['addresses'][0]
            full_address = addr.get('full')
            if 'parsed' in addr:
                judet = addr['parsed'].get('judet')
                oras = addr['parsed'].get('oras')
                strada = addr['parsed'].get('strada')

        phone = item['phones'][0] if item['phones'] else None
        j_number = item['j_numbers'][0] if item['j_numbers'] else None
        cod_caen = ', '.join(item['cod_caen']) if item['cod_caen'] else None
        capital = item['capital_subscris'][0] if item['capital_subscris'] else None

        # Coordinates
        latitude = None
        longitude = None
        if item['coordinates']:
            coords = item['coordinates'][0]
            if isinstance(coords, dict):
                latitude = coords.get('lat')
                longitude = coords.get('lon')

        # Update database
        try:
            cursor.execute("""
                UPDATE companii
                SET
                    company_name = %s,
                    judet = %s,
                    oras = %s,
                    strada = %s,
                    full_address = %s,
                    phone = %s,
                    j_number = %s,
                    cod_caen = %s,
                    capital = %s,
                    latitude = %s,
                    longitude = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE cif = %s
            """, (
                company_name, judet, oras, strada, full_address,
                phone, j_number, cod_caen, capital,
                latitude, longitude, cif
            ))
            updated += 1
        except Exception as e:
            print(f"  ⚠ Error updating CIF {cif}: {e}")

    conn.commit()
    progress = min(batch_num + BATCH_SIZE, total)
    print(f"  Progress: {progress:,}/{total:,} ({100*progress/total:.1f}%)")

print(f"\n  ✓ Updated {updated:,} records")

# Verification
print("\n[VERIFY] Checking updated data...")
cursor.execute("""
    SELECT
        COUNT(*) as total,
        COUNT(company_name) as with_name,
        COUNT(judet) as with_judet,
        COUNT(oras) as with_oras,
        COUNT(phone) as with_phone,
        COUNT(cod_caen) as with_caen
    FROM companii
""")

row = cursor.fetchone()
print(f"""
  Total records: {row[0]:,}
  With company name: {row[1]:,} ({100*row[1]/row[0]:.1f}%)
  With județ: {row[2]:,} ({100*row[2]/row[0]:.1f}%)
  With oraș: {row[3]:,} ({100*row[3]/row[0]:.1f}%)
  With phone: {row[4]:,} ({100*row[4]/row[0]:.1f}%)
  With COD CAEN: {row[5]:,} ({100*row[5]/row[0]:.1f}%)
""")

# Close connection
cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✓ ENRICHED DATA UPLOAD COMPLETE!")
print("=" * 80)
print("\nNew columns added:")
for col_name, _ in new_columns:
    print(f"  - {col_name}")
print("\nDatabase ready for filtering!")
