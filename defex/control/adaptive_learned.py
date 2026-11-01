"""Controller G: controller C plus a learned contact prior in the hole localizer (W9).

Identical to C except at one point: after C's analytic update of the hole localizer
for a blocked attempt on the top face, G adds ``w x log N(h; mean, cov)`` from the
learned model's prediction for that contact (:mod:`defex.recovery.learned_prior`), or,
for a v2 model (v0.2c), ``w x g(h)`` from :mod:`defex.recovery.contact_likelihood`,
then C's own probe selection runs on the combined posterior. ``w`` is the integration
weight chosen on the validation seed and stored with the model.

The model is looked up by the fixture dynamics the backend reports: without a model
trained on this fixture (or with weight 0), G behaves exactly like C and says so in
its event log.
"""

from __future__ import annotations

from pathlib import Path

from defex.config import MM, AdaptiveConfig, LearnedPriorConfig
from defex.control.adaptive_fsm import AdaptiveInsertionController
from defex.control.base import ControllerContext
from defex.perception.state_estimator import Observation
from defex.recovery.contact_likelihood import ContactLikelihood
from defex.recovery.failure_detector import ContactDiagnosis
from defex.recovery.learned_prior import ContactPrior, find_model, load_model


class AdaptiveLearnedController(AdaptiveInsertionController):
    name = "adaptive_learned"
    label = "G: Defex adaptive + learned contact prior"

    def __init__(
        self,
        cfg: AdaptiveConfig | None = None,
        prior_cfg: LearnedPriorConfig | None = None,
        model_dir: str | Path | None = None,
        model_path: str | Path | None = None,
    ) -> None:
        super().__init__(cfg)
        self.prior_cfg = prior_cfg or LearnedPriorConfig()
        self.model_dir = model_dir
        self.model_path = model_path
        self.prior: ContactPrior | ContactLikelihood | None = None
        self.prior_weight = 0.0
        self._prior_note = ""

    def reset(self, ctx: ControllerContext) -> None:
        super().reset(ctx)
        pc = self.prior_cfg
        fd = ctx.fixture_dynamics
        if self.model_path is not None:
            model = load_model(self.model_path)
            self.prior = model if model.matches(fd, pc.fixture_match_rel_tol) else None
        else:
            self.prior = find_model(fd, self.model_dir, pc.fixture_match_rel_tol)
        weight = pc.weight
        if self.prior is not None and weight is None:
            weight = self.prior.integration_weight
        self.prior_weight = float(weight or 0.0)
        if self.prior is None:
            self._prior_note = "no model for this fixture: behaving as C"
            self.prior_weight = 0.0
        elif self.prior_weight <= 0.0:
            self._prior_note = f"model {Path(self.prior.path or '').name} at weight 0: behaving as C"
        else:
            self._prior_note = f"model {Path(self.prior.path or '').name}, weight {self.prior_weight:g}"

    def step(self, obs: Observation):
        if self._prior_note:
            self.log(obs.t, "learned_prior", self._prior_note)
            self._prior_note = ""
        return super().step(obs)

    def _contact_prior_update(self, diag: ContactDiagnosis, record: dict | None) -> None:
        if self.prior is None or self.prior_weight <= 0.0 or record is None or diag.kind not in self.prior.applies_to:
            return
        if getattr(self.prior, "version", 1) == 2:
            # v0.2c: mixture / likelihood-type term, evaluated on the localizer's own grid.
            loc = self.localizer
            term = self.prior.localizer_log_term(record, loc.hx, loc.hy, loc.area)
            loc.update_log_term(self.prior_weight * term)
            record["learned_mean_mm"] = self.prior.mixture_mean_mm(record).tolist()
            record["combined_mean_mm"] = (loc.mean() / MM).tolist()
            return
        mean, precision = self.prior.localizer_term(record)
        self.localizer.update_gaussian(mean, precision, self.prior_weight, self.prior_cfg.outlier_weight)
        record["learned_mean_mm"] = (mean / MM).tolist()
        record["learned_precision_mm-2"] = (precision * MM**2).tolist()
        record["combined_mean_mm"] = (self.localizer.mean() / MM).tolist()
