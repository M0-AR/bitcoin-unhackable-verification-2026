import sys

import pytest

sys.path.insert(0, "src")

from btc_study.chain_stage import create_chain
from btc_study.consensus_stage import nakamoto_catchup_probability
from btc_study.defense import confirmation_table, estimate_attack_cost, recommended_confirmations, reorg_guard


def test_recommended_confirmations_sane():
    z = recommended_confirmations(0.1, 0.01)
    assert 1 <= z <= 10


def test_recommended_confirmations_increases_with_attacker_share():
    assert recommended_confirmations(0.3, 0.01) >= recommended_confirmations(0.1, 0.01)


def test_reorg_guard_no_alarm_on_normal_extend():
    chain = create_chain(["a", "b"], difficulty=0)
    old_tip = chain[-1].hash
    chain2 = chain + create_chain(["c"], difficulty=0)
    # link manually for the guard test
    chain2[2].previous_hash = old_tip
    import copy

    chain2[2].hash = chain2[2].recompute()
    r = reorg_guard(old_tip, chain2, max_reorg_depth=6)
    assert r["alarm"] is False


def test_attack_cost_scales_with_network():
    small = estimate_attack_cost(1e18, hours=1)
    big = estimate_attack_cost(1e21, hours=1)
    assert big["energy_usd_floor"] > small["energy_usd_floor"]
    assert big["power_gw"] > 0


def test_confirmation_table_shape():
    rows = confirmation_table()
    assert len(rows) == 4 and all("recommended_z" in r for r in rows)


# --- Boundary + failure-path guards (audit fixes) ---

@pytest.mark.parametrize("q", [-0.1, -1.0, 1.5, float("nan")])
def test_nakamoto_rejects_out_of_range_q(q):
    with pytest.raises(ValueError, match="q must be within"):
        nakamoto_catchup_probability(q, 2)


@pytest.mark.parametrize("z", [-1, 1.5, "2"])
def test_nakamoto_rejects_bad_z(z):
    with pytest.raises(ValueError, match="z must be"):
        nakamoto_catchup_probability(0.1, z)


@pytest.mark.parametrize("q,risk", [(-0.1, 0.01), (0.1, 0.0), (0.1, 1.0), (1.5, 0.01)])
def test_recommended_confirmations_rejects_bad_inputs(q, risk):
    with pytest.raises(ValueError):
        recommended_confirmations(q, risk)


def test_recommended_confirmations_unreachable_raises():
    with pytest.raises(ValueError, match="unreachable"):
        recommended_confirmations(0.51, 0.001, z_max=10)


def test_reorg_guard_empty_chain_alarms_without_crash():
    r = reorg_guard("abc", [], max_reorg_depth=6)
    assert r["alarm"] is True and r["tip"] is None


def test_reorg_guard_boundary_depth_is_inclusive():
    chain = create_chain(["a", "b", "c"], difficulty=0)
    r = reorg_guard(chain[0].hash, chain, max_reorg_depth=2)
    assert r["reorg_depth"] == 2 and r["alarm"] is False
    r2 = reorg_guard(chain[0].hash, chain, max_reorg_depth=1)
    assert r2["alarm"] is True


def test_reorg_guard_rejects_bad_depth():
    chain = create_chain(["a"], difficulty=0)
    with pytest.raises(ValueError, match="max_reorg_depth"):
        reorg_guard(chain[0].hash, chain, max_reorg_depth=-1)


@pytest.mark.parametrize("kw", [{"hours": -1}, {"share": 1.5}, {"share": -0.1}, {"network_hashrate_hs": -5}])
def test_attack_cost_rejects_bad_inputs(kw):
    if "network_hashrate_hs" in kw:
        with pytest.raises(ValueError):
            estimate_attack_cost(kw["network_hashrate_hs"])
    else:
        with pytest.raises(ValueError):
            estimate_attack_cost(1e21, **kw)


def test_attack_cost_zero_share_is_zero():
    r = estimate_attack_cost(1e21, share=0.0, hours=1)
    assert r["energy_usd_floor"] == 0.0 and r["power_gw"] == 0.0
