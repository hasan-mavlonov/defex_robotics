from experiments.checkpoint_report import decisions, defect_decision, escape, mcnemar, wilson


def row(ctrl, i, ok, stop=False, declared="True", cond="nominal"):
    return {"controller": ctrl, "condition": cond, "trial_index": str(i), "success": str(ok),
            "protective_stop": str(stop), "declared_success": declared, "gt_seated": str(ok)}


def test_wilson_and_mcnemar():
    lo, hi = wilson(0, 80)
    assert lo == 0.0 and 0.045 < hi < 0.047
    assert mcnemar(0, 0) == 1.0
    assert abs(mcnemar(0, 12) - 2 / 4096) < 1e-12


def test_escape_definition():
    assert escape(row("spiral", 0, False))
    assert not escape(row("spiral", 0, False, stop=True))
    assert not escape(row("spiral", 0, False, declared="False"))
    assert not escape(row("spiral", 0, True))


def test_rules():
    rows = [row("adaptive", i, True) for i in range(40)]
    rows += [row("spiral", i, i >= 12) for i in range(40)]
    rows += [row("adaptive_learned", i, True) for i in range(40)]
    out = decisions("x", rows)
    assert "C ahead of every fair baseline" in out[0]
    assert "no measurable gain from G" in out[1]
    rows = [row("adaptive", i, i >= 12) for i in range(40)] + [row("spiral", i, True) for i in range(40)]
    assert "C below the best fair baseline" in decisions("x", rows)[0]
    bad = [row("adaptive", i, False, declared="False", cond="mf_broken_latch") for i in range(20)]
    bad += [row("spiral", i, False, cond="mf_broken_latch") for i in range(20)]
    assert "C passes fewer bad parts" in defect_decision("x", bad)[0]
