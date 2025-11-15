#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CompanyIntel API - Flask Backend
=================================
Egyszerű API a CIF kereséshez és megjelenítéshez.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
import os
from datetime import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Database kapcsolat
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')

def get_db_connection():
    """Database kapcsolat"""
    return psycopg2.connect(DATABASE_URL)

@app.route('/api/search', methods=['GET'])
def search_company():
    """CIF keresés"""
    cif = request.args.get('cif', '').strip()

    if not cif:
        return jsonify({'error': 'CIF szükséges'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Keresés
        cursor.execute("""
            SELECT * FROM companii WHERE cif = %s
        """, (cif,))

        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Nem található CIF'}), 404

        # Oszlopnevek
        columns = [desc[0] for desc in cursor.description]

        # Dict készítése
        company = dict(zip(columns, row))

        # Évenkénti adatok strukturálása
        years_data = []

        for year in range(2013, 2025):
            year_obj = {
                'an': year,
                'active_imobilizate': company.get(f'active_imobilizate_{year}'),
                'active_circulante': company.get(f'active_circulante_{year}'),
                'stocuri': company.get(f'stocuri_{year}'),
                'creante': company.get(f'creante_{year}'),
                'datorii': company.get(f'datorii_{year}'),
                'provizioane': company.get(f'provizioane_{year}'),
                'capitaluri_total': company.get(f'capitaluri_total_{year}'),
                'patrimoniul_regiei': company.get(f'patrimoniul_regiei_{year}'),
                'cifra_de_afaceri_neta': company.get(f'cifra_de_afaceri_neta_{year}'),
                'venituri_totale': company.get(f'venituri_totale_{year}'),
                'cheltuieli_totale': company.get(f'cheltuieli_totale_{year}'),
                'profit_brut': company.get(f'profit_brut_{year}'),
                'pierdere_brut': company.get(f'pierdere_brut_{year}'),
                'profit_net': company.get(f'profit_net_{year}'),
                'pierdere_net': company.get(f'pierdere_net_{year}'),
                'salariati': company.get(f'salariati_{year}')
            }

            # Csak ha van adat
            if any(v is not None for k, v in year_obj.items() if k != 'an'):
                years_data.append(year_obj)

        cursor.close()
        conn.close()

        # Add enriched metadata
        return jsonify({
            'cif': company['cif'],
            'company_name': company.get('company_name'),
            'judet': company.get('judet'),
            'oras': company.get('oras'),
            'strada': company.get('strada'),
            'full_address': company.get('full_address'),
            'phone': company.get('phone'),
            'j_number': company.get('j_number'),
            'cod_caen': company.get('cod_caen'),
            'capital': company.get('capital'),
            'latitude': float(company['latitude']) if company.get('latitude') else None,
            'longitude': float(company['longitude']) if company.get('longitude') else None,
            'years': years_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def stats():
    """Statisztikák"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Összes rekord
        cursor.execute("SELECT COUNT(*) FROM companii")
        total = cursor.fetchone()[0]

        # 2023 top 10
        cursor.execute("""
            SELECT cif, cifra_de_afaceri_neta_2023
            FROM companii
            WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
            ORDER BY cifra_de_afaceri_neta_2023 DESC
            LIMIT 10
        """)

        top_companies = []
        for cif, revenue in cursor.fetchall():
            top_companies.append({'cif': cif, 'revenue': revenue})

        cursor.close()
        conn.close()

        return jsonify({
            'total_companies': total,
            'top_companies_2023': top_companies
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companii")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'companies': count
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filter values"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get unique județe
        cursor.execute("""
            SELECT DISTINCT judet
            FROM companii
            WHERE judet IS NOT NULL
            ORDER BY judet
        """)
        judete = [row[0] for row in cursor.fetchall()]

        # Get unique orașe
        cursor.execute("""
            SELECT DISTINCT oras
            FROM companii
            WHERE oras IS NOT NULL
            ORDER BY oras
            LIMIT 100
        """)
        orase = [row[0] for row in cursor.fetchall()]

        # Get unique COD CAEN
        cursor.execute("""
            SELECT DISTINCT cod_caen
            FROM companii
            WHERE cod_caen IS NOT NULL
            LIMIT 50
        """)
        cod_caen_list = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({
            'judete': judete,
            'orase': orase,
            'cod_caen': cod_caen_list
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/companies', methods=['GET'])
def list_companies():
    """List companies with filters"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build WHERE clause from filters
        where_clauses = []
        params = []

        # Filter by județ
        judet = request.args.get('judet')
        if judet:
            where_clauses.append("judet = %s")
            params.append(judet)

        # Filter by oraș
        oras = request.args.get('oras')
        if oras:
            where_clauses.append("oras = %s")
            params.append(oras)

        # Filter by COD CAEN (partial match)
        cod_caen = request.args.get('cod_caen')
        if cod_caen:
            where_clauses.append("cod_caen LIKE %s")
            params.append(f'%{cod_caen}%')

        # Filter by has address
        has_address = request.args.get('has_address')
        if has_address == 'true':
            where_clauses.append("full_address IS NOT NULL")
        elif has_address == 'false':
            where_clauses.append("full_address IS NULL")

        # Filter by has name
        has_name = request.args.get('has_name')
        if has_name == 'true':
            where_clauses.append("company_name IS NOT NULL")
        elif has_name == 'false':
            where_clauses.append("company_name IS NULL")

        # Filter by has phone
        has_phone = request.args.get('has_phone')
        if has_phone == 'true':
            where_clauses.append("phone IS NOT NULL")
        elif has_phone == 'false':
            where_clauses.append("phone IS NULL")

        # Build query
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        offset = (page - 1) * per_page

        # Count total
        count_query = f"SELECT COUNT(*) FROM companii WHERE {where_sql}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Get results
        query = f"""
            SELECT cif, company_name, judet, oras, full_address, phone, cod_caen,
                   cifra_de_afaceri_neta_2024, cifra_de_afaceri_neta_2023
            FROM companii
            WHERE {where_sql}
            ORDER BY cifra_de_afaceri_neta_2024 DESC NULLS LAST
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, params + [per_page, offset])

        companies = []
        for row in cursor.fetchall():
            companies.append({
                'cif': row[0],
                'company_name': row[1],
                'judet': row[2],
                'oras': row[3],
                'full_address': row[4],
                'phone': row[5],
                'cod_caen': row[6],
                'cifra_de_afaceri_2024': row[7],
                'cifra_de_afaceri_2023': row[8]
            })

        cursor.close()
        conn.close()

        return jsonify({
            'total': total,
            'page': page,
            'per_page': per_page,
            'companies': companies
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
