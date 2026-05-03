"""Catalog service — GEM library, microbe traits, byproduct ontology.

Phase 0 stub: in-memory reference catalog so the API can serve responses
during scaffolding. Phase 1 replaces this with a Postgres-backed catalog and
real BiGG/KEGG/MetaCyc importers.
"""

from .reference import REFERENCE_BYPRODUCTS, REFERENCE_GEMS, REFERENCE_MICROBES

__all__ = ["REFERENCE_BYPRODUCTS", "REFERENCE_GEMS", "REFERENCE_MICROBES"]
