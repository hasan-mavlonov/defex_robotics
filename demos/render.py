"""Offscreen frame rendering with telemetry overlays (for videos and stills).

Uses ``mujoco.Renderer`` (CGL on macOS, EGL/OSMesa on Linux: set
``MUJOCO_GL=egl`` or ``MUJOCO_GL=osmesa`` on a headless Linux machine).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import mujoco
import numpy as np
from PIL import Image, ImageDraw

from defex.config import MM
from defex.tasks.insertion import StepInfo
from demos.common import FSM_FLOW, SERIES_RGB, SceneMarkers, Telemetry, font, font_bold

INK = (240, 239, 236)
INK2 = (195, 194, 183)
MUTED = (137, 135, 129)
PANEL = (13, 13, 13, 190)
GOOD = (12, 163, 12)
CRITICAL = (208, 59, 59)
STOP_LINE = (208, 59, 59)

PROGRAM_STEPS = {"fixed": ("APPROACH", "INSERT", "DWELL", "DONE"), "correction": ("APPROACH", "INSERT", "DWELL", "DONE")}


def friendly(kind: str, detail: str) -> str | None:
    """Plain-language caption for a controller event (None = not worth showing)."""
    if kind == "attempt":
        n = detail.split()[0]
        return f"Insertion attempt {n}"
    if kind == "detect":
        if detail.startswith("surface_block"):
            return "Contact detected: blocked on the socket rim"
        if detail.startswith("seated_candidate"):
            return "Bottomed out at seat depth: verifying"
        if detail.startswith("partial_jam"):
            return "Jam detected inside the socket"
        if "treated as" in detail:
            return None
        return "Contact detected"
    if kind == "conform":
        if "slid" in detail:
            return "Lead-in captured the connector: inserting"
        return "Probing contact: reading where the force acts"
    if kind == "touch_calibration":
        return "Socket height calibrated by touch"
    if kind == "surface_alignment":
        return "Socket tilt measured by touch: orientation corrected"
    if kind == "recover":
        if detail.startswith("localizer"):
            return "Retract and correct: new estimate from contact forces"
        if detail.startswith("jam"):
            return "Retract and re-aim using measured contact torque"
        if detail.startswith("yaw"):
            return "Retract and rotate: searching yaw"
        return "Retract and retry"
    if kind == "seat_conform":
        return "Seated: aligning to the socket floor"
    if kind == "verify":
        return "Verified: socket walls felt on both sides" if "PASS" in detail else "Verification failed: retrying"
    if kind == "yaw_centering":
        return "Yaw centred between the socket walls"
    if kind == "protective_stop":
        return "SAFETY STOP: contact force limit exceeded"
    if kind == "abort":
        return f"Aborted: {detail.replace('_', ' ')}"
    return None


@dataclass
class OverlayState:
    caption: str = ""
    caption_t: float = -1e9
    n_events_seen: int = 0
    outcome: str | None = None  # "success" | "failure"
    outcome_text: str = ""
    extra_lines: list[str] = field(default_factory=list)


class FrameRenderer:
    def __init__(
        self,
        model: mujoco.MjModel,
        width: int = 1280,
        height: int = 720,
        camera: str = "closeup",
        pip_camera: str | None = "side",
        title: str = "",
        subtitle: str = "",
    ) -> None:
        self.w, self.h = width, height
        self.renderer = mujoco.Renderer(model, height, width)
        self.pip_w, self.pip_h = int(width * 0.27), int(height * 0.27)
        self.pip = mujoco.Renderer(model, self.pip_h, self.pip_w) if pip_camera else None
        self.camera = camera
        self.pip_camera = pip_camera
        self.title = title
        self.subtitle = subtitle
        self.opt = mujoco.MjvOption()
        self.f_title = font_bold(26)
        self.f_sub = font(15)
        self.f_chip = font_bold(13)
        self.f_tel = font(16)
        self.f_tel_b = font_bold(16)
        self.f_cap = font_bold(22)
        self.f_small = font(12)
        self.f_banner = font_bold(30)

    def close(self) -> None:
        self.renderer.close()
        if self.pip:
            self.pip.close()

    # ------------------------------------------------------------------ 3D
    def _render_3d(self, data: mujoco.MjData, info: StepInfo | None, markers: SceneMarkers | None) -> np.ndarray:
        self.renderer.update_scene(data, camera=self.camera, scene_option=self.opt)
        if markers is not None:
            markers.draw(self.renderer.scene, info)
        img = self.renderer.render()
        if self.pip:
            self.pip.update_scene(data, camera=self.pip_camera, scene_option=self.opt)
            pip = self.pip.render()
            img = img.copy()
            x0, y0 = self.w - self.pip_w - 24, self.h // 2 - self.pip_h // 2 - 20
            img[y0 : y0 + self.pip_h, x0 : x0 + self.pip_w] = pip
            img[y0 - 2 : y0, x0 - 2 : x0 + self.pip_w + 2] = 90
            img[y0 + self.pip_h : y0 + self.pip_h + 2, x0 - 2 : x0 + self.pip_w + 2] = 90
            img[y0 - 2 : y0 + self.pip_h + 2, x0 - 2 : x0] = 90
            img[y0 - 2 : y0 + self.pip_h + 2, x0 + self.pip_w : x0 + self.pip_w + 2] = 90
            self._pip_box = (x0, y0)
        return img

    # ------------------------------------------------------------------ overlays
    def _panel(self, d: ImageDraw.ImageDraw, box, radius=10) -> None:
        d.rounded_rectangle(box, radius=radius, fill=PANEL)

    def frame(
        self,
        data: mujoco.MjData,
        info: StepInfo | None,
        telemetry: Telemetry | None,
        markers: SceneMarkers | None,
        state: OverlayState,
        controller_name: str = "adaptive",
    ) -> np.ndarray:
        img = Image.fromarray(self._render_3d(data, info, markers)).convert("RGBA")
        over = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(over)
        col = SERIES_RGB.get(controller_name, (217, 89, 38))
        # Title card
        tw = max(d.textlength(self.title, font=self.f_title), d.textlength(self.subtitle, font=self.f_sub)) + 56
        self._panel(d, (20, 20, 20 + tw, 96))
        d.rectangle((34, 34, 40, 66), fill=col + (255,))
        d.text((52, 30), self.title, font=self.f_title, fill=INK)
        d.text((52, 66), self.subtitle, font=self.f_sub, fill=INK2)
        if info is not None:
            self._chips(d, info, col, controller_name)
            self._telemetry(d, info)
            if telemetry is not None:
                self._sparkline(d, telemetry, col)
            self._update_caption(info, state)
        if self.pip:
            x0, y0 = self._pip_box
            d.text((x0 + 8, y0 + 6), "cutaway view", font=self.f_small, fill=INK2)
        # Caption
        t_now = info.t if info is not None else 0.0
        if state.caption and t_now - state.caption_t < 3.5:
            cw = d.textlength(state.caption, font=self.f_cap) + 40
            x0 = (self.w - cw) / 2
            self._panel(d, (x0, self.h - 82, x0 + cw, self.h - 36))
            d.text((x0 + 20, self.h - 75), state.caption, font=self.f_cap, fill=INK)
        if state.outcome:
            self._banner(d, state)
        out = Image.alpha_composite(img, over).convert("RGB")
        return np.asarray(out)

    def _chips(self, d: ImageDraw.ImageDraw, info: StepInfo, col, name: str) -> None:
        steps = FSM_FLOW if name == "adaptive" else PROGRAM_STEPS.get(name, ("RUN",))
        cur = info.controller.state
        x = self.w - 20
        widths = [d.textlength(s, font=self.f_chip) + 22 for s in steps]
        total = sum(widths) + 6 * (len(steps) - 1) + 20
        self._panel(d, (self.w - 20 - total, 20, self.w - 20, 62))
        x = self.w - 20 - total + 10
        for s, w in zip(steps, widths):
            active = s == cur or (cur in ("SUCCESS", "FAILURE") and s == steps[-1] and name != "adaptive")
            if active:
                d.rounded_rectangle((x, 28, x + w, 54), radius=8, fill=col + (255,))
                d.text((x + 11, 33), s, font=self.f_chip, fill=(255, 255, 255))
            else:
                d.rounded_rectangle((x, 28, x + w, 54), radius=8, outline=MUTED + (255,), width=1)
                d.text((x + 11, 33), s, font=self.f_chip, fill=MUTED)
            x += w + 6

    def _telemetry(self, d: ImageDraw.ImageDraw, info: StepInfo) -> None:
        rows = Telemetry.lines(info)
        h = 24 * len(rows) + 64
        y0 = self.h - 110 - h
        self._panel(d, (20, y0, 372, y0 + h))
        y = y0 + 10
        for label, value in rows:
            warn = label == "SAFETY"
            d.text((34, y), label, font=self.f_tel, fill=CRITICAL if warn else INK2)
            d.text((200, y), value, font=self.f_tel_b, fill=CRITICAL if warn else INK)
            y += 24
        d.text((34, y + 2), "* simulation truth; force = wrist F/T sensor", font=self.f_small, fill=MUTED)
        # Marker legend: identity is carried by the swatch, text stays in ink.
        y += 26
        x = 34
        for rgb, label in (((242, 51, 51), "programmed pose"), ((38, 242, 89), "vision estimate"), ((25, 204, 255), "target")):
            d.rectangle((x, y + 4, x + 10, y + 14), fill=rgb + (255,))
            d.text((x + 15, y), label, font=self.f_small, fill=INK2)
            x += 25 + d.textlength(label, font=self.f_small) + 8

    def _sparkline(self, d: ImageDraw.ImageDraw, tel: Telemetry, col) -> None:
        w, h = 330, 120
        x0, y0 = self.w - w - 20, self.h - h - 110
        self._panel(d, (x0, y0, x0 + w, y0 + h))
        d.text((x0 + 12, y0 + 8), "measured contact force (last 4 s)", font=self.f_small, fill=INK2)
        px0, px1, py0, py1 = x0 + 40, x0 + w - 12, y0 + 30, y0 + h - 14
        fmax = 35.0
        for f, lab in ((0, "0"), (30, "30 N")):
            y = py1 - (py1 - py0) * f / fmax
            d.line((px0, y, px1, y), fill=(STOP_LINE if f == 30 else (60, 60, 58)) + (255,), width=1)
            d.text((x0 + 8, y - 7), lab, font=self.f_small, fill=CRITICAL if f == 30 else MUTED)
        if len(tel.force_hist) > 1:
            t_end = tel.force_hist[-1][0]
            pts = [
                (px0 + (px1 - px0) * (1 - (t_end - t) / 4.0), py1 - (py1 - py0) * min(f, fmax) / fmax)
                for t, f in tel.force_hist
                if t_end - t <= 4.0
            ]
            if len(pts) > 1:
                d.line(pts, fill=col + (255,), width=2, joint="curve")

    def _update_caption(self, info: StepInfo, state: OverlayState) -> None:
        ev = info.controller.events
        while state.n_events_seen < len(ev):
            e = ev[state.n_events_seen]
            state.n_events_seen += 1
            text = friendly(e.kind, e.detail)
            if text:
                state.caption, state.caption_t = text, info.t

    def _banner(self, d: ImageDraw.ImageDraw, state: OverlayState) -> None:
        ok = state.outcome == "success"
        colr = GOOD if ok else CRITICAL
        icon = "✓" if ok else "✕"
        text = f"{icon}  {state.outcome_text}"
        widths = [d.textlength(text, font=self.f_banner)] + [d.textlength(x, font=self.f_sub) for x in state.extra_lines]
        tw = max(widths) + 60
        h = 64 + 24 * len(state.extra_lines)
        x0 = (self.w - tw) / 2
        y0 = 112
        d.rounded_rectangle((x0, y0, x0 + tw, y0 + h), radius=14, fill=(13, 13, 13, 225), outline=colr + (255,), width=3)
        d.text(((self.w - widths[0]) / 2, y0 + 12), text, font=self.f_banner, fill=INK)
        for i, line in enumerate(state.extra_lines):
            d.text(((self.w - widths[i + 1]) / 2, y0 + 58 + 24 * i), line, font=self.f_sub, fill=INK2)


def outcome_text(result) -> tuple[str, str, list[str]]:
    if result.success:
        lines = [
            f"depth {result.final_depth_mm:.2f} mm  ·  peak force {result.peak_contact_force_n:.1f} N  ·  "
            f"{result.retries} recoveries  ·  cycle {result.cycle_time_s:.1f} s"
        ]
        return "success", "SEATED AND VERIFIED" if result.declared_success else "SEATED", lines
    reason = result.failure_reason.replace("_", " ")
    if result.failure_reason == "protective_stop":
        head = "FAILED: SAFETY STOP"
    elif result.failure_reason.startswith("aborted"):
        head = "FAILED: ABORTED SAFELY"
    else:
        head = "FAILED: NOT SEATED"
    lines = [f"{reason}  ·  depth {result.final_depth_mm:.2f} mm  ·  peak force {result.peak_contact_force_n:.1f} N"]
    return "failure", head, lines


def to_mm(v: float) -> float:
    return v / MM
