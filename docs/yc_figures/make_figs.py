"""Explainer figures for docs/YC_ANSWERS_EXPLAINED.md, from committed results only."""
import csv, math, sys
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch

REPO = sys.argv[1]
OUT = sys.argv[2]

SURF = "#fcfcfb"; INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#8a8984"; GRID = "#e6e5e0"
BLUE = "#2a78d6"   # Defex VERIFY (C, J)
ORANGE = "#eb6834" # no VERIFY (spiral: I, F)
AQUA = "#1baf7a"
SOCKET = "#d9d7cf"; SOCKET_EDGE = "#8a8984"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
})

def save(fig, name):
    fig.savefig(f"{OUT}/{name}", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)

def rect(cx, cy, w, h, ang_deg):
    a = math.radians(ang_deg); c, s = math.cos(a), math.sin(a)
    pts = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    return [(cx + x*c - y*s, cy + x*s + y*c) for x, y in pts]

# ---------- fig1: yaw and tilt ----------
fig, axs = plt.subplots(1, 2, figsize=(10, 4.4))
ax = axs[0]
ax.add_patch(Rectangle((-6.5, -4.5), 13, 9, fc="white", ec=SOCKET_EDGE, lw=2))
ax.add_patch(Polygon(rect(0, 0, 12, 8, 0), closed=True, fc="none", ec=MUTED, lw=1.5, ls="--"))
ax.add_patch(Polygon(rect(0, 0, 12, 8, 4), closed=True, fc=BLUE, alpha=0.85, ec=BLUE))
ax.annotate("", xy=(5.5, 3.3), xytext=(6.0, -0.4), arrowprops=dict(arrowstyle="->", color=INK, lw=1.5,
            connectionstyle="arc3,rad=0.3"))
ax.text(0, -6.3, "Seen from above.\nYaw = the plug is TWISTED in the hole.", ha="center", va="top", color=INK2)
ax.text(0, 5.4, "socket hole 13 x 9 mm", ha="center", color=INK2, fontsize=10)
ax.set_title("Yaw (twist)")
ax.set_xlim(-9, 9); ax.set_ylim(-9.5, 7); ax.set_aspect("equal"); ax.axis("off")

ax = axs[1]
# side view: socket walls and floor
ax.add_patch(Rectangle((-9, -16), 2.5, 16, fc=SOCKET, ec=SOCKET_EDGE))
ax.add_patch(Rectangle((6.5, -16), 2.5, 16, fc=SOCKET, ec=SOCKET_EDGE))
ax.add_patch(Rectangle((-9, -18), 18, 2, fc=SOCKET, ec=SOCKET_EDGE))
ax.add_patch(Polygon(rect(0, -6, 12, 20, 0), closed=True, fc="none", ec=MUTED, lw=1.5, ls="--"))
ax.add_patch(Polygon(rect(0.6, -5.5, 12, 20, -3), closed=True, fc=BLUE, alpha=0.85, ec=BLUE))
ax.text(0, -20, "Seen from the side.\nTilt = the plug is LEANING.", ha="center", va="top", color=INK2)
ax.set_title("Tilt (lean)")
ax.set_xlim(-11, 11); ax.set_ylim(-24, 6); ax.set_aspect("equal"); ax.axis("off")
fig.suptitle("Our 'seated correctly' rule: at least 14.5 mm deep, centred, twist under 3 deg AND lean under 3 deg",
             fontsize=11, color=INK, y=0.02)
save(fig, "fig1_yaw_tilt.png")

# ---------- fig2: crooked plug still fits ----------
def fits(ang):
    a = math.radians(ang)
    return 6*math.sin(a) + 4*math.cos(a), 6*math.cos(a) + 4*math.sin(a)
yaw_max = math.degrees(math.asin(4.5/math.hypot(6, 4)) - math.atan2(4, 6))
fig, axs = plt.subplots(1, 3, figsize=(12, 4.2))
for ax, ang, col, lab in [(axs[0], 0, AQUA, "0 deg: perfect"),
                          (axs[1], 3, AQUA, "3 deg: the limit of 'good'"),
                          (axs[2], 4.9, ORANGE, "4.9 deg: still slides to the\nbottom, but OUT of spec")]:
    ax.add_patch(Rectangle((-6.5, -4.5), 13, 9, fc="white", ec=SOCKET_EDGE, lw=2))
    ax.add_patch(Polygon(rect(0, 0, 12, 8, ang), closed=True, fc=col, alpha=0.85, ec=col))
    hy, hx = fits(ang)
    ax.set_title(lab, fontsize=12)
    ax.text(0, -5.6, f"gap left at the tightest corner: {max(4.5-hy,0):.2f} mm", ha="center", va="top",
            color=INK2, fontsize=10)
    ax.set_xlim(-7.5, 7.5); ax.set_ylim(-7.5, 6); ax.set_aspect("equal"); ax.axis("off")
fig.suptitle(f"The 12 x 8 mm plug fits in the 13 x 9 mm hole at up to {yaw_max:.2f} deg of twist (top view).\n"
             "Anything between 3 and 4.9 deg reaches full depth, so a depth check says 'done', but it is crooked.",
             fontsize=11, y=0.03, va="top")
save(fig, "fig2_crooked_plug_fits.png")

# ---------- fig3: what VERIFY does ----------
fig, axs = plt.subplots(1, 3, figsize=(15, 5.6))
def socket_side(ax):
    for x0 in (-9, 6.5):
        ax.add_patch(Rectangle((x0, -15), 2.5, 15, fc=SOCKET, ec=SOCKET_EDGE))
    ax.add_patch(Rectangle((-9, -17), 18, 2, fc=SOCKET, ec=SOCKET_EDGE))
ax = axs[0]
socket_side(ax)
ax.add_patch(Rectangle((-6, -15), 12, 17, fc=BLUE, alpha=0.85, ec=BLUE))
for d in (-1, 1):
    ax.add_patch(FancyArrowPatch((d*1.5, -6), (d*5.6, -6), arrowstyle="-|>", mutation_scale=18, color="white", lw=2))
ax.set_title("1. Feel both walls", color=INK)
ax.text(0, -18.5, "Push gently left, then right.\nA plug truly inside hits a wall each way\nwithin the 0.5 mm gap (at least 2 N).\nBoth walls felt = really inside: PASS.",
        ha="center", va="top", fontsize=10, color=INK2)
ax.set_xlim(-11, 11); ax.set_ylim(-27, 6); ax.set_aspect("equal"); ax.axis("off")
ax = axs[1]
socket_side(ax)
ax.add_patch(Polygon(rect(-3.6, 9.4, 12, 17, 8), closed=True, fc=ORANGE, alpha=0.85, ec=ORANGE))
ax.add_patch(FancyArrowPatch((-9.6, 6), (-13.5, 6), arrowstyle="-|>", mutation_scale=18, color=INK, lw=1.5))
ax.text(-11.6, 7.2, "push: no wall", ha="center", fontsize=9, color=INK)
ax.set_title("2. Caught on the edge: FAIL", color=INK)
ax.text(0, -18.5, "The plug is perched on the rim, not inside.\nThe push finds no wall within the allowed\n1.2 mm, so the walls test fails.\nDefex does NOT say done; it retries.",
        ha="center", va="top", fontsize=10, color=INK2)
ax.set_xlim(-15, 11); ax.set_ylim(-27, 20); ax.set_aspect("equal"); ax.axis("off")
ax = axs[2]
ax.add_patch(Rectangle((-6.5, -4.5), 13, 9, fc="white", ec=SOCKET_EDGE, lw=2))
ax.add_patch(Polygon(rect(0, 0, 12, 8, 4.9), closed=True, fc="none", ec=ORANGE, lw=1.5, ls="--"))
ax.add_patch(Polygon(rect(0, 0, 12, 8, -4.9), closed=True, fc="none", ec=ORANGE, lw=1.5, ls="--"))
ax.add_patch(Polygon(rect(0, 0, 12, 8, 0), closed=True, fc=BLUE, alpha=0.85, ec=BLUE))
ax.set_title("3. Straighten the twist (gantry)", color=INK)
ax.text(0, -6.2, "Top view. Twist until the corners touch (left limit),\nthen the other way (right limit),\nthen park in the MIDDLE: twist is now about 0 deg.\nThis is why Defex's 'done' plugs are never crooked.",
        ha="center", va="top", fontsize=10, color=INK2)
ax.set_xlim(-9, 9); ax.set_ylim(-14, 6); ax.set_aspect("equal"); ax.axis("off")
fig.suptitle("What Defex's VERIFY step does after the plug reaches the bottom (simplified; it also squares the lean to the floor)",
             fontsize=12, y=1.0, fontweight="bold")
save(fig, "fig3_verify_walls.png")

# ---------- data ----------
def load(cell):
    with open(f"{REPO}/results/benchmark_v0.2e/{cell}/trials.csv") as f:
        return list(csv.DictReader(f))
T = lambda v: v == "True"

# ---------- fig4: escapes ----------
seeds = ["20261123", "20261124", "20261130"]
esc = {"C  Defex": [0, 0, 0], "J  spiral + Defex VERIFY": [3, 2, 2],
       "I  spiral + pull test": [161, 138, 138], "F  spiral search": [197, 176, 178]}
cols = {"C  Defex": BLUE, "J  spiral + Defex VERIFY": BLUE, "I  spiral + pull test": ORANGE, "F  spiral search": ORANGE}
fig, ax = plt.subplots(figsize=(10, 4.6))
names = list(esc)
w = 0.26
for i, n in enumerate(names):
    for j, s in enumerate(seeds):
        v = esc[n][j]; x = i + (j-1)*w
        ax.bar(x, max(v, 0.6), w*0.9, color=cols[n], alpha=[0.55, 0.75, 1.0][j])
        ax.text(x, v + 3, str(v), ha="center", va="bottom", fontsize=10, color=INK)
ax.set_xticks(range(len(names))); ax.set_xticklabels(names, fontsize=10)
ax.set_ylabel("crooked or short plugs called 'done'\n(out of 7,400 good parts)")
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.set_ylim(0, 225)
ax.set_title("Escapes: bad plugs the robot said were fine. Three bars = three independent test runs (seeds)", loc="left", fontsize=12)
ax.text(1.5, 205, "blue = has Defex's VERIFY step     orange = depth check only", ha="center", color=INK2, fontsize=10)
save(fig, "fig4_escapes.png")

# ---------- fig5: success by condition ----------
rows = load("gantry_standard")
ok = defaultdict(lambda: [0, 0])
for r in rows:
    k = (r["condition"], r["controller"]); ok[k][0] += T(r["success"]); ok[k][1] += 1
conds = []
for r in rows:
    if r["condition"] not in conds: conds.append(r["condition"])
rate = lambda c, ctl: 100*ok[(c, ctl)][0]/ok[(c, ctl)][1]
conds.sort(key=lambda c: rate(c, "adaptive") - rate(c, "spiral_rcc_pull"))
fig, ax = plt.subplots(figsize=(10, 7))
for i, c in enumerate(conds):
    a, b = rate(c, "adaptive"), rate(c, "spiral_rcc_pull")
    ax.plot([b, a], [i, i], color=GRID, lw=3, zorder=1)
    ax.scatter([b], [i], s=70, color=ORANGE, zorder=3, edgecolor=SURF, linewidth=2)
    ax.scatter([a], [i], s=70, color=BLUE, zorder=3, edgecolor=SURF, linewidth=2)
    if abs(a-b) >= 1:
        ax.text((a + b) / 2, i + 0.42, f"Defex {a:.0f}%  vs  spiral {b:.0f}%", ha="center", va="bottom", fontsize=9, color=INK)
ax.set_yticks(range(len(conds))); ax.set_yticklabels(conds, fontsize=9)
ax.set_ylim(-0.7, len(conds) + 0.3); ax.set_xlim(45, 101.5); ax.set_xlabel("seated correctly (% of 100 trials)")
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
ax.scatter([], [], color=BLUE, s=60, label="C  Defex"); ax.scatter([], [], color=ORANGE, s=60, label="I  spiral + pull test")
ax.legend(loc="lower left", frameon=False)
ax.set_title("Where Defex wins: only the bad-camera rows (gantry, standard suite, latest run)", loc="left", fontsize=12)
save(fig, "fig5_success_by_condition.png")

# ---------- fig6: how crooked are the 'done' plugs ----------
fig, axs = plt.subplots(2, 1, figsize=(10, 5.6), sharex=True)
bins = [x*0.25 for x in range(0, 25)]
for ax, ctl, col, lab in [(axs[0], "spiral_rcc_pull", ORANGE, "I  spiral + pull test"), (axs[1], "adaptive", BLUE, "C  Defex")]:
    v = [max(abs(float(r["final_yaw_deg"])), abs(float(r["final_tilt_deg"])))
         for r in rows if r["controller"] == ctl and T(r["declared_success"])]
    over = sum(x > 3 for x in v)
    ax.hist(v, bins=bins, color=col, edgecolor=SURF, linewidth=1.5)
    ax.set_yscale("log"); ax.set_ylim(0.7, 3000)
    ax.axvline(3, color=INK, lw=1.2, ls="--")
    ax.text(3.08, 900, "3 deg limit", fontsize=9, color=INK)
    ax.set_title(f"{lab}: {len(v)} plugs called 'done', {over} of them more than 3 deg off", loc="left", fontsize=11)
    ax.set_ylabel("plugs (log scale)")
axs[1].set_xlabel("how crooked the plug really is when the robot says 'done' (worst of twist and lean, deg)")
fig.suptitle("Same 2,000 sockets for both. Spiral search's mistakes sit just past 3 deg; Defex has none there.",
             fontsize=11, y=1.0)
fig.tight_layout()
save(fig, "fig6_how_crooked_when_done.png")

# ---------- fig7: speed ----------
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
labs = ["C  Defex", "J  spiral +\nDefex VERIFY", "I  spiral +\npull test"]
med = [5.30, 4.78, 2.43]; uph = [601, 643, 1100]; cc = [BLUE, BLUE, ORANGE]
for ax, vals, title, fmt in [(axs[0], med, "Time per good part (median, seconds)", "{:.2f} s"),
                             (axs[1], uph, "Good parts per hour", "{:,}")]:
    ax.bar(range(3), vals, 0.6, color=cc)
    for i, v in enumerate(vals):
        ax.text(i, v*1.02, fmt.format(v), ha="center", va="bottom", fontsize=10)
    ax.set_xticks(range(3)); ax.set_xticklabels(labs, fontsize=10)
    ax.set_title(title, loc="left", fontsize=12, pad=18); ax.set_yticks([]); ax.set_ylim(0, max(vals)*1.15)
    ax.spines["left"].set_visible(False)
fig.suptitle("The price: checking takes time (gantry, standard suite, latest run). VERIFY is 1.89 s of Defex's extra time.",
             fontsize=11, y=-0.02)
save(fig, "fig7_speed.png")
print("ok")
