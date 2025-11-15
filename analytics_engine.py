#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analytics Engine - Romanian Waste Management Sector
====================================================
Comprehensive analysis of 8,390 companies with financial data.

5 Analysis Types:
1. Trend Analysis (Growth/Decline 2013-2024)
2. Financial Health Score (Rating 0-100)
3. Company Segmentation (Clusters)
4. Geographic Analysis (by Județ)
5. Time Series & Predictions
"""

import os
import sys
import psycopg2
import json
from datetime import datetime
from collections import defaultdict
import statistics

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DATABASE_URL = os.getenv('DATABASE_URL') or 'postgresql://neondb_owner:npg_otTyEmd6lAH9@ep-tiny-sunset-a4gek1az-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)

def safe_division(numerator, denominator, default=0):
    """Safe division with default value"""
    try:
        if denominator and denominator != 0:
            return numerator / denominator
    except:
        pass
    return default

def calculate_cagr(start_value, end_value, years):
    """Calculate Compound Annual Growth Rate"""
    try:
        if start_value and end_value and years > 0 and start_value > 0:
            return ((end_value / start_value) ** (1 / years) - 1) * 100
    except:
        pass
    return 0

# =============================================================================
# ANALYSIS 1: TREND ANALYSIS (Analiza Tendințe)
# =============================================================================

def analyze_trends():
    """
    Analyze growth/decline trends 2013-2024
    Returns: Companies with fastest growth, decline, COVID impact
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("ANALYSIS 1: TREND ANALYSIS (Analiza Tendințe)")
    print("="*80)

    # Get all companies with multi-year data
    cursor.execute("""
        SELECT
            cif,
            company_name,
            cifra_de_afaceri_neta_2024,
            cifra_de_afaceri_neta_2023,
            cifra_de_afaceri_neta_2022,
            cifra_de_afaceri_neta_2021,
            cifra_de_afaceri_neta_2020,
            cifra_de_afaceri_neta_2019,
            cifra_de_afaceri_neta_2018,
            cifra_de_afaceri_neta_2017,
            cifra_de_afaceri_neta_2016,
            cifra_de_afaceri_neta_2015,
            cifra_de_afaceri_neta_2014,
            cifra_de_afaceri_neta_2013,
            profit_net_2024,
            profit_net_2023,
            profit_net_2022,
            pierdere_net_2024,
            pierdere_net_2023,
            pierdere_net_2022,
            salariati_2024,
            salariati_2023,
            salariati_2013
        FROM companii
        WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
    """)

    companies = []
    for row in cursor.fetchall():
        cif = row[0]
        name = row[1] or f"CIF {cif}"

        # Revenue data
        revenues = {
            2024: row[2], 2023: row[3], 2022: row[4], 2021: row[5],
            2020: row[6], 2019: row[7], 2018: row[8], 2017: row[9],
            2016: row[10], 2015: row[11], 2014: row[12], 2013: row[13]
        }

        # Calculate CAGR (2020-2024 - last 4 years)
        rev_2020 = revenues.get(2020) or 0
        rev_2024 = revenues.get(2024) or revenues.get(2023) or 0

        if rev_2020 > 0 and rev_2024 > 0:
            cagr = calculate_cagr(rev_2020, rev_2024, 4)
        else:
            cagr = 0

        # COVID impact (2019 vs 2020)
        rev_2019 = revenues.get(2019) or 0
        rev_2020_val = revenues.get(2020) or 0
        covid_impact = safe_division((rev_2020_val - rev_2019), rev_2019, 0) * 100

        # Net profit 2023
        profit_2023 = (row[15] or 0) - (row[18] or 0)
        profit_2024 = (row[14] or 0) - (row[17] or 0)

        # Employee change
        sal_2024 = row[20] or 0
        sal_2013 = row[22] or 0
        employee_change = sal_2024 - sal_2013

        companies.append({
            'cif': cif,
            'name': name,
            'revenue_2024': rev_2024,
            'revenue_2023': revenues.get(2023) or 0,
            'revenue_2020': rev_2020,
            'revenue_2013': revenues.get(2013) or 0,
            'cagr': cagr,
            'covid_impact': covid_impact,
            'profit_2023': profit_2023,
            'profit_2024': profit_2024,
            'employees_2024': sal_2024,
            'employee_change': employee_change
        })

    # Sort by CAGR
    fastest_growth = sorted(companies, key=lambda x: x['cagr'], reverse=True)[:50]
    fastest_decline = sorted(companies, key=lambda x: x['cagr'])[:50]

    # COVID winners/losers
    covid_winners = sorted(companies, key=lambda x: x['covid_impact'], reverse=True)[:30]
    covid_losers = sorted(companies, key=lambda x: x['covid_impact'])[:30]

    # Profitable companies
    most_profitable = sorted(
        [c for c in companies if c['profit_2023'] > 0],
        key=lambda x: x['profit_2023'],
        reverse=True
    )[:50]

    cursor.close()
    conn.close()

    return {
        'fastest_growth': fastest_growth,
        'fastest_decline': fastest_decline,
        'covid_winners': covid_winners,
        'covid_losers': covid_losers,
        'most_profitable': most_profitable,
        'total_analyzed': len(companies)
    }

# =============================================================================
# ANALYSIS 2: FINANCIAL HEALTH SCORE (Scor Sănătate Financiară)
# =============================================================================

def calculate_financial_health_score():
    """
    Calculate financial health score (0-100) for each company
    Based on: profit margin, debt ratio, liquidity, growth, capital
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("ANALYSIS 2: FINANCIAL HEALTH SCORE (Scor Sănătate Financiară)")
    print("="*80)

    cursor.execute("""
        SELECT
            cif,
            company_name,
            cifra_de_afaceri_neta_2023,
            profit_net_2023,
            pierdere_net_2023,
            venituri_totale_2023,
            datorii_2023,
            creante_2023,
            capitaluri_total_2023,
            active_imobilizate_2023,
            salariati_2023,
            salariati_2020,
            cifra_de_afaceri_neta_2020
        FROM companii
        WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
    """)

    companies_scores = []

    for row in cursor.fetchall():
        cif = row[0]
        name = row[1] or f"CIF {cif}"
        revenue = row[2] or 0
        profit = (row[3] or 0) - (row[4] or 0)
        total_income = row[5] or 0
        datorii = row[6] or 0
        creante = row[7] or 0
        capital = row[8] or 0
        active = row[9] or 0
        sal_2023 = row[10] or 0
        sal_2020 = row[11] or 0
        rev_2020 = row[12] or 0

        # Calculate score components
        score = 0
        reasons = []

        # 1. Profit Margin (20 points)
        profit_margin = safe_division(profit, revenue, 0) * 100
        if profit_margin > 10:
            score += 20
            reasons.append(f"Marjă profit >10% ({profit_margin:.1f}%)")
        elif profit_margin > 5:
            score += 15
            reasons.append(f"Marjă profit >5% ({profit_margin:.1f}%)")
        elif profit_margin > 0:
            score += 10
            reasons.append(f"Profitabil ({profit_margin:.1f}%)")

        # 2. Debt Ratio (20 points)
        debt_ratio = safe_division(datorii, total_income, 0) * 100
        if debt_ratio < 30:
            score += 20
            reasons.append(f"Datorii mici <30% ({debt_ratio:.1f}%)")
        elif debt_ratio < 50:
            score += 15
            reasons.append(f"Datorii moderate <50% ({debt_ratio:.1f}%)")
        elif debt_ratio < 80:
            score += 10

        # 3. Liquidity (15 points)
        if creante > datorii:
            score += 15
            reasons.append("Creanțe > Datorii (lichiditate bună)")
        elif creante > datorii * 0.7:
            score += 10

        # 4. Growth 3 years (15 points)
        if rev_2020 > 0:
            growth = ((revenue - rev_2020) / rev_2020) * 100
            if growth > 20:
                score += 15
                reasons.append(f"Creștere >20% (3 ani: {growth:.1f}%)")
            elif growth > 10:
                score += 10
                reasons.append(f"Creștere >10% (3 ani: {growth:.1f}%)")
            elif growth > 0:
                score += 5

        # 5. Positive Capital (10 points)
        if capital and capital > 0:
            score += 10
            reasons.append("Capital pozitiv")

        # 6. Employee Growth (10 points)
        if sal_2020 > 0 and sal_2023 > sal_2020:
            score += 10
            emp_growth = ((sal_2023 - sal_2020) / sal_2020) * 100
            reasons.append(f"Creștere angajați +{emp_growth:.0f}%")
        elif sal_2023 >= sal_2020:
            score += 5

        # 7. Revenue per employee (10 points)
        if sal_2023 > 0:
            rev_per_employee = revenue / sal_2023
            if rev_per_employee > 500000:  # > 500k RON/employee
                score += 10
                reasons.append(f"Productivitate mare ({rev_per_employee/1000:.0f}k RON/ang.)")
            elif rev_per_employee > 200000:
                score += 5

        # Categorize
        if score >= 80:
            category = "EXCELENT"
            risk = "Scăzut"
        elif score >= 60:
            category = "BUN"
            risk = "Scăzut-Mediu"
        elif score >= 40:
            category = "MODERAT"
            risk = "Mediu"
        elif score >= 20:
            category = "SLAB"
            risk = "Ridicat"
        else:
            category = "RISC ÎNALT"
            risk = "Foarte Ridicat"

        companies_scores.append({
            'cif': cif,
            'name': name,
            'score': score,
            'category': category,
            'risk': risk,
            'revenue': revenue,
            'profit': profit,
            'profit_margin': profit_margin,
            'debt_ratio': debt_ratio,
            'employees': sal_2023,
            'reasons': reasons[:5]  # Top 5 reasons
        })

    # Sort by score
    companies_scores.sort(key=lambda x: x['score'], reverse=True)

    # Statistics
    scores = [c['score'] for c in companies_scores]
    avg_score = statistics.mean(scores) if scores else 0
    median_score = statistics.median(scores) if scores else 0

    # Category breakdown
    categories = defaultdict(int)
    for c in companies_scores:
        categories[c['category']] += 1

    cursor.close()
    conn.close()

    return {
        'companies': companies_scores,
        'top_50': companies_scores[:50],
        'bottom_50': companies_scores[-50:],
        'average_score': avg_score,
        'median_score': median_score,
        'categories': dict(categories),
        'total_analyzed': len(companies_scores)
    }

# =============================================================================
# ANALYSIS 3: SEGMENTATION (Segmentare Companii)
# =============================================================================

def segment_companies():
    """
    Segment companies by:
    - Size (Micro, Small, Medium, Large)
    - CAEN code specialization
    - Business model (Cash Cow, Star, Question Mark, Dog)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("ANALYSIS 3: COMPANY SEGMENTATION (Segmentare Companii)")
    print("="*80)

    cursor.execute("""
        SELECT
            cif,
            company_name,
            cifra_de_afaceri_neta_2023,
            profit_net_2023,
            pierdere_net_2023,
            salariati_2023,
            cod_caen,
            cifra_de_afaceri_neta_2020
        FROM companii
        WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
    """)

    companies = []
    for row in cursor.fetchall():
        cif = row[0]
        name = row[1] or f"CIF {cif}"
        revenue = row[2] or 0
        profit = (row[3] or 0) - (row[4] or 0)
        employees = row[5] or 0
        caen = row[6] or ""
        rev_2020 = row[7] or 0

        # SIZE categorization
        if employees < 10 and revenue < 500000:
            size = "MICRO"
        elif employees < 50 and revenue < 5000000:
            size = "MIC"
        elif employees < 250 and revenue < 50000000:
            size = "MEDIU"
        else:
            size = "MARE"

        # CAEN specialization
        caen_main = caen.split(',')[0].strip() if caen else ""
        if '3811' in caen:
            specialization = "Colectare deșeuri nepericuloase"
        elif '3812' in caen:
            specialization = "Colectare deșeuri periculoase"
        elif '3831' in caen:
            specialization = "Demontare epave"
        elif '3832' in caen:
            specialization = "Recuperare materiale"
        elif '4677' in caen:
            specialization = "Comerț deșeuri metalice"
        else:
            specialization = "Altele"

        # BUSINESS MODEL (BCG Matrix)
        profit_margin = safe_division(profit, revenue, 0) * 100
        growth = safe_division((revenue - rev_2020), rev_2020, 0) * 100 if rev_2020 > 0 else 0

        if profit_margin > 5 and growth > 10:
            business_model = "STAR"  # High profit, high growth
        elif profit_margin > 5 and growth < 10:
            business_model = "CASH COW"  # High profit, low growth
        elif profit_margin < 5 and growth > 10:
            business_model = "QUESTION MARK"  # Low profit, high growth
        else:
            business_model = "DOG"  # Low profit, low growth

        companies.append({
            'cif': cif,
            'name': name,
            'revenue': revenue,
            'profit': profit,
            'profit_margin': profit_margin,
            'employees': employees,
            'size': size,
            'specialization': specialization,
            'caen': caen_main,
            'business_model': business_model,
            'growth': growth
        })

    # Aggregate statistics
    size_stats = defaultdict(lambda: {'count': 0, 'total_revenue': 0, 'total_employees': 0})
    specialization_stats = defaultdict(lambda: {'count': 0, 'total_revenue': 0})
    model_stats = defaultdict(lambda: {'count': 0, 'avg_profit_margin': []})

    for c in companies:
        # Size stats
        size_stats[c['size']]['count'] += 1
        size_stats[c['size']]['total_revenue'] += c['revenue']
        size_stats[c['size']]['total_employees'] += c['employees']

        # Specialization stats
        specialization_stats[c['specialization']]['count'] += 1
        specialization_stats[c['specialization']]['total_revenue'] += c['revenue']

        # Business model stats
        model_stats[c['business_model']]['count'] += 1
        model_stats[c['business_model']]['avg_profit_margin'].append(c['profit_margin'])

    # Calculate averages
    for size in size_stats:
        count = size_stats[size]['count']
        if count > 0:
            size_stats[size]['avg_revenue'] = size_stats[size]['total_revenue'] / count
            size_stats[size]['avg_employees'] = size_stats[size]['total_employees'] / count

    for spec in specialization_stats:
        count = specialization_stats[spec]['count']
        if count > 0:
            specialization_stats[spec]['avg_revenue'] = specialization_stats[spec]['total_revenue'] / count

    for model in model_stats:
        margins = model_stats[model]['avg_profit_margin']
        if margins:
            model_stats[model]['avg_profit_margin'] = statistics.mean(margins)

    cursor.close()
    conn.close()

    return {
        'companies': companies,
        'size_distribution': dict(size_stats),
        'specialization_distribution': dict(specialization_stats),
        'business_model_distribution': dict(model_stats),
        'stars': [c for c in companies if c['business_model'] == 'STAR'][:20],
        'cash_cows': [c for c in companies if c['business_model'] == 'CASH COW'][:20],
        'total_analyzed': len(companies)
    }

# =============================================================================
# ANALYSIS 4: GEOGRAPHIC ANALYSIS (Analiză Geografică)
# =============================================================================

def analyze_by_geography():
    """
    Analyze companies by Județ (county)
    - Total companies per county
    - Total revenue per county
    - Average company size
    - Competition intensity
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("ANALYSIS 4: GEOGRAPHIC ANALYSIS (Analiză Geografică)")
    print("="*80)

    cursor.execute("""
        SELECT
            judet,
            COUNT(*) as num_companies,
            SUM(cifra_de_afaceri_neta_2023) as total_revenue,
            AVG(cifra_de_afaceri_neta_2023) as avg_revenue,
            SUM(salariati_2023) as total_employees,
            AVG(salariati_2023) as avg_employees,
            SUM(profit_net_2023) as total_profit,
            SUM(pierdere_net_2023) as total_loss
        FROM companii
        WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
          AND judet IS NOT NULL
        GROUP BY judet
        ORDER BY total_revenue DESC NULLS LAST
    """)

    county_stats = []
    for row in cursor.fetchall():
        judet = row[0]
        num_companies = row[1]
        total_revenue = row[2] or 0
        avg_revenue = row[3] or 0
        total_employees = row[4] or 0
        avg_employees = row[5] or 0
        total_profit = (row[6] or 0) - (row[7] or 0)

        county_stats.append({
            'judet': judet,
            'num_companies': num_companies,
            'total_revenue': total_revenue,
            'avg_revenue': avg_revenue,
            'total_employees': int(total_employees),
            'avg_employees': avg_employees,
            'total_profit': total_profit,
            'revenue_per_capita': safe_division(total_revenue, num_companies, 0)
        })

    # Find monopolized counties (1-2 large companies dominate)
    cursor.execute("""
        SELECT
            judet,
            COUNT(*) as num_companies,
            MAX(cifra_de_afaceri_neta_2023) as max_revenue,
            SUM(cifra_de_afaceri_neta_2023) as total_revenue
        FROM companii
        WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
          AND judet IS NOT NULL
        GROUP BY judet
        HAVING COUNT(*) >= 2
    """)

    monopolized = []
    fragmented = []

    for row in cursor.fetchall():
        judet = row[0]
        num_companies = row[1]
        max_revenue = row[2] or 0
        total_revenue = row[3] or 0

        # If top company has >50% market share → monopolized
        market_concentration = safe_division(max_revenue, total_revenue, 0) * 100

        if market_concentration > 50:
            monopolized.append({
                'judet': judet,
                'num_companies': num_companies,
                'concentration': market_concentration
            })
        elif num_companies > 50 and market_concentration < 20:
            fragmented.append({
                'judet': judet,
                'num_companies': num_companies,
                'concentration': market_concentration
            })

    cursor.close()
    conn.close()

    return {
        'county_stats': county_stats,
        'top_counties': county_stats[:20],
        'monopolized_counties': monopolized,
        'fragmented_counties': fragmented,
        'total_counties': len(county_stats)
    }

# =============================================================================
# ANALYSIS 5: TIME SERIES & PREDICTIONS (Serii Temporale & Predicții)
# =============================================================================

def analyze_timeseries_and_predictions():
    """
    Analyze time series data and make simple predictions
    - Revenue trends over 12 years
    - Identify anomalies (sudden jumps)
    - Simple linear forecast for 2025-2026
    - Bankruptcy risk prediction
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print("\n" + "="*80)
    print("ANALYSIS 5: TIME SERIES & PREDICTIONS (Serii Temporale)")
    print("="*80)

    cursor.execute("""
        SELECT
            cif,
            company_name,
            cifra_de_afaceri_neta_2024,
            cifra_de_afaceri_neta_2023,
            cifra_de_afaceri_neta_2022,
            cifra_de_afaceri_neta_2021,
            cifra_de_afaceri_neta_2020,
            profit_net_2024,
            profit_net_2023,
            profit_net_2022,
            pierdere_net_2024,
            pierdere_net_2023,
            pierdere_net_2022,
            datorii_2023,
            capitaluri_total_2023
        FROM companii
        WHERE cifra_de_afaceri_neta_2023 IS NOT NULL
    """)

    predictions = []
    bankruptcy_risks = []
    anomalies = []

    for row in cursor.fetchall():
        cif = row[0]
        name = row[1] or f"CIF {cif}"

        # Revenue time series
        revenues = [
            row[2] or 0,  # 2024
            row[3] or 0,  # 2023
            row[4] or 0,  # 2022
            row[5] or 0,  # 2021
            row[6] or 0   # 2020
        ]

        # Profits
        profits = [
            (row[7] or 0) - (row[10] or 0),  # 2024
            (row[8] or 0) - (row[11] or 0),  # 2023
            (row[9] or 0) - (row[12] or 0)   # 2022
        ]

        # Simple linear prediction for 2025
        # Using last 3 years average growth
        if revenues[1] > 0 and revenues[2] > 0 and revenues[3] > 0:
            growth_22_23 = safe_division(revenues[1] - revenues[2], revenues[2], 0)
            growth_21_22 = safe_division(revenues[2] - revenues[3], revenues[3], 0)
            growth_20_21 = safe_division(revenues[3] - revenues[4], revenues[4], 0)

            avg_growth = statistics.mean([growth_22_23, growth_21_22, growth_20_21])
            predicted_2025 = revenues[1] * (1 + avg_growth)

            predictions.append({
                'cif': cif,
                'name': name,
                'revenue_2023': revenues[1],
                'predicted_2025': max(0, predicted_2025),
                'growth_rate': avg_growth * 100
            })

        # Anomaly detection (sudden jump >100%)
        for i in range(len(revenues) - 1):
            if revenues[i+1] > 0:
                change = safe_division(revenues[i] - revenues[i+1], revenues[i+1], 0) * 100
                if abs(change) > 100:  # >100% change
                    anomalies.append({
                        'cif': cif,
                        'name': name,
                        'year_from': 2023 - i,
                        'year_to': 2024 - i,
                        'change_percent': change,
                        'type': 'spike' if change > 0 else 'drop'
                    })

        # Bankruptcy risk prediction
        # Risk factors:
        # 1. Consecutive losses (3 years)
        # 2. Negative capital
        # 3. High debt (>80% revenue)
        # 4. Declining revenue

        risk_score = 0
        risk_factors = []

        # Check consecutive losses
        if all(p < 0 for p in profits):
            risk_score += 40
            risk_factors.append("Pierderi consecutive 3 ani")

        # Negative capital
        capital = row[14] or 0
        if capital < 0:
            risk_score += 30
            risk_factors.append("Capital negativ")

        # High debt
        datorii = row[13] or 0
        if revenues[1] > 0:
            debt_ratio = safe_division(datorii, revenues[1], 0)
            if debt_ratio > 0.8:
                risk_score += 20
                risk_factors.append(f"Datorii mari ({debt_ratio*100:.0f}%)")

        # Declining revenue
        if len(revenues) >= 3 and revenues[0] < revenues[2] * 0.7:
            risk_score += 10
            risk_factors.append("Scădere venituri -30%")

        if risk_score >= 50:
            bankruptcy_risks.append({
                'cif': cif,
                'name': name,
                'risk_score': risk_score,
                'risk_factors': risk_factors,
                'risk_level': 'ÎNALT' if risk_score >= 70 else 'MEDIU'
            })

    # Sort predictions by growth rate
    predictions.sort(key=lambda x: x['growth_rate'], reverse=True)

    # Sort bankruptcy risks by score
    bankruptcy_risks.sort(key=lambda x: x['risk_score'], reverse=True)

    cursor.close()
    conn.close()

    return {
        'predictions_2025': predictions[:100],  # Top 100 growth predictions
        'bankruptcy_risks': bankruptcy_risks,
        'high_risk_count': len([r for r in bankruptcy_risks if r['risk_score'] >= 70]),
        'anomalies': anomalies[:50],  # Top 50 anomalies
        'total_analyzed': len(predictions)
    }

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("="*80)
    print("ROMANIAN WASTE MANAGEMENT SECTOR - COMPREHENSIVE ANALYTICS")
    print("8,390 Companies | 12 Years Financial Data (2013-2024)")
    print("="*80)

    # Run all analyses
    print("\n🔍 Starting comprehensive analysis...")

    # Analysis 1: Trends
    trends = analyze_trends()
    print(f"\n✅ Analysis 1 Complete: {trends['total_analyzed']} companies analyzed")
    print(f"   - Top growth: {trends['fastest_growth'][0]['name']} (CAGR: {trends['fastest_growth'][0]['cagr']:.1f}%)")
    print(f"   - COVID winner: {trends['covid_winners'][0]['name']} ({trends['covid_winners'][0]['covid_impact']:.1f}%)")

    # Analysis 2: Financial Health
    health = calculate_financial_health_score()
    print(f"\n✅ Analysis 2 Complete: {health['total_analyzed']} companies scored")
    print(f"   - Average score: {health['average_score']:.1f}/100")
    print(f"   - Top company: {health['top_50'][0]['name']} (Score: {health['top_50'][0]['score']}/100)")

    # Analysis 3: Segmentation
    segments = segment_companies()
    print(f"\n✅ Analysis 3 Complete: {segments['total_analyzed']} companies segmented")
    print(f"   - STARs: {len(segments['stars'])} companies")
    print(f"   - Cash Cows: {len(segments['cash_cows'])} companies")

    # Analysis 4: Geographic
    geography = analyze_by_geography()
    print(f"\n✅ Analysis 4 Complete: {geography['total_counties']} județe analyzed")
    if geography['top_counties']:
        print(f"   - Top județ: {geography['top_counties'][0]['judet']} ({geography['top_counties'][0]['num_companies']} companies)")
    print(f"   - Monopolized: {len(geography['monopolized_counties'])} județe")

    # Analysis 5: Time Series & Predictions
    timeseries = analyze_timeseries_and_predictions()
    print(f"\n✅ Analysis 5 Complete: {timeseries['total_analyzed']} companies analyzed")
    print(f"   - Bankruptcy risks: {len(timeseries['bankruptcy_risks'])} companies (HIGH: {timeseries['high_risk_count']})")
    if timeseries['predictions_2025']:
        print(f"   - Top predicted growth: {timeseries['predictions_2025'][0]['name']} ({timeseries['predictions_2025'][0]['growth_rate']:.1f}%)")

    # Save results to JSON
    results = {
        'generated_at': datetime.now().isoformat(),
        'trends': trends,
        'financial_health': health,
        'segmentation': segments,
        'geography': geography,
        'timeseries': timeseries
    }

    output_file = 'analytics_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n✅ Results saved to: {output_file}")
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
