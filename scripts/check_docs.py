"""Check documentation consistency without network access or third-party packages."""

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def heading_anchors(text):
    anchors = set()
    seen = {}
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        match = re.match(r"^#{1,6}\s+(.+)$", line)
        if match:
            heading = match.group(1).strip().lower()
            slug = re.sub(r"[^\w -]", "", heading).replace(" ", "-")
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            anchors.add(f"{slug}-{count}" if count else slug)
    return anchors


def check():
    errors = []
    markdown_files = sorted(ROOT.rglob("*.md"))
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        if len(re.findall(r"^```", text, re.MULTILINE)) % 2:
            errors.append(f"{relative}: unbalanced fenced blocks")
        for link in re.findall(r"!?\[[^\]]*\]\(([^)\s]+)\)", text):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not target.is_relative_to(ROOT):
                errors.append(f"{relative}: link escapes repository: {link}")
            elif not target.exists():
                errors.append(f"{relative}: missing target: {link}")
            elif parsed.fragment and target.suffix == ".md":
                if unquote(parsed.fragment) not in heading_anchors(target.read_text(encoding="utf-8")):
                    errors.append(f"{relative}: missing heading anchor: {link}")

    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    embedded = re.findall(r"```mermaid\n(.*?)\n```", architecture, re.DOTALL)
    diagrams = sorted((ROOT / "diagrams").glob("*.mmd"))
    if len(embedded) != 4 or len(diagrams) != 4:
        errors.append("Expected four embedded and four standalone diagrams")
    for path in diagrams:
        source = path.read_text(encoding="utf-8").strip()
        if embedded.count(source) != 1:
            errors.append(f"{path.relative_to(ROOT)}: not matched exactly once in architecture.md")

    manifest = json.loads((ROOT / "examples/illustrative-manifest.json").read_text(encoding="utf-8"))
    canonical = manifest["extraction"]["canonicalText"]
    input_text = (ROOT / "examples/synthetic-input.md").read_text(encoding="utf-8")
    if f"```text\n{canonical}\n```" not in input_text:
        errors.append("Synthetic input and manifest canonical text differ")
    for candidate in manifest["candidates"]:
        span = candidate["span"]
        offset, length = span["offset"], span["length"]
        if offset < 0 or length <= 0 or canonical[offset:offset + length] != span["text"]:
            errors.append("Illustrative candidate span does not match canonical text")
    expected_output = canonical.replace("Black", "[REMOVED: explicit race reference]")
    output_text = (ROOT / "examples/illustrative-output.md").read_text(encoding="utf-8")
    if f"```text\n{expected_output}\n```" not in output_text:
        errors.append("Illustrative output differs from the documented removal")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Checked {len(markdown_files)} Markdown files, local links/anchors, 4 diagram copies, and synthetic examples.")
    print("Mermaid grammar/rendering and PDF integrity were not validated by this script.")


if __name__ == "__main__":
    check()
