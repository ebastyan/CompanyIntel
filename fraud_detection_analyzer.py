#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fraud Detection Analyzer
=========================
Gyanús pénzügyi minták felismerése a 8,390 cég adataiban.
Csalási/trükk pattern-ek detektálása és risk scoring.
"""

import json
import statistics
from collections import defaultdict

class FraudDetector:
    """Csalás detektálás és risk scoring"""

    def __init__(self):
        self.companies = []
        self.sector_stats = {}
        self.fraud_results = []

        print("=" * 80)
        print("FRAUD DETECTION ANALYZER - INDÍTÁS")
        print("=" * 80)

    def load_data(self):
        """Bilanturi adatok betöltése"""
        print("\n[1/5] Adatok betöltése...")

        with open('bilanturi_integrated.json', 'r', encoding='utf-8') as f:
            self.companies = json.load(f)

        print(f"  ✓ {len(self.companies):,} cég betöltve")

    def calculate_sector_benchmarks(self):
        """Szektor átlagok számítása (benchmark)"""
        print("\n[2/5] Szektor benchmark számítása...")

        # 2024-es adatok gyűjtése
        profit_margins = []
        debt_ratios = []
        efficiencies = []

        for company in self.companies:
            revenue = company.get('cifra_de_afaceri_neta_2024')
            profit = company.get('profit_net_2024')
            debt = company.get('datorii_2024')
            employees = company.get('salariati_2024')

            if revenue and revenue > 0:
                if profit is not None:
                    profit_margins.append(100 * profit / revenue)

                if debt is not None:
                    debt_ratios.append(100 * debt / revenue)

                if employees and employees > 0:
                    efficiencies.append(revenue / employees)

        self.sector_stats = {
            'profit_margin_median': statistics.median(profit_margins) if profit_margins else 0,
            'profit_margin_stdev': statistics.stdev(profit_margins) if len(profit_margins) > 1 else 0,
            'debt_ratio_median': statistics.median(debt_ratios) if debt_ratios else 0,
            'efficiency_median': statistics.median(efficiencies) if efficiencies else 0
        }

        print(f"  ✓ Szektor profit margin átlag: {self.sector_stats['profit_margin_median']:.1f}%")
        print(f"  ✓ Szektor adósság ratio átlag: {self.sector_stats['debt_ratio_median']:.1f}%")
        print(f"  ✓ Szektor hatékonyság átlag: {self.sector_stats['efficiency_median']:,.0f} RON/fő")

    def detect_fraud_patterns(self):
        """8 red flag pattern felismerése minden cégnél"""
        print("\n[3/5] Fraud pattern-ek detektálása...")

        for idx, company in enumerate(self.companies):
            if idx % 1000 == 0:
                print(f"  Progress: {idx}/{len(self.companies)}...")

            cif = company['CIF']
            flags = []
            risk_score = 0
            details = {}

            # 2024-es adatok
            revenue_2024 = company.get('cifra_de_afaceri_neta_2024') or 0
            profit_2024 = company.get('profit_net_2024') or 0
            loss_2024 = company.get('pierdere_net_2024') or 0
            creante_2024 = company.get('creante_2024') or 0
            datorii_2024 = company.get('datorii_2024') or 0
            capitaluri_2024 = company.get('capitaluri_total_2024') or 0
            salariati_2024 = company.get('salariati_2024') or 0

            # 2023-as adatok (összehasonlításhoz)
            revenue_2023 = company.get('cifra_de_afaceri_neta_2023') or 0
            salariati_2023 = company.get('salariati_2023') or 0
            datorii_2023 = company.get('datorii_2023') or 0

            # 1. PHANTOM REVENUE
            if revenue_2024 > 1_000_000:
                profit_margin = (profit_2024 / revenue_2024 * 100) if revenue_2024 > 0 else 0
                creante_ratio = (creante_2024 / revenue_2024 * 100) if revenue_2024 > 0 else 0

                if profit_margin < 5 and creante_ratio < 10:
                    flags.append('phantom_revenue')
                    risk_score += 20
                    details['phantom_revenue'] = f'Profit margin: {profit_margin:.1f}%, Creante: {creante_ratio:.1f}%'

            # 2. ZOMBIE COMPANY
            years_with_loss = 0
            for year in [2024, 2023, 2022]:
                loss = company.get(f'pierdere_net_{year}') or 0
                if loss > 0:
                    years_with_loss += 1

            if salariati_2024 == 0 and revenue_2024 < 50_000 and years_with_loss >= 2:
                flags.append('zombie_company')
                risk_score += 15
                details['zombie_company'] = f'{years_with_loss} év veszteség, 0 alkalmazott'

            # 3. DEBT BOMB
            if datorii_2023 > 0 and datorii_2024 > 0:
                debt_growth = ((datorii_2024 - datorii_2023) / datorii_2023) * 100

                if debt_growth > 50:
                    flags.append('debt_bomb')
                    risk_score += 25
                    details['debt_bomb'] = f'Adósság növekedés: {debt_growth:.1f}%'

            # 4. REVENUE SPIKE
            if revenue_2023 > 0 and revenue_2024 > 0:
                revenue_growth = revenue_2024 / revenue_2023
                employee_change = abs(salariati_2024 - salariati_2023) / max(salariati_2023, 1) if salariati_2023 > 0 else 0

                if revenue_growth > 3 and employee_change < 0.2:
                    flags.append('revenue_spike')
                    risk_score += 15
                    details['revenue_spike'] = f'Árbevétel {revenue_growth:.1f}x, létszám +{employee_change*100:.0f}%'

            # 5. NEGATIVE EQUITY
            negative_equity_years = 0
            for year in [2024, 2023]:
                cap = company.get(f'capitaluri_total_{year}') or 0
                if cap < 0:
                    negative_equity_years += 1

            if negative_equity_years >= 2:
                flags.append('negative_equity')
                risk_score += 20
                details['negative_equity'] = f'{negative_equity_years} év negatív tőke'

            # 6. CASH FLOW MISMATCH
            if profit_2024 > 0 and datorii_2024 > 0:
                if creante_2024 > 2 * datorii_2024:
                    flags.append('cash_flow_mismatch')
                    risk_score += 10
                    details['cash_flow_mismatch'] = f'Creante/Datorii: {creante_2024/datorii_2024:.1f}x'

            # 7. EFFICIENCY DROP
            if salariati_2023 > 0 and salariati_2024 > 0:
                eff_2023 = revenue_2023 / salariati_2023
                eff_2024 = revenue_2024 / salariati_2024

                if eff_2023 > 0:
                    eff_drop = ((eff_2023 - eff_2024) / eff_2023) * 100

                    if eff_drop > 40:
                        flags.append('efficiency_drop')
                        risk_score += 10
                        details['efficiency_drop'] = f'Hatékonyság csökkenés: {eff_drop:.1f}%'

            # 8. PROFIT MARGIN ANOMALY
            if revenue_2024 > 0:
                profit_margin = (profit_2024 / revenue_2024) * 100

                if profit_margin > 50 or profit_margin < -20:
                    flags.append('profit_margin_anomaly')
                    risk_score += 15
                    details['profit_margin_anomaly'] = f'Profit margin: {profit_margin:.1f}%'

            # Health status
            if risk_score >= 75:
                health_status = 'critical'
            elif risk_score >= 40:
                health_status = 'warning'
            else:
                health_status = 'healthy'

            # Eredmény tárolása
            self.fraud_results.append({
                'cif': cif,
                'risk_score': risk_score,
                'fraud_flags': flags,
                'health_status': health_status,
                'details': details,
                'metrics': {
                    'revenue_2024': revenue_2024,
                    'profit_2024': profit_2024,
                    'profit_margin': (profit_2024 / revenue_2024 * 100) if revenue_2024 > 0 else 0,
                    'debt_ratio': (datorii_2024 / revenue_2024 * 100) if revenue_2024 > 0 else 0,
                    'employees': salariati_2024,
                    'efficiency': (revenue_2024 / salariati_2024) if salariati_2024 > 0 else 0
                }
            })

        print(f"  ✓ {len(self.fraud_results):,} cég elemezve")

    def generate_statistics(self):
        """Statisztikák generálása"""
        print("\n[4/5] Statisztikák generálása...")

        # Health status összesítés
        health_counts = defaultdict(int)
        for result in self.fraud_results:
            health_counts[result['health_status']] += 1

        # Flag összesítés
        flag_counts = defaultdict(int)
        for result in self.fraud_results:
            for flag in result['fraud_flags']:
                flag_counts[flag] += 1

        # Top gyanús cégek
        high_risk = [r for r in self.fraud_results if r['risk_score'] >= 75]
        high_risk.sort(key=lambda x: x['risk_score'], reverse=True)

        print(f"\n  📊 HEALTH STATUS:")
        print(f"     Healthy:  {health_counts['healthy']:,} cég ({100*health_counts['healthy']/len(self.fraud_results):.1f}%)")
        print(f"     Warning:  {health_counts['warning']:,} cég ({100*health_counts['warning']/len(self.fraud_results):.1f}%)")
        print(f"     Critical: {health_counts['critical']:,} cég ({100*health_counts['critical']/len(self.fraud_results):.1f}%)")

        print(f"\n  🚩 TOP FRAUD FLAGS:")
        for flag, count in sorted(flag_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"     {flag}: {count:,} cég")

        print(f"\n  ⚠️  HIGH RISK CÉGEK (75+ score): {len(high_risk):,}")
        if high_risk:
            print(f"\n     TOP 5 leggyanúsabb:")
            for i, company in enumerate(high_risk[:5], 1):
                print(f"     {i}. CIF {company['cif']} - Risk: {company['risk_score']}, Flags: {len(company['fraud_flags'])}")

    def export_results(self):
        """Eredmények exportálása"""
        print("\n[5/5] Export...")

        # Rendezés risk score szerint
        self.fraud_results.sort(key=lambda x: x['risk_score'], reverse=True)

        output = {
            'generated_at': '2024-11-15',
            'total_companies': len(self.fraud_results),
            'sector_benchmarks': self.sector_stats,
            'summary': {
                'healthy': len([r for r in self.fraud_results if r['health_status'] == 'healthy']),
                'warning': len([r for r in self.fraud_results if r['health_status'] == 'warning']),
                'critical': len([r for r in self.fraud_results if r['health_status'] == 'critical'])
            },
            'companies': self.fraud_results
        }

        with open('fraud_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Exportálva: fraud_analysis.json ({len(json.dumps(output))/1024/1024:.2f} MB)")

def main():
    """Főprogram"""
    detector = FraudDetector()

    detector.load_data()
    detector.calculate_sector_benchmarks()
    detector.detect_fraud_patterns()
    detector.generate_statistics()
    detector.export_results()

    print("\n" + "=" * 80)
    print("✓ FRAUD DETECTION ANALYSIS KÉSZ!")
    print("=" * 80)

if __name__ == "__main__":
    main()
