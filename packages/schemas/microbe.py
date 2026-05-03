from __future__ import annotations

from pydantic import BaseModel, Field


class MicrobeTrait(BaseModel):
    """Environmental and regulatory traits attached to an organism."""

    organism: str
    ncbi_taxon_id: int | None = None
    gem_id: str | None = Field(default=None, description="Linked GEMRecord.gem_id")
    ph_min: float | None = None
    ph_max: float | None = None
    temp_min_c: float | None = None
    temp_max_c: float | None = None
    oxygen_requirement: str | None = Field(
        default=None, description="aerobe | anaerobe | facultative | microaerophile"
    )
    gras: bool | None = None
    bsl_level: int | None = None
    notes: str | None = None
