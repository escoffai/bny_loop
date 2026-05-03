from packages.schemas import (
    ByproductComponent,
    ByproductProfile,
    FBAResult,
    SimulationRequest,
)


def test_byproduct_round_trip():
    profile = ByproductProfile(
        profile_id="x",
        common_name="x",
        source="x",
        components=[ByproductComponent(name="lactose", concentration_g_per_l=10.0)],
    )
    assert ByproductProfile.model_validate_json(profile.model_dump_json()) == profile


def test_simulation_request_defaults():
    profile = ByproductProfile(profile_id="p", common_name="p", source="s")
    req = SimulationRequest(byproduct=profile)
    assert req.objective == "max_yield"
    assert req.candidate_microbe_ids is None


def test_fba_result_validation():
    result = FBAResult(
        microbe_id="m",
        objective="max_yield",
        objective_value=1.0,
        solver_status="ok",
        solve_time_s=0.01,
    )
    assert result.objective_value == 1.0
