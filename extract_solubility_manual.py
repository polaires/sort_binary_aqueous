#!/usr/bin/env python3
"""
Manually extract binary solubility data from SDS-13_filtered.pdf with correct mass% conversion.

The PDF uses two different solubility formats:
1. "g(l)/100 g(2)" = grams solute per 100g water → needs conversion to mass%
2. "mass %" = already in mass percent → use as-is

Conversion formula: mass% = (g_solute / (g_solute + 100)) × 100
"""

import fitz  # PyMuPDF
import re
import csv

def convert_g_per_100g_to_mass_percent(g):
    """Convert g solute / 100g water to mass%"""
    return round((g / (g + 100)) * 100, 2)

# Manually extracted data from PDF with correct conversions
# Format: (Salt, CAS, Temp, Solubility, Molality, Solid_Phase, Ref, Journal, Year, Notes)

all_data_raw = [
    # Scandium nitrate - Pushkina et al. 1963 - Uses g/100g → needs conversion
    ("Sc(NO3)3", "[13465-60-6]", 0, 56.37, 5.595, "Sc(NO3)3·4H2O", "Pushkina, G. Ya.; Komissarova, L.N.", "Zh. Neorg. Khim.", "1963", "g_per_100g"),
    ("Sc(NO3)3", "[13465-60-6]", 15, 61.30, 6.857, "Sc(NO3)3·4H2O", "Pushkina, G. Ya.; Komissarova, L.N.", "Zh. Neorg. Khim.", "1963", "g_per_100g"),
    ("Sc(NO3)3", "[13465-60-6]", 25, 62.37, 7.176, "Sc(NO3)3·4H2O", "Pushkina, G. Ya.; Komissarova, L.N.", "Zh. Neorg. Khim.", "1963", "g_per_100g"),
    ("Sc(NO3)3", "[13465-60-6]", 30, 64.28, 7.791, "Sc(NO3)3·4H2O", "Pushkina, G. Ya.; Komissarova, L.N.", "Zh. Neorg. Khim.", "1963", "g_per_100g"),
    ("Sc(NO3)3", "[13465-60-6]", 40, 66.99, 8.787, "Sc(NO3)3·4H2O", "Pushkina, G. Ya.; Komissarova, L.N.", "Zh. Neorg. Khim.", "1963", "g_per_100g"),
    ("Sc(NO3)3", "[13465-60-6]", 50, 67.63, 9.045, "Sc(NO3)3·4H2O", "Pushkina, G. Ya.; Komissarova, L.N.", "Zh. Neorg. Khim.", "1963", "g_per_100g"),

    # Yttrium nitrate - Crew et al. 1925 - Uses g/100g → needs conversion (this is the problematic data!)
    ("Y(NO3)3", "[10361-93-0]", 0, 93.55, 3.403, "Y(NO3)3·6H2O", "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "g_per_100g"),
    ("Y(NO3)3", "[10361-93-0]", 22.5, 135.2, 4.917, "Y(NO3)3·6H2O", "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "g_per_100g"),
    ("Y(NO3)3", "[10361-93-0]", 35, 156.1, 5.677, "Y(NO3)3·6H2O", "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "g_per_100g"),
    ("Y(NO3)3", "[10361-93-0]", 60.2, 196.2, 7.138, "Y(NO3)3·6H2O", "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "g_per_100g"),
    ("Y(NO3)3", "[10361-93-0]", 66.5, 213.1, 7.752, "Y(NO3)3·6H2O", "Crew, M.C.; Steinert, H.E.; Hopkins, B.S.", "J. Phys. Chem.", "1925", "g_per_100g"),

    # Yttrium nitrate - Moret 1963 - Already mass% → no conversion
    ("Y(NO3)3", "[10361-93-0]", 0, 55.51, 4.538, "Y(NO3)3·6H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent"),
    ("Y(NO3)3", "[10361-93-0]", 10, 57.12, 4.845, "Y(NO3)3·6H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent"),
    ("Y(NO3)3", "[10361-93-0]", 20, 58.45, 5.117, "Y(NO3)3·6H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent"),
    ("Y(NO3)3", "[10361-93-0]", 25, 59.92, 5.438, "Y(NO3)3·6H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent"),
    ("Y(NO3)3", "[10361-93-0]", 30, 61.23, 5.745, "Y(NO3)3·6H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent"),
    ("Y(NO3)3", "[10361-93-0]", 35, 62.49, 6.060, "Y(NO3)3·6H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent"),
    ("Y(NO3)3", "[10361-93-0]", 40, 63.76, 6.400, "Y(NO3)3·5H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent;Transition at 38.5°C"),
    ("Y(NO3)3", "[10361-93-0]", 50, 64.51, 6.612, "Y(NO3)3·5H2O", "Moret R.", "Thesis Universite de Lausanne", "1963", "mass_percent"),

    # Lanthanum nitrate - Friend 1935
    ("La(NO3)3", "[10099-59-9]", 0, 50.03, 3.081, "α-La(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 18.4, 54.16, 3.636, "α-La(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 21.2, 55.03, 3.766, "α-La(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 25.4, 55.80, 3.885, "α-La(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 35.4, 59.12, 4.451, "α-La(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 42.4, 63.84, 5.434, "α-La(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent;Transition ~43°C"),

    # Lanthanum nitrate - Brunisholz et al. 1964
    ("La(NO3)3", "[10099-59-9]", 0, 54.99, 3.760, "La(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 5, 55.88, 3.898, "La(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 10, 57.09, 4.095, "La(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 20, 58.97, 4.423, "La(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 25, 59.98, 4.613, "La(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 35, 62.34, 5.095, "La(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("La(NO3)3", "[10099-59-9]", 50, 66.29, 6.052, "La(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),

    # Lanthanum nitrate - Spedding et al. 1975
    ("La(NO3)3", "[10099-59-9]", 25, "", 4.610, "La(NO3)3·6H2O", "Spedding, F.R.; Shiers, L.E.; Rard, J.A.", "J. Chem. Eng. Data", "1975", "mass_percent;Preferred value: 4.610 mol/kg"),

    # Cerium nitrate - Quill and Robey 1937
    ("Ce(NO3)3", "[10108-73-3]", 25, 63.71, 5.383, "Ce(NO3)3·6H2O", "Quill, L.L.; Robey, R.F.", "J. Am. Chem. Soc.", "1937", "mass_percent;density=1.88 kg/m³"),
    ("Ce(NO3)3", "[10108-73-3]", 50, 73.88, 8.673, "Ce(NO3)3·6H2O", "Quill, L.L.; Robey, R.F.", "J. Am. Chem. Soc.", "1937", "mass_percent;density=2.04 kg/m³"),

    # Cerium nitrate - Brunisholz et al. 1964
    ("Ce(NO3)3", "[10108-73-3]", 0, 58.02, 4.238, "Ce(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("Ce(NO3)3", "[10108-73-3]", 10, 59.83, 4.567, "Ce(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("Ce(NO3)3", "[10108-73-3]", 20, 62.02, 5.007, "Ce(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("Ce(NO3)3", "[10108-73-3]", 35, 65.62, 5.852, "Ce(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("Ce(NO3)3", "[10108-73-3]", 50, 70.51, 7.331, "Ce(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),

    # Praseodymium nitrate - Friend 1935
    ("Pr(NO3)3", "[10361-80-5]", 15.8, 59.32, 4.460, "Pr(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("Pr(NO3)3", "[10361-80-5]", 22.0, 60.18, 4.623, "Pr(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("Pr(NO3)3", "[10361-80-5]", 30.4, 61.94, 4.978, "Pr(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("Pr(NO3)3", "[10361-80-5]", 43.0, 65.00, 5.681, "Pr(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent"),
    ("Pr(NO3)3", "[10361-80-5]", 56.0, 75.15, 9.250, "Pr(NO3)3·6H2O", "Friend J.N.", "J. Chem. Soc.", "1935", "mass_percent;Melting point"),

    # Praseodymium nitrate - Brunisholz et al. 1964
    ("Pr(NO3)3", "[10361-80-5]", 0, 57.46, 4.132, "Pr(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("Pr(NO3)3", "[10361-80-5]", 10, 59.29, 4.455, "Pr(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("Pr(NO3)3", "[10361-80-5]", 20, 61.24, 4.833, "Pr(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
    ("Pr(NO3)3", "[10361-80-5]", 35, 64.86, 5.646, "Pr(NO3)3·6H2O", "Brunisholz, G.; Quinche, J.P.; Kalo, A.M.", "Helv. Chim. Acta", "1964", "mass_percent"),
]

def main():
    output_csv = "SDS-13_solubility_data_corrected.csv"

    all_data = []

    for entry in all_data_raw:
        salt, cas, temp, solub, molal, solid, ref, journal, year, notes = entry

        # Determine if we need to convert
        needs_conversion = "g_per_100g" in notes

        # Process solubility
        if solub == "":
            mass_percent = ""
        elif needs_conversion:
            # Convert from g/100g water to mass%
            mass_percent_converted = convert_g_per_100g_to_mass_percent(solub)
            print(f"{salt} {temp}°C: {solub} g/100g H2O → {mass_percent_converted}% mass")
            mass_percent = mass_percent_converted
        else:
            # Already in mass%
            mass_percent = solub

        # Extract additional conditions
        additional = ""
        if ";" in notes:
            parts = notes.split(";")
            if len(parts) > 1:
                additional = parts[1]

        row = {
            'Salt': salt,
            'CAS_Number': cas,
            'Temperature_C': temp,
            'Solubility_mass_percent': mass_percent,
            'Solubility_mol_per_kg': molal if molal else '',
            'Solid_Phase': solid,
            'Reference': ref,
            'Journal': journal,
            'Year': year,
            'Additional_Conditions': additional
        }
        all_data.append(row)

    # Write to CSV
    fieldnames = ['Salt', 'CAS_Number', 'Temperature_C', 'Solubility_mass_percent',
                 'Solubility_mol_per_kg', 'Solid_Phase', 'Reference', 'Journal',
                 'Year', 'Additional_Conditions']

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)

    print(f"\n✓ Extracted {len(all_data)} data points to {output_csv}")

    # Verify no mass% > 100
    invalid = [d for d in all_data if d['Solubility_mass_percent'] != '' and float(d['Solubility_mass_percent']) > 100]
    if invalid:
        print(f"\n⚠ WARNING: Found {len(invalid)} entries with mass% > 100!")
        for inv in invalid[:5]:
            print(f"  {inv['Salt']} at {inv['Temperature_C']}°C: {inv['Solubility_mass_percent']}%")
    else:
        print(f"✓ All mass% values are valid (≤100%)")

    # Show example of corrected values
    print(f"\n✓ Example corrected values for Y(NO3)3 at 35°C:")
    y_35 = [d for d in all_data if d['Salt'] == 'Y(NO3)3' and d['Temperature_C'] == 35]
    for entry in y_35:
        print(f"  {entry['Reference']}: {entry['Solubility_mass_percent']}% (mol/kg={entry['Solubility_mol_per_kg']})")

if __name__ == "__main__":
    main()
