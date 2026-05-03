from __future__ import annotations

from pydantic import BaseModel, Field, NonNegativeFloat


class ByproductComponent(BaseModel):
    """One molecular species inside a byproduct stream."""

    name: str
    concentration_g_per_l: NonNegativeFloat
    molar_mass_g_per_mol: NonNegativeFloat | None = None
    inchi_key: str | None = None


class ByproductProfile(BaseModel):
    """A normalized byproduct stream ready to feed the engine as exchange fluxes."""

    profile_id: str
    common_name: str
    source: str = Field(description="e.g. 'cheddar cheese production'")
    ph: float | None = None
    components: list[ByproductComponent] = Field(default_factory=list)
    notes: str | None = None
