"""
build_dataset.py
Genera i file CSV del dataset AMJ per la cartella amj_dataset.
Eseguire dalla cartella che contiene amj_dataset/.
"""

import csv
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "..", "Dati Questionari Impostor Bias")
MATERIALS_DIR = os.path.join(BASE, "materials")
DATA_OUT = os.path.join(BASE, "data")

# ─── Mappings ────────────────────────────────────────────────────────────────

VARIANT_NAME = {"1": "alpha", "2": "beta", "3": "gamma", "4": "delta", "5": "epsilon"}

# Filename suffix → ground_truth label
def suffix_to_gt(filename):
    name = os.path.splitext(filename)[0]
    if name.endswith("_real"):
        return "real"
    elif name.endswith("_mm"):
        return "AI_magnific"
    elif name.endswith("_m"):
        return "AI_midjourney"
    raise ValueError(f"Unknown suffix in: {filename}")

# Initial choice normalisation
def norm_initial(val):
    v = val.strip().lower()
    if v in ("reale", "real"):
        return "real"
    if v in ("generata da ia", "generato da ia", "ai generated"):
        return "AI"
    raise ValueError(f"Unknown initial_choice: {val!r}")

# Final choice normalisation
def norm_final(val):
    v = val.strip().lower()
    if v in ("sì, confermo", "si, confermo", "yes, i confirm"):
        return "confirm"
    if v in ("no, cambio la mia scelta", "no, cambio scelta", "no, i change my choice"):
        return "change"
    raise ValueError(f"Unknown final_choice: {val!r}")

# Department normalisation (broad academic category, PII removed)
DEPT_MAP = {
    "dmi": "DMI",
    "professioni sanitarie": "Professioni Sanitarie",
    "disfor": "DiSFor",
    "dieei": "DIEEI",
    "dieei (ingegneria elettronica)": "DIEEI",
    "deei": "DIEEI",
    "dei": "DIEEI",
    "diiei": "DIEEI",
    "dieii": "DIEEI",
    "scuola di medicina": "Scuola di Medicina",
    "casalinga": "non-academic",
    "docente": "non-academic",
    "work": "non-academic",
    "scienze biologiche": "Scienze Biologiche",
    "scienze politiche e socali": "Scienze Politiche e Sociali",
    "dipartimento di scienze politiche e socali": "Scienze Politiche e Sociali",
    "scienze politiche e sociali": "Scienze Politiche e Sociali",
    "scienze politiche": "Scienze Politiche e Sociali",
    "disum": "DISUM",
    "poznań university of technology": "Poznań University of Technology",
    "poznan university of technology": "Poznań University of Technology",
    "poznan university of technology (put)": "Poznań University of Technology",
    "put": "Poznań University of Technology",
    "economia aziendale": "Economia Aziendale",
    "economia": "Economia",
    "economia e impresa": "Economia e Impresa",
    "digital forensics": "Digital Forensics",
    "corso singolo : digital forensics": "Digital Forensics",
    "scienze motorie": "Scienze Motorie",
    "giurisprudenza": "Giurisprudenza",
    "accademia di belle arti di catania": "Accademia di Belle Arti",
    "accademia": "Accademia di Belle Arti",
    "3 dipartimenti": "multi-department",
    "tridipartimentale": "multi-department",
    "dmi, ingegneria, economia": "multi-department",
    "economia, matematica, ingegneria": "multi-department",
    "ingegneria informatica": "Ingegneria",
    "ingegneria": "Ingegneria",
    "architettura": "Architettura",
    "scienze della formazione": "Scienze della Formazione",
    "psicologia": "Psicologia",
    "dipartimento di chimica": "Chimica",
    "scientifico": "other",
    "università degli studi di catania": "other (UniCT unspecified)",
    "university of catania": "other (UniCT unspecified)",
    "catania": "other (UniCT unspecified)",
    "data science university of catania": "Data Science",
}

def norm_dept(val):
    v = val.strip().lower()
    # redact any email address
    if re.search(r"@", v):
        return "redacted_pii"
    return DEPT_MAP.get(v, f"other ({val.strip()})")


# ─── Build stimuli manifest ───────────────────────────────────────────────────

def build_stimuli_manifest():
    rows = []
    img_dir = os.path.join(MATERIALS_DIR, "images")
    for var_num in ["1", "2", "3", "4", "5"]:
        var_name = VARIANT_NAME[var_num]
        folder = os.path.join(img_dir, var_name)
        files = sorted(os.listdir(folder), key=lambda f: int(f.split("_")[0]))
        for fname in files:
            if not fname.endswith(".jpg"):
                continue
            num = int(fname.split("_")[0])
            gt = suffix_to_gt(fname)
            image_id = f"{var_name}_{num:02d}"
            rows.append({
                "image_id": image_id,
                "variant": var_name,
                "presentation_order": num,
                "filename": fname,
                "ground_truth": gt,
            })
    out_path = os.path.join(MATERIALS_DIR, "stimuli_manifest.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image_id", "variant", "presentation_order", "filename", "ground_truth"])
        w.writeheader()
        w.writerows(rows)
    print(f"Scritto: {out_path}  ({len(rows)} righe)")
    return {(r["variant"], str(r["presentation_order"])): r["image_id"] for r in rows}


# ─── Build participant ID mapping ─────────────────────────────────────────────

def build_pid_mapping(rows):
    """Returns dict original_pid → new anonymous global P-ID."""
    pid_set = {}
    for row in rows:
        pid = row["participant_id"]
        v = row["variant"]
        if pid not in pid_set:
            pid_set[pid] = v
    # Sort: first by variant, then by numeric suffix of original pid
    def sort_key(item):
        pid, v = item
        m = re.search(r"(\d+)$", pid)
        return (v, int(m.group(1)) if m else 0)
    sorted_pids = sorted(pid_set.items(), key=sort_key)
    mapping = {}
    for idx, (orig_pid, _) in enumerate(sorted_pids, start=1):
        mapping[orig_pid] = f"P{idx:04d}"
    return mapping


# ─── Build responses CSV ──────────────────────────────────────────────────────

def build_responses(rows, pid_map, image_id_map, ai_conf_map):
    out_rows = []
    errors = 0
    for row in rows:
        new_pid = pid_map[row["participant_id"]]
        var_name = VARIANT_NAME[row["variant"]]
        image_id = image_id_map.get((var_name, row["image_num"]))
        if image_id is None:
            print(f"WARN: image_id not found for variant={var_name} img={row['image_num']}")
            errors += 1
            continue

        try:
            initial = norm_initial(row["initial_choice"])
        except ValueError as e:
            print(f"WARN: {e}")
            errors += 1
            continue

        try:
            final_action = norm_final(row["final_choice"])
        except ValueError as e:
            print(f"WARN: {e}")
            errors += 1
            continue

        # Derive effective final response
        if final_action == "confirm":
            effective_final = initial
        else:  # change
            effective_final = "real" if initial == "AI" else "AI"

        # Ground truth normalisation
        gt_raw = row["ground_truth"]
        if gt_raw == "Real":
            gt = "real"
        elif gt_raw == "AI-Generated (Midjourney)":
            gt = "AI_midjourney"
        elif gt_raw == "AI-Enhanced (Magnific)":
            gt = "AI_magnific"
        else:
            gt = gt_raw

        # Doubt
        doubt_val = row["doubt"].strip().lower()
        had_doubt = "yes" if doubt_val in ("sì", "si", "yes", "1") else "no"

        # AI confidence score
        conf = ai_conf_map.get((row["variant"], row["image_num"]), "")

        out_rows.append({
            "participant_id": new_pid,
            "variant": var_name,
            "image_id": image_id,
            "ground_truth": gt,
            "initial_response": initial,
            "had_doubt": had_doubt,
            "ai_confidence_score": conf,
            "post_suggestion_action": final_action,
            "effective_final_response": effective_final,
        })

    out_path = os.path.join(DATA_OUT, "responses_task.csv")
    fieldnames = [
        "participant_id", "variant", "image_id", "ground_truth",
        "initial_response", "had_doubt",
        "ai_confidence_score", "post_suggestion_action", "effective_final_response",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    print(f"Scritto: {out_path}  ({len(out_rows)} righe, {errors} errori)")


# ─── Build demographics CSV ───────────────────────────────────────────────────

def build_demographics(rows, pid_map):
    seen = {}
    for row in rows:
        pid = row["participant_id"]
        if pid in seen:
            continue
        seen[pid] = {
            "participant_id": pid_map[pid],
            "variant": VARIANT_NAME[row["variant"]],
            "age": row["age"].strip().replace("23 o più", "23_or_older").replace("o più", "_or_older"),
            "gender": row["gender"].strip(),
            "academic_affiliation": norm_dept(row["department"]),
        }

    out_rows = sorted(seen.values(), key=lambda r: r["participant_id"])
    out_path = os.path.join(DATA_OUT, "participants_demographics.csv")
    fieldnames = ["participant_id", "variant", "age", "gender", "academic_affiliation"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    print(f"Scritto: {out_path}  ({len(out_rows)} partecipanti)")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Load processed data
    proc_path = os.path.join(DATA_DIR, "processed_data.csv")
    with open(proc_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"Dati caricati: {len(rows)} righe, {len(set(r['participant_id'] for r in rows))} partecipanti")

    # Build ai_confidence map: (variant_num, image_num) -> score
    ai_conf_map = {}
    for row in rows:
        k = (row["variant"], row["image_num"])
        if k not in ai_conf_map:
            ai_conf_map[k] = row["ai_confidence_percentage"]

    image_id_map = build_stimuli_manifest()

    pid_map = build_pid_mapping(rows)
    print(f"PID mapping: {len(pid_map)} partecipanti → P0001…P{len(pid_map):04d}")

    build_responses(rows, pid_map, image_id_map, ai_conf_map)
    build_demographics(rows, pid_map)


if __name__ == "__main__":
    main()
