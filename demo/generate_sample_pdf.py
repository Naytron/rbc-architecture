"""Generate a synthetic one-page PDF for the low-cost demo.

ILLUSTRATIVE ONLY. The text matches examples/synthetic-input.md: a fictional
person and a fictional location. This script creates no real case material.
"""

import argparse

import pymupdf as fitz

SYNTHETIC_TEXT = (
    "At 14:20, the report describes Person A as Black. "
    "Person A wore a green coat near Fictional Square."
)


def generate_sample_pdf(out_path: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), SYNTHETIC_TEXT, fontsize=12)
    doc.save(out_path)
    doc.close()
    print(f"Wrote synthetic test document: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="sample.pdf", help="Output PDF path")
    args = parser.parse_args()
    generate_sample_pdf(args.out)
