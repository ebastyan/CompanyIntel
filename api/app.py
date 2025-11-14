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

        return jsonify({
            'cif': company['cif'],
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
