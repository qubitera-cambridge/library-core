#!/usr/bin/env python3
"""Stage 2 of the documentation site build: render every algorithm's page from
metadata.yaml (always present), EXPLANATION.md (optional, hand-written prose),
and a cached demo() result (optional, produced by generate_demo_outputs.py).

Deliberately needs no quantum SDK — only the pre-generated demo cache, which is
why this is a separate step from generate_demo_outputs.py. Output goes to
website/build/, which mkdocs.yml points `docs_dir` at; nothing here is
committed to git (website/build/ is gitignored) since it's fully derived from
metadata.yaml + EXPLANATION.md + the demo cache.

See docs/site-generation.md.
"""

import json
from pathlib import Path

import jinja2
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ALGORITHMS_DIR = REPO_ROOT / "algorithms"
TEMPLATES_DIR = REPO_ROOT / "website" / "templates"
DEMO_CACHE_DIR = REPO_ROOT / "website" / "demo_cache"
BUILD_DIR = REPO_ROOT / "website" / "build"


def _algorithm_dirs():
    return sorted(p.parent for p in ALGORITHMS_DIR.glob("*/*/metadata.yaml"))


def render_site():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    algorithm_template = env.get_template("algorithm.md.j2")
    index_template = env.get_template("index.md.j2")

    categories = {}

    for algo_dir in _algorithm_dirs():
        with open(algo_dir / "metadata.yaml") as f:
            meta = yaml.safe_load(f)

        explanation_path = algo_dir / "EXPLANATION.md"
        explanation = explanation_path.read_text() if explanation_path.exists() else None

        demo_cache_path = DEMO_CACHE_DIR / f"{meta['id']}.json"
        demo = json.loads(demo_cache_path.read_text()) if demo_cache_path.exists() else None

        algo_repo_path = str(algo_dir.relative_to(REPO_ROOT))

        page = algorithm_template.render(
            meta=meta, explanation=explanation, demo=demo, algo_repo_path=algo_repo_path
        )

        out_path = BUILD_DIR / meta["category"] / f"{meta['id']}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page)
        print(f"rendered: {out_path.relative_to(REPO_ROOT)}")

        categories.setdefault(meta["category"], []).append(meta)

    index_page = index_template.render(categories=categories)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.md").write_text(index_page)
    print(f"rendered: {(BUILD_DIR / 'index.md').relative_to(REPO_ROOT)}")

    total = sum(len(v) for v in categories.values())
    print(f"\n{total} algorithm page(s) rendered across {len(categories)} categor(y/ies)")


if __name__ == "__main__":
    render_site()
