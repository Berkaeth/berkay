#!/usr/bin/env python3
"""Pin Factory: generate Pinterest keywords, pin copy, and a 30-day plan."""

from __future__ import annotations

import argparse
import csv
import os
import random
import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence

PIN_FORMATS = [
    "List pin",
    "Checklist",
    "Mini-guide",
    "Template preview",
    "Mistakes to avoid",
    "Before/After",
]

EVERGREEN_MODIFIERS = [
    "for beginners",
    "ideas",
    "template",
    "checklist",
    "planner",
    "guide",
    "printable",
]

THEME_TEMPLATES = [
    "Beginner Basics",
    "Daily Practice",
    "Printable Templates",
    "Guides & How-Tos",
    "Ideas & Inspiration",
    "Mistakes to Avoid",
    "Before & After",
    "Planner Flow",
]

TITLE_TEMPLATES = [
    "{keyword} you can try today",
    "Simple {keyword} ideas",
    "A fresh take on {keyword}",
    "{keyword} made easy",
    "Starter {keyword} checklist",
    "Quick guide to {keyword}",
    "{keyword} for a calm routine",
    "{keyword} you will love",
]

DESCRIPTION_TEMPLATES = [
    "Quick idea for {keyword}. {cta}",
    "Simple inspiration for {keyword}. {cta}",
    "A gentle approach to {keyword}. {cta}",
    "Clear steps for {keyword}. {cta}",
]

CTA_OPTIONS = [
    "Save this for later.",
    "Explore the idea.",
    "Get inspired.",
]


@dataclass(frozen=True)
class KeywordItem:
    niche: str
    theme: str
    keyword: str


@dataclass(frozen=True)
class PinItem:
    niche: str
    theme: str
    keyword: str
    pin_format: str
    title: str
    description: str


def slug_words(text: str) -> List[str]:
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text).lower()
    words = [w for w in cleaned.split() if w]
    return words


def normalize_keyword(keyword: str) -> str:
    return re.sub(r"\s+", " ", keyword.strip().lower())


def signature(keyword: str) -> str:
    words = []
    for word in slug_words(keyword):
        if word.endswith("s") and len(word) > 3:
            word = word[:-1]
        words.append(word)
    return " ".join(sorted(words))


def choose_themes(rng: random.Random, count: int) -> List[str]:
    unique = list(dict.fromkeys(THEME_TEMPLATES))
    rng.shuffle(unique)
    count = max(5, min(8, count))
    return unique[:count]


def distribute_counts(total: int, buckets: int) -> List[int]:
    base = total // buckets
    remainder = total % buckets
    counts = [base] * buckets
    for i in range(remainder):
        counts[i] += 1
    return counts


def build_keyword_patterns(niche: str) -> List[str]:
    base = " ".join(slug_words(niche))
    core = base if base else niche.strip().lower()
    return [
        f"{core} ideas",
        f"{core} for beginners",
        f"{core} checklist",
        f"{core} guide",
        f"{core} printable",
        f"{core} planner",
        f"daily {core} routine",
        f"simple {core} prompts",
        f"easy {core} template",
        f"{core} journal layout",
        f"{core} tracker printable",
        f"{core} log template",
        f"{core} pages to try",
        f"{core} starter kit",
        f"{core} inspiration board",
    ]


def generate_keywords(
    niche: str,
    themes: Sequence[str],
    total_keywords: int,
    rng: random.Random,
) -> List[KeywordItem]:
    base_patterns = build_keyword_patterns(niche)
    modifiers = EVERGREEN_MODIFIERS
    theme_counts = distribute_counts(total_keywords, len(themes))
    items: List[KeywordItem] = []
    seen = set()
    seen_signature = set()

    for theme, count in zip(themes, theme_counts):
        attempts = 0
        while count > 0 and attempts < total_keywords * 10:
            attempts += 1
            pattern = rng.choice(base_patterns)
            modifier = rng.choice(modifiers)
            keyword = pattern
            if modifier not in pattern:
                keyword = f"{pattern} {modifier}"
            keyword = normalize_keyword(keyword)
            if not (3 <= len(keyword.split()) <= 8):
                continue
            key = normalize_keyword(keyword)
            sig = signature(keyword)
            if key in seen or sig in seen_signature:
                continue
            seen.add(key)
            seen_signature.add(sig)
            items.append(KeywordItem(niche=niche, theme=theme, keyword=keyword))
            count -= 1

    return items


def title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def generate_pin_copy(
    keywords: Iterable[KeywordItem],
    pins_per_keyword: int,
    rng: random.Random,
) -> List[PinItem]:
    pins: List[PinItem] = []
    for item in keywords:
        for idx in range(pins_per_keyword):
            pin_format = PIN_FORMATS[(idx + rng.randint(0, len(PIN_FORMATS) - 1)) % len(PIN_FORMATS)]
            title_template = rng.choice(TITLE_TEMPLATES)
            title = title_template.format(keyword=item.keyword)
            title = title_case(title)
            if not (4 <= len(title.split()) <= 10):
                title = title_case(f"{item.keyword} ideas")
            description_template = rng.choice(DESCRIPTION_TEMPLATES)
            cta = rng.choice(CTA_OPTIONS)
            description = description_template.format(keyword=item.keyword, cta=cta)
            pins.append(
                PinItem(
                    niche=item.niche,
                    theme=item.theme,
                    keyword=item.keyword,
                    pin_format=pin_format,
                    title=title,
                    description=description,
                )
            )
    return pins


def write_csv(path: str, headers: Sequence[str], rows: Iterable[Sequence[str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def build_plan_md(
    niche: str,
    themes: Sequence[str],
    pins: Sequence[PinItem],
) -> str:
    summary = (
        f"**Niche Summary:** {niche.title()} works well on Pinterest because it is evergreen, "
        "search-driven, and suited for faceless, idea-forward pins that people save for later."
    )
    theme_lines = "\n".join(f"- {theme}" for theme in themes)
    format_lines = "\n".join(
        [
            "- **List pin:** Quick, scannable ideas grouped in one pin.",
            "- **Checklist:** Simple steps or prompts in a tick-box style.",
            "- **Mini-guide:** A short how-to with a clear start and finish.",
            "- **Template preview:** A peek at a layout or printable structure.",
            "- **Mistakes to avoid:** Helpful do-not-do reminders.",
            "- **Before/After:** Contrast of an unfocused vs. improved approach.",
        ]
    )

    plan_rows = []
    total_days = 30
    for day in range(1, total_days + 1):
        pin = pins[(day - 1) % len(pins)]
        plan_rows.append(
            f"| {day} | {pin.theme} | {pin.keyword} | {pin.title} | {pin.pin_format} |"
        )

    table_header = "| Day | Theme | Keyword | Pin Title | Pin Format |"
    table_divider = "| --- | --- | --- | --- | --- |"
    table_body = "\n".join(plan_rows)

    return (
        "# 30-Day Pin Posting Plan\n\n"
        f"{summary}\n\n"
        "## Themes\n\n"
        f"{theme_lines}\n\n"
        "## Faceless Pin Format Explanations\n\n"
        f"{format_lines}\n\n"
        "## 30-Day Schedule\n\n"
        f"{table_header}\n{table_divider}\n{table_body}\n"
    )


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Pinterest pin assets.")
    parser.add_argument("--niche", required=True, help="Niche to target, e.g. 'tarot journal printables'")
    parser.add_argument("--num_keywords", type=int, default=50)
    parser.add_argument("--pins_per_keyword", type=int, default=3)
    parser.add_argument("--themes", type=int, default=6)
    parser.add_argument("--output_dir", default="output")
    parser.add_argument("--seed", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    themes = choose_themes(rng, args.themes)
    keywords = generate_keywords(args.niche, themes, args.num_keywords, rng)
    if not keywords:
        raise SystemExit("No keywords generated; adjust inputs and try again.")

    pins = generate_pin_copy(keywords, args.pins_per_keyword, rng)

    ensure_output_dir(args.output_dir)
    keywords_path = os.path.join(args.output_dir, "keywords.csv")
    pins_path = os.path.join(args.output_dir, "pins.csv")
    plan_path = os.path.join(args.output_dir, "plan.md")

    write_csv(
        keywords_path,
        ["niche", "theme", "keyword"],
        ([item.niche, item.theme, item.keyword] for item in keywords),
    )
    write_csv(
        pins_path,
        ["niche", "theme", "keyword", "pin_format", "title", "description"],
        (
            [
                item.niche,
                item.theme,
                item.keyword,
                item.pin_format,
                item.title,
                item.description,
            ]
            for item in pins
        ),
    )

    plan_md = build_plan_md(args.niche, themes, pins)
    with open(plan_path, "w", encoding="utf-8") as handle:
        handle.write(plan_md)


if __name__ == "__main__":
    main()
