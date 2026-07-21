"""
Build-time script: Extract Kuesioner Profil Risiko from PDF → data/kuesioner.json
Uses regex + rule-based parsing (NLP-lite), not LLM.
"""

import re, json, os, sys
from langchain_community.document_loaders import PyPDFLoader

PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "Kuesioner-Profil-Risiko.pdf")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "kuesioner.json")


def parse_kuesioner(text: str) -> dict:
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    profiles = []

    # === Phase 1: Extract questions and options ===
    question_texts = []
    option_blocks = []
    current_options = []

    for line in lines:
        o = re.match(r"^([a-d])\.\s+(.+)$", line)
        if o:
            current_options.append((o.group(1), o.group(2)))
            if o.group(1) == "d":
                option_blocks.append(list(current_options))
                current_options = []
            continue

    q_patterns = [
        r"lama masa investasi",
        r"tujuan\s+dari\s+investasi",
        r"risiko kerugian",
        r"dana yang siap",
        r"tingkat pengetahuan",
    ]
    for line in lines:
        if "TOTAL SKOR" in line:
            break
        if line.strip() == "SKOR":
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"^[a-d]\.", line):
            continue
        lower = line.lower()
        if any(re.search(p, lower) for p in q_patterns):
            cleaned = re.sub(r"\s*[\dA-Z]+\s*$", "", line).strip()
            cleaned = re.sub(r"^\d+\s+", "", cleaned).strip()
            cleaned = re.sub(r"\?(\d+)$", "?", cleaned).strip()
            if cleaned not in question_texts:
                question_texts.append(cleaned)

    questions = []
    for i, q_text in enumerate(question_texts):
        if i < len(option_blocks):
            opts = option_blocks[i]
            if len(opts) == 4:
                questions.append({
                    "text": q_text,
                    "options": [
                        {"label": f"{k}.", "text": v, "score": sc}
                        for (k, v), sc in zip(opts, [5, 10, 15, 20])
                    ],
                })

    # === Phase 2: Extract profile headers ===
    for line in lines:
        m = re.match(
            r"^(Konservatif|Moderat|Agresif|Sangat\s*Agresif)\s*\|\|\s*Total Skor.*?:\s*([\d\s>]+)\s*-\s*(\d+)$",
            line,
        )
        if m:
            name = m.group(1).replace(" ", " ")
            raw = m.group(2).strip()
            min_raw = int(re.sub(r"[^\d]", "", raw)) if re.search(r"\d", raw) else 0
            if ">" in raw:
                min_score = min_raw + 1
            else:
                min_score = min_raw
            max_score = int(m.group(3))
            profiles.append({
                "name": name.title(),
                "min_score": min_score,
                "max_score": max_score,
            })

    profiles.sort(key=lambda p: p["min_score"])

    # === Phase 3: Extract profile descriptions ===
    normalized_lines = [l.replace("\ufb01", "fi") for l in lines]

    desc_raw = []
    in_desc = False
    for line in normalized_lines:
        if "Profil Risiko" in line and "Berdasarkan" in line:
            in_desc = True
            continue
        if in_desc:
            if "||" in line and "Total Skor" in line:
                continue
            if "KATEGORI PRODUK" in line:
                break
            desc_raw.append(line.strip())

    full = " ".join(desc_raw)
    full = full.replace("Prioritas Anda", "\n__MODERAT__")
    full = full.replace("Tujuan investasi Anda adalah", "\n__SANGAT_AGRESIF__")
    full = full.replace("Tujuan investasi Anda ", "\n__AGRESIF__")
    full = full.replace("__SANGAT_AGRESIF__", "Tujuan investasi Anda adalah ")
    full = full.replace("__AGRESIF__", "Tujuan investasi Anda ")
    full = full.replace("__MODERAT__", "Prioritas Anda ")

    desc_groups = [p.strip() for p in full.split("\n") if p.strip()]
    desc_groups = [g for g in desc_groups if len(g) > 50 and "||" not in g]

    for i, p in enumerate(profiles):
        if i < len(desc_groups):
            desc = desc_groups[i]
            desc = re.sub(r"\s+Moderat\s+Sangat\s+Agresif.*$", "", desc)
            desc = re.sub(r"\s+Tunai\s+Pendapatan\s+Berkembang.*$", "", desc)
            p["description"] = desc.strip()

    # === Phase 4: Set pasar modal categories ===
    remap_categories = {
        "Saham": ["Saham"],
        "Obligasi": ["Obligasi Pemerintah", "Obligasi Korporasi"],
        "Reksa Dana": [
            "Reksa Dana Pasar Uang",
            "Reksa Dana Pendapatan Tetap",
            "Reksa Dana Campuran",
            "Reksa Dana Saham",
            "Reksa Dana Terproteksi",
        ],
    }

    remap_alloc = {
        "Konservatif": {"Saham": "10%", "Obligasi": "30%", "Reksa Dana": "60%"},
        "Moderat": {"Saham": "30%", "Obligasi": "30%", "Reksa Dana": "40%"},
        "Agresif": {"Saham": "60%", "Obligasi": "15%", "Reksa Dana": "25%"},
        "Sangat Agresif": {"Saham": "75%", "Obligasi": "10%", "Reksa Dana": "15%"},
    }

    for p in profiles:
        p["allocation"] = remap_alloc.get(p["name"], {})

    return {
        "questions": questions,
        "profiles": profiles,
        "product_categories": remap_categories,
    }


def main():
    print(f"[Extract] Loading PDF: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    text = docs[0].page_content
    print(f"[Extract] Raw length: {len(text)} chars")

    data = parse_kuesioner(text)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Extract] Saved to: {OUT_PATH}")
    print(f"  Questions: {len(data['questions'])}")
    for q in data["questions"]:
        print(f"    - {q['text'][:60]} ({len(q['options'])} options)")
    print(f"  Profiles: {len(data['profiles'])}")
    for p in data["profiles"]:
        print(f"    - {p['name']}: {p['min_score']}-{p['max_score']}")
    print(f"  Product categories: {list(data['product_categories'].keys())}")


if __name__ == "__main__":
    main()
