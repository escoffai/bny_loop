from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class GEMRecord(BaseModel):
    """A genome-scale metabolic model entry in the catalog."""

    gem_id: str = Field(description="Stable in-house ID, e.g. 'bigg:iML1515'.")
    organism: str
    source: str = Field(description="bigg | kegg | metacyc | vmh | inhouse")
    source_url: str | None = None
    license: str | None = None
    sbml_path: str
    reaction_count: int
    metabolite_count: int
    sha256: str
    imported_at: datetime
