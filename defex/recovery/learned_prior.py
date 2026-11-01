"""Learned contact prior for the hole localizer (W9, controller G).

C localizes the hole after a blocked attempt with an explicit Bayesian filter whose
likelihood comes from an analytic centre-of-pressure model
(:mod:`defex.recovery.search_policy`). This module holds a small learned model of
what one blocked contact says about the true mouth offset, trained offline on C's
own contact records (``AdaptiveInsertionController.contact_records``) with labels
from simulation (``experiments/collect_contacts.py``, ``experiments/train_contact_prior.py``).

Model: a multilayer perceptron (tanh) mapping the contact features to a
heteroscedastic Gaussian over the plug-to-mouth offset ``o = probe - h``:
mean (x, y, yaw), a full 2 x 2 covariance in x/y (Cholesky factor of the precision,
so the NLL and its gradients stay simple and the covariance is always positive
definite) and a yaw sigma. The mouth offset relative to the vision estimate is then
``h = probe - o`` with the same covariance. Inputs are standardized with training-set
statistics stored in the model file.

Only numpy and JSON: no simulator, no ground truth. A model file states the fixture
dynamics it was trained on, every field of FixtureDynamics; :func:`find_model` returns a
model only for a fixture that matches on all of them, so G falls back to C on any machine
without its own model.
"""

from __future__ import annotations

import json
from dataclasses import fields
from functools import lru_cache
from pathlib import Path

import numpy as np

from defex.config import DEG, MM, REPO_ROOT

FORMAT = "defex-contact-prior-v1"
DEFAULT_MODEL_DIR = REPO_ROOT / "assets" / "models"
D_MAX = 6.0  # bound on each log-precision output in standardized units (|log sigma| <= 6), for stable training
_ABS_TOL_FLOOR = 1e-3  # absolute floor of the fixture match tolerance, for values stored as zero (latency)
TRIGGERS = ("stall", "excess_force", "excess_torque", "excess_lateral_force", "insert_timeout", "bottomed")
TARGET_NAMES = ("o_x_mm", "o_y_mm", "o_yaw_deg")  # plug minus mouth, estimated socket frame
N_OUT = 7  # mean (3), log-precision diagonal x/y (2), precision off-diagonal x/y (1), yaw log-precision (1)

# Translation-invariant contact features: what the wrench, compliance and encoders say about
# the contact itself. The physics of a blocked contact depends on the plug-to-mouth offset,
# not on where the probe sits in the camera's frame.
CONTACT_FEATURES = (
    "cop_valid", "cop_x_mm", "cop_y_mm", "cop_x_rel", "cop_y_rel", "cop_clean",
    "axial_force_n", "lateral_force_x_n", "lateral_force_y_n", "torque_x_nm", "torque_y_nm", "torque_z_nm",
    "depth_mm", "touch_calibrated", "depth_offset_mm",
    "conform_ran", "conform_saturated", "conform_rot_x_deg", "conform_rot_y_deg",
    "lateral_compliance_x_mm", "lateral_compliance_y_mm",
    "rot_compliance_x_deg", "rot_compliance_y_deg", "rot_compliance_z_deg",
    "orientation_correction_x_deg", "orientation_correction_y_deg",
    "plug_half_x_mm", "plug_half_y_mm", "clearance_x_mm", "clearance_y_mm", "chamfer_mm", "latching",
    *(f"trigger_{t}" for t in TRIGGERS),
)
# Context features: where the probe was, which attempt, how good the camera is said to be.
# They carry the vision prior and the search policy's beliefs, which the localizer already has.
CONTEXT_FEATURES = (
    "probe_x_mm", "probe_y_mm", "probe_yaw_deg", "commanded_x_mm", "commanded_y_mm",
    "orientation_correction_z_deg", "attempt",
    "vision_xy_sigma_mm", "vision_z_sigma_mm", "vision_yaw_sigma_deg", "vision_bias_mm",
)
FEATURE_SETS = {"contact": CONTACT_FEATURES, "all": CONTACT_FEATURES + CONTEXT_FEATURES}


def raw_features(rec: dict) -> dict[str, float]:
    """Every candidate input, by name, from one contact record (observation-derived only)."""
    cop = rec.get("cop_mm")
    ph = rec["plug_half_mm"]
    ch = rec["cavity_half_mm"]
    lf = rec["lateral_force_n"]
    tq = rec["torque_nm"]
    conf = rec["conform_rot_deg"]
    lc = rec["lateral_compliance_mm"]
    rc = rec["rot_compliance_deg"]
    oc = rec["orientation_correction_deg"]
    f = {
        "cop_valid": float(cop is not None),
        "cop_x_mm": cop[0] if cop is not None else 0.0,
        "cop_y_mm": cop[1] if cop is not None else 0.0,
        "cop_x_rel": cop[0] / ph[0] if cop is not None else 0.0,
        "cop_y_rel": cop[1] / ph[1] if cop is not None else 0.0,
        "cop_clean": float(rec.get("cop_clean", False)),
        "axial_force_n": rec["axial_force_n"],
        "lateral_force_x_n": lf[0], "lateral_force_y_n": lf[1],
        "torque_x_nm": tq[0], "torque_y_nm": tq[1], "torque_z_nm": tq[2],
        "depth_mm": rec["depth_mm"],
        "touch_calibrated": float(rec["touch_calibrated"]),
        "depth_offset_mm": rec["depth_offset_mm"],
        "conform_ran": float(rec["conform_ran"]),
        "conform_saturated": float(rec["conform_saturated"]),
        "conform_rot_x_deg": conf[0], "conform_rot_y_deg": conf[1],
        "lateral_compliance_x_mm": lc[0], "lateral_compliance_y_mm": lc[1],
        "rot_compliance_x_deg": rc[0], "rot_compliance_y_deg": rc[1], "rot_compliance_z_deg": rc[2],
        "orientation_correction_x_deg": oc[0], "orientation_correction_y_deg": oc[1],
        "orientation_correction_z_deg": oc[2],
        "plug_half_x_mm": ph[0], "plug_half_y_mm": ph[1],
        "clearance_x_mm": ch[0] - ph[0], "clearance_y_mm": ch[1] - ph[1],
        "chamfer_mm": rec["chamfer_mm"],
        "latching": float(rec["latching"]),
        "probe_x_mm": rec["probe_xy_mm"][0], "probe_y_mm": rec["probe_xy_mm"][1],
        "probe_yaw_deg": rec["probe_yaw_deg"],
        "commanded_x_mm": rec["commanded_xy_mm"][0], "commanded_y_mm": rec["commanded_xy_mm"][1],
        "attempt": float(rec["attempt"]),
        "vision_xy_sigma_mm": rec["vision_xy_sigma_mm"], "vision_z_sigma_mm": rec["vision_z_sigma_mm"],
        "vision_yaw_sigma_deg": rec["vision_yaw_sigma_deg"], "vision_bias_mm": rec["vision_bias_mm"],
    }
    for t in TRIGGERS:
        f[f"trigger_{t}"] = float(rec["trigger"] == t)
    return f


def feature_matrix(records: list[dict], names: tuple[str, ...] | list[str]) -> np.ndarray:
    rows = [raw_features(r) for r in records]
    return np.array([[row[n] for n in names] for row in rows], dtype=float).reshape(len(rows), len(names))


def probe_pose(records: list[dict]) -> np.ndarray:
    """(N, 3) probe x, y (mm) and yaw (deg) relative to the vision estimate."""
    return np.array([[*r["probe_xy_mm"], r["probe_yaw_deg"]] for r in records], dtype=float).reshape(-1, 3)


# ------------------------------------------------------------------ network
def mlp_forward(layers: list[tuple[np.ndarray, np.ndarray]], x: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    """tanh hidden layers, linear output. Returns the output and every layer's activation."""
    acts = [x]
    h = x
    for k, (W, b) in enumerate(layers):
        h = h @ W + b
        if k < len(layers) - 1:
            h = np.tanh(h)
        acts.append(h)
    return h, acts


def gaussian_head(raw: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Raw outputs -> mean (N, 3), log-precision diagonal (N, 3) (x, y, yaw), off-diagonal u (N,)."""
    mu = raw[:, :3]
    d = D_MAX * np.tanh(raw[:, [3, 4, 6]] / D_MAX)
    return mu, d, raw[:, 5], raw[:, [3, 4, 6]]


def gaussian_nll(raw: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Per-sample negative log-likelihood (nats) of standardized targets ``t`` (N, 3)."""
    mu, d, u, _ = gaussian_head(raw)
    r = t - mu
    e = np.exp(d)
    z1 = e[:, 0] * r[:, 0] + u * r[:, 1]
    z2 = e[:, 1] * r[:, 1]
    z3 = e[:, 2] * r[:, 2]
    return 0.5 * (z1**2 + z2**2 + z3**2) - d.sum(axis=1) + 1.5 * np.log(2.0 * np.pi)


class ContactPrior:
    """A trained model file (see ``experiments/train_contact_prior.py`` for its fields)."""

    def __init__(self, data: dict, path: str | None = None) -> None:
        if data.get("format") != FORMAT:
            raise ValueError(f"not a {FORMAT} file: {path}")
        self.data = data
        self.path = path
        self.feature_names = tuple(data["feature_names"])
        self.x_mean = np.asarray(data["x_mean"], dtype=float)
        self.x_std = np.asarray(data["x_std"], dtype=float)
        self.y_mean = np.asarray(data["y_mean"], dtype=float)
        self.y_std = np.asarray(data["y_std"], dtype=float)
        self.layers = [(np.asarray(L["W"], dtype=float), np.asarray(L["b"], dtype=float)) for L in data["layers"]]
        self.applies_to = tuple(data.get("applies_to_kinds", ("surface_block",)))
        self.integration_weight = data.get("integration_weight")
        self.backend = data.get("backend", "")
        self.fixture_dynamics = data.get("fixture_dynamics") or {}

    @classmethod
    def from_json(cls, path: str | Path) -> "ContactPrior":
        return cls(json.loads(Path(path).read_text()), str(path))

    def matches(self, fixture_dynamics, rel_tol: float) -> bool:
        """True when the model states every field of the running fixture's dynamics, and no other,
        and each value agrees within ``rel_tol``. A value stored as None (not characterized) matches
        only None on the running fixture, and the other way round."""
        if fixture_dynamics is None or not self.fixture_dynamics:
            return False
        names = [f.name for f in fields(fixture_dynamics)]
        if set(names) != set(self.fixture_dynamics):
            return False
        for k in names:
            v, have = self.fixture_dynamics[k], getattr(fixture_dynamics, k)
            if v is None or have is None:
                if v is not None or have is not None:
                    return False
                continue
            if abs(float(have) - float(v)) > rel_tol * max(abs(float(v)), abs(float(have)), _ABS_TOL_FLOOR):
                return False
        return True

    def raw(self, records: list[dict]) -> np.ndarray:
        x = (feature_matrix(records, self.feature_names) - self.x_mean) / self.x_std
        return mlp_forward(self.layers, x)[0]

    def predict(self, records: list[dict]) -> dict[str, np.ndarray]:
        """Gaussian over the mouth offset h for each record.

        mean: (N, 3) x, y in mm and yaw in deg relative to the vision estimate;
        precision_xy / cov_xy: (N, 2, 2) in mm^-2 / mm^2; sigma_yaw_deg: (N,).
        """
        mu, d, u, _ = gaussian_head(self.raw(records))
        e = np.exp(d)
        n = mu.shape[0]
        U = np.zeros((n, 2, 2))
        U[:, 0, 0] = e[:, 0] / self.y_std[0]
        U[:, 0, 1] = u / self.y_std[1]
        U[:, 1, 1] = e[:, 1] / self.y_std[1]
        prec = np.einsum("nki,nkj->nij", U, U)
        o_mean = mu * self.y_std + self.y_mean
        return {
            "mean": probe_pose(records) - o_mean,
            "precision_xy": prec,
            "cov_xy": np.linalg.inv(prec),
            "sigma_yaw_deg": self.y_std[2] / e[:, 2],
        }

    def localizer_term(self, record: dict) -> tuple[np.ndarray, np.ndarray]:
        """(mean (2,) in m, precision (2, 2) in m^-2) for HoleLocalizer.update_gaussian."""
        p = self.predict([record])
        return p["mean"][0, :2] * MM, p["precision_xy"][0] / MM**2

    def yaw_term(self, record: dict) -> tuple[float, float]:
        """(mean, sigma) of the mouth yaw relative to the vision estimate, in rad (reported, not used by G)."""
        p = self.predict([record])
        return float(p["mean"][0, 2] * DEG), float(p["sigma_yaw_deg"][0] * DEG)


@lru_cache(maxsize=16)
def _load(path: str, mtime_ns: int) -> ContactPrior:
    return ContactPrior.from_json(path)


def load_model(path: str | Path) -> ContactPrior:
    p = Path(path)
    return _load(str(p), p.stat().st_mtime_ns)


def find_model(fixture_dynamics, model_dir: str | Path | None = None, rel_tol: float = 0.01) -> ContactPrior | None:
    """The model in ``model_dir`` trained on this fixture (``contact_prior_*.json``), or None."""
    d = Path(DEFAULT_MODEL_DIR if model_dir is None else model_dir)
    if fixture_dynamics is None or not d.is_dir():
        return None
    for path in sorted(d.glob("contact_prior_*.json")):
        model = load_model(path)
        if model.matches(fixture_dynamics, rel_tol):
            return model
    return None
