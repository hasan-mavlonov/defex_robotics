"""Escapes and false rejects per code version on the arm training trials (noise_2mm, mf_noise_1mm).
python results/v0.2c_integration/diagnosis_arm_escapes/escapes.py > results/v0.2c_integration/diagnosis_arm_escapes/escapes.txt"""
import csv

D = "results/v0.2c_integration/diagnosis_arm_escapes"
RUNS = {"Checkpoint 2 C (54f3097 code)": "results/checkpoint2_prep/arm_prior/data/arm/train_main",
        "defect-verdict afa08a4": D + "/defect_verdict_afa08a4", "arm-robustness a5bd452": D + "/arm_robustness_a5bd452",
        "integrated 0ace479": "results/v0.2c_integration/prior/data/arm/train_main"}
for name, path in RUNS.items():
    rows = [r for r in csv.DictReader(open(path + "/trials.csv")) if r["condition"] in ("noise_2mm", "mf_noise_1mm")]
    for cond in ("noise_2mm", "mf_noise_1mm"):
        rs = [r for r in rows if r["condition"] == cond]
        esc = [r for r in rs if r["success"] != "True" and r["protective_stop"] != "True" and r["declared_success"] != "False"]
        fr = [r for r in rs if r["gt_seated"] == "True" and r["declared_success"] == "False"]
        print(f"{name:30s} {cond:13s} n={len(rs)} seated={sum(r['success'] == 'True' for r in rs)} escapes={len(esc)} "
              f"false_rejects={len(fr)} stops={sum(r['protective_stop'] == 'True' for r in rs)} "
              f"escape_tilt_deg={[round(float(r['final_tilt_deg']), 2) for r in esc]}")
