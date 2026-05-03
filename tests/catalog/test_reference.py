from services.catalog import REFERENCE_BYPRODUCTS, REFERENCE_GEMS, REFERENCE_MICROBES


def test_reference_catalog_is_non_empty():
    assert REFERENCE_GEMS, "expected at least one reference GEM"
    assert REFERENCE_MICROBES, "expected at least one reference microbe"
    assert REFERENCE_BYPRODUCTS, "expected at least one reference byproduct"


def test_microbes_link_to_known_gems():
    gem_ids = {g.gem_id for g in REFERENCE_GEMS}
    for microbe in REFERENCE_MICROBES:
        if microbe.gem_id is not None:
            assert microbe.gem_id in gem_ids, f"{microbe.organism} references unknown GEM"
