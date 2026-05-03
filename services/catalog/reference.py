"""Tiny built-in reference catalog used until Phase 1 lands real importers.

Values are illustrative only. All numerical metabolic claims must be replaced
with citations to BiGG / KEGG / MetaCyc / peer-reviewed sources before any
customer-visible use.
"""

from __future__ import annotations

from datetime import UTC, datetime

from packages.schemas import ByproductComponent, ByproductProfile, GEMRecord, MicrobeTrait

REFERENCE_GEMS: list[GEMRecord] = [
    GEMRecord(
        gem_id="bigg:iML1515",
        organism="Escherichia coli K-12 MG1655",
        source="bigg",
        source_url="http://bigg.ucsd.edu/models/iML1515",
        license="see BiGG terms",
        sbml_path="data/gems/iML1515.xml",
        reaction_count=2712,
        metabolite_count=1877,
        sha256="placeholder-sha256-iML1515",
        imported_at=datetime.now(UTC),
    ),
    GEMRecord(
        gem_id="bigg:iJO1366",
        organism="Escherichia coli K-12 MG1655",
        source="bigg",
        source_url="http://bigg.ucsd.edu/models/iJO1366",
        license="see BiGG terms",
        sbml_path="data/gems/iJO1366.xml",
        reaction_count=2583,
        metabolite_count=1805,
        sha256="placeholder-sha256-iJO1366",
        imported_at=datetime.now(UTC),
    ),
]

REFERENCE_MICROBES: list[MicrobeTrait] = [
    MicrobeTrait(
        organism="Escherichia coli K-12 MG1655",
        ncbi_taxon_id=511145,
        gem_id="bigg:iML1515",
        ph_min=5.5,
        ph_max=8.0,
        temp_min_c=15.0,
        temp_max_c=45.0,
        oxygen_requirement="facultative",
        gras=False,
        bsl_level=1,
    ),
    MicrobeTrait(
        organism="Saccharomyces cerevisiae S288C",
        ncbi_taxon_id=559292,
        gem_id=None,
        ph_min=3.0,
        ph_max=7.5,
        temp_min_c=10.0,
        temp_max_c=37.0,
        oxygen_requirement="facultative",
        gras=True,
        bsl_level=1,
    ),
]

REFERENCE_BYPRODUCTS: list[ByproductProfile] = [
    ByproductProfile(
        profile_id="cheese-whey-cheddar",
        common_name="Cheese whey (cheddar)",
        source="cheddar cheese production",
        ph=6.4,
        components=[
            ByproductComponent(
                name="lactose", concentration_g_per_l=48.0, molar_mass_g_per_mol=342.30
            ),
            ByproductComponent(name="protein", concentration_g_per_l=8.0),
            ByproductComponent(
                name="lactate", concentration_g_per_l=1.4, molar_mass_g_per_mol=90.08
            ),
        ],
        notes="Reference profile only — real composition varies by dairy and process.",
    ),
]
