#!/usr/bin/env python3
"""
Extract binary solubility data from SDS-13_filtered.pdf with ALL columns.

Includes:
- Raw experimental data (mass saturated solution, mass oxide)
- Calculated solubility using old atomic masses (1925)
- Calculated solubility using new atomic masses (1977 IUPAC)
- Molality
- Converted mass percent

The PDF uses two different reporting formats:
1. Full experimental data with g(l)/100 g(2) - needs conversion to mass%
2. Direct mass % reporting - use as-is
"""

import csv

def convert_g_per_100g_to_mass_percent(g):
    """Convert g solute / 100g water to mass%"""
    if g == "":
        return ""
    return round((g / (g + 100)) * 100, 2)

# Complete data extracted from PDF
# Format: (Salt, CAS, Temp, mass_satd_sln, mass_oxide, g_per_100g_old, g_per_100g_new, molality,
#          Solid_Phase, Ref, Journal, Year, format_type, Notes)

all_data_raw = [
    # Yttrium nitrate - Crew et al. 1925 - Full experimental data
    # From PDF page 3: t/°C | mass satd sln/g | mass Y2O3/g | g(l)/100 g(2) a | g(l)/100 g(2)b | mol kg^-1
    ("Y(NO3)3", "[10361-93-0]", 0, 1.3078, 0.2596, 93.1, 93.55, 3.403, "Y(NO3)3·6H2O",
     "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "experimental", ""),

    ("Y(NO3)3", "[10361-93-0]", 22.5, 1.2234, 0.2888, 136, 135.2, 4.917, "Y(NO3)3·6H2O",
     "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "experimental", ""),

    ("Y(NO3)3", "[10361-93-0]", 22.5, 1.2721, 0.2988, 133, 133.6, 4.860, "Y(NO3)3·6H2O",
     "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "experimental", "Duplicate measurement"),

    ("Y(NO3)3", "[10361-93-0]", 35, 0.7403, 0.1853, 155, 156.1, 5.677, "Y(NO3)3·6H2O",
     "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "experimental", ""),

    ("Y(NO3)3", "[10361-93-0]", 60.2, 0.5738, 0.1561, 197, 196.2, 7.138, "Y(NO3)3·6H2O",
     "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "experimental", ""),

    ("Y(NO3)3", "[10361-93-0]", 60.2, 0.7974, 0.2193, 203.1, 202.7, 7.374, "Y(NO3)3·6H2O",
     "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "experimental", "Duplicate measurement"),

    ("Y(NO3)3", "[10361-93-0]", 66.5, 0.9248, 0.2585, 211, 213.1, 7.752, "Y(NO3)3·6H2O",
     "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "experimental", ""),

    # Yttrium nitrate - Moret 1963 - Direct mass% (no raw experimental data in PDF)
    ("Y(NO3)3", "[10361-93-0]", 0, "", "", "", 55.51, 4.538, "Y(NO3)3·6H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", ""),
    ("Y(NO3)3", "[10361-93-0]", 10, "", "", "", 57.12, 4.845, "Y(NO3)3·6H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", ""),
    ("Y(NO3)3", "[10361-93-0]", 20, "", "", "", 58.45, 5.117, "Y(NO3)3·6H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", ""),
    ("Y(NO3)3", "[10361-93-0]", 25, "", "", "", 59.92, 5.438, "Y(NO3)3·6H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", ""),
    ("Y(NO3)3", "[10361-93-0]", 30, "", "", "", 61.23, 5.745, "Y(NO3)3·6H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", ""),
    ("Y(NO3)3", "[10361-93-0]", 35, "", "", "", 62.49, 6.060, "Y(NO3)3·6H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", ""),
    ("Y(NO3)3", "[10361-93-0]", 40, "", "", "", 63.76, 6.400, "Y(NO3)3·5H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", "Transition at 38.5°C"),
    ("Y(NO3)3", "[10361-93-0]", 50, "", "", "", 64.51, 6.612, "Y(NO3)3·5H2O",
     "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent", ""),

    # Lanthanum nitrate - Friend 1935 - Direct mass%
    ("La(NO3)3", "[10099-59-9]", 0, "", "", "", 50.03, 3.081, "α-La(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 18.4, "", "", "", 54.16, 3.636, "α-La(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 21.2, "", "", "", 55.03, 3.766, "α-La(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 25.4, "", "", "", 55.80, 3.885, "α-La(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 35.4, "", "", "", 59.12, 4.451, "α-La(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 42.4, "", "", "", 63.84, 5.434, "α-La(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", "Transition ~43°C"),

    # Lanthanum nitrate - Brunisholz et al. 1964
    ("La(NO3)3", "[10099-59-9]", 0, "", "", "", 54.99, 3.760, "La(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 5, "", "", "", 55.88, 3.898, "La(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 10, "", "", "", 57.09, 4.095, "La(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 20, "", "", "", 58.97, 4.423, "La(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 25, "", "", "", 59.98, 4.613, "La(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 35, "", "", "", 62.34, 5.095, "La(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("La(NO3)3", "[10099-59-9]", 50, "", "", "", 66.29, 6.052, "La(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),

    # Lanthanum nitrate - Spedding et al. 1975
    ("La(NO3)3", "[10099-59-9]", 25, "", "", "", "", 4.610, "La(NO3)3·6H2O",
     "Spedding, F.R.; Shiers, L.E.; Rard, J.A.", "J. Chem. Eng. Data", "1975", "mass_percent", "Preferred value: 4.610 mol/kg"),

    # Cerium nitrate - Quill and Robey 1937
    ("Ce(NO3)3", "[10108-73-3]", 25, "", "", "", 63.71, 5.383, "Ce(NO3)3·6H2O",
     "Quill, L.L.; Robey, R.F.", "J. Am. Chem. Soc.", "1937", "mass_percent", "density=1.88 kg/m³"),
    ("Ce(NO3)3", "[10108-73-3]", 50, "", "", "", 73.88, 8.673, "Ce(NO3)3·6H2O",
     "Quill, L.L.; Robey, R.F.", "J. Am. Chem. Soc.", "1937", "mass_percent", "density=2.04 kg/m³"),

    # Cerium nitrate - Brunisholz et al. 1964
    ("Ce(NO3)3", "[10108-73-3]", 0, "", "", "", 58.02, 4.238, "Ce(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("Ce(NO3)3", "[10108-73-3]", 10, "", "", "", 59.83, 4.567, "Ce(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("Ce(NO3)3", "[10108-73-3]", 20, "", "", "", 62.02, 5.007, "Ce(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("Ce(NO3)3", "[10108-73-3]", 35, "", "", "", 65.62, 5.852, "Ce(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("Ce(NO3)3", "[10108-73-3]", 50, "", "", "", 70.51, 7.331, "Ce(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),

    # Praseodymium nitrate - Friend 1935
    ("Pr(NO3)3", "[10361-80-5]", 15.8, "", "", "", 59.32, 4.460, "Pr(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("Pr(NO3)3", "[10361-80-5]", 22.0, "", "", "", 60.18, 4.623, "Pr(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("Pr(NO3)3", "[10361-80-5]", 30.4, "", "", "", 61.94, 4.978, "Pr(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("Pr(NO3)3", "[10361-80-5]", 43.0, "", "", "", 65.00, 5.681, "Pr(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", ""),
    ("Pr(NO3)3", "[10361-80-5]", 56.0, "", "", "", 75.15, 9.250, "Pr(NO3)3·6H2O",
     "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent", "Melting point"),

    # Praseodymium nitrate - Brunisholz et al. 1964
    ("Pr(NO3)3", "[10361-80-5]", 0, "", "", "", 57.46, 4.132, "Pr(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("Pr(NO3)3", "[10361-80-5]", 10, "", "", "", 59.29, 4.455, "Pr(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("Pr(NO3)3", "[10361-80-5]", 20, "", "", "", 61.24, 4.833, "Pr(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
    ("Pr(NO3)3", "[10361-80-5]", 35, "", "", "", 64.86, 5.646, "Pr(NO3)3·6H2O",
     "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent", ""),
]

def main():
    output_csv = "SDS-13_solubility_data.csv"

    all_data = []

    for entry in all_data_raw:
        (salt, cas, temp, mass_satd, mass_oxide, g_per_100g_old, g_per_100g_new,
         molal, solid, ref, journal, year, format_type, notes) = entry

        # Determine mass percent
        if format_type == "experimental":
            # Has g/100g water data - convert to mass%
            mass_percent = convert_g_per_100g_to_mass_percent(g_per_100g_new)
            print(f"{salt} {temp}°C: {g_per_100g_new} g/100g H2O → {mass_percent}% mass")
        elif format_type == "mass_percent":
            # Already in mass%
            if g_per_100g_new == "":
                mass_percent = ""
            else:
                mass_percent = g_per_100g_new
        else:
            mass_percent = ""

        row = {
            'Salt': salt,
            'CAS_Number': cas,
            'Temperature_C': temp,
            'Mass_Saturated_Solution_g': mass_satd,
            'Mass_Oxide_g': mass_oxide,
            'Solubility_g_per_100g_H2O_old_masses': g_per_100g_old,
            'Solubility_g_per_100g_H2O_new_masses': g_per_100g_new,
            'Solubility_mass_percent': mass_percent,
            'Solubility_mol_per_kg': molal if molal else '',
            'Solid_Phase': solid,
            'Reference': ref,
            'Journal': journal,
            'Year': year,
            'Additional_Conditions': notes
        }
        all_data.append(row)

    # Write to CSV
    fieldnames = ['Salt', 'CAS_Number', 'Temperature_C',
                 'Mass_Saturated_Solution_g', 'Mass_Oxide_g',
                 'Solubility_g_per_100g_H2O_old_masses', 'Solubility_g_per_100g_H2O_new_masses',
                 'Solubility_mass_percent', 'Solubility_mol_per_kg',
                 'Solid_Phase', 'Reference', 'Journal', 'Year', 'Additional_Conditions']

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"\n✓ Extracted {len(all_data)} data points to {output_csv}")

    # Verify no mass% > 100
    invalid = [d for d in all_data if d['Solubility_mass_percent'] != '' and
               float(d['Solubility_mass_percent']) > 100]
    if invalid:
        print(f"\n⚠ WARNING: Found {len(invalid)} entries with mass% > 100!")
        for inv in invalid[:5]:
            print(f"  {inv['Salt']} at {inv['Temperature_C']}°C: {inv['Solubility_mass_percent']}%")
    else:
        print(f"✓ All mass% values are valid (≤100%)")

    print(f"\n✓ Example Y(NO3)3 at 35°C with all columns:")
    y_35 = [d for d in all_data if d['Salt'] == 'Y(NO3)3' and d['Temperature_C'] == 35]
    for entry in y_35:
        print(f"\n  Reference: {entry['Reference']}")
        print(f"  Raw data: mass_satd={entry['Mass_Saturated_Solution_g']}g, mass_oxide={entry['Mass_Oxide_g']}g")
        print(f"  g/100g H2O (old masses): {entry['Solubility_g_per_100g_H2O_old_masses']}")
        print(f"  g/100g H2O (new masses): {entry['Solubility_g_per_100g_H2O_new_masses']}")
        print(f"  mass%: {entry['Solubility_mass_percent']}%")
        print(f"  molality: {entry['Solubility_mol_per_kg']} mol/kg")

if __name__ == "__main__":
    main()
