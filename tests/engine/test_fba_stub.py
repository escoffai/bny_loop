from packages.schemas import ByproductComponent, ByproductProfile
from services.engine import evaluate


def _profile() -> ByproductProfile:
    return ByproductProfile(
        profile_id="t",
        common_name="t",
        source="t",
        components=[
            ByproductComponent(name="glucose", concentration_g_per_l=10.0),
            ByproductComponent(name="lactose", concentration_g_per_l=5.0),
        ],
    )


def test_evaluate_is_deterministic():
    a = evaluate("bigg:iML1515", _profile())
    b = evaluate("bigg:iML1515", _profile())
    assert a.objective_value == b.objective_value
    assert a.target_yield_g_per_g == b.target_yield_g_per_g


def test_evaluate_responds_to_concentration():
    base = _profile()
    enriched = ByproductProfile(
        **{
            **base.model_dump(),
            "components": [
                *base.components,
                ByproductComponent(name="extra", concentration_g_per_l=20.0),
            ],
        }
    )
    assert evaluate("m", enriched).objective_value > evaluate("m", base).objective_value


def test_evaluate_solver_status_is_marked_placeholder():
    """Guardrail: stub output must never be confused with a real solver run."""
    result = evaluate("m", _profile())
    assert "placeholder" in result.solver_status
