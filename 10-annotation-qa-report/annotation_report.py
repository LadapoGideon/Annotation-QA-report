"""Summarise annotation data: label counts, majority labels, and each annotator's agreement.

Input is a CSV with the columns: task_id, annotator, label.
Usage: python3 annotation_report.py annotations.csv
"""
import csv
import sys
from collections import Counter, defaultdict


def load_rows(file_obj):
    rows = list(csv.DictReader(file_obj))
    required = {"task_id", "annotator", "label"}
    if rows and not required.issubset(rows[0].keys()):
        raise ValueError(f"CSV must have columns: {sorted(required)}")
    return rows


def majority_labels(rows):
    """Majority label per task. Tasks with a tie between labels get None."""
    by_task = defaultdict(list)
    for row in rows:
        by_task[row["task_id"]].append(row["label"])

    result = {}
    for task, labels in by_task.items():
        ranked = Counter(labels).most_common()
        top_count = ranked[0][1]
        leaders = [label for label, count in ranked if count == top_count]
        result[task] = leaders[0] if len(leaders) == 1 else None
    return result


def annotator_stats(rows):
    majority = majority_labels(rows)
    stats = defaultdict(lambda: {"labelled": 0, "agreed": 0, "tied_tasks": 0})
    for row in rows:
        entry = stats[row["annotator"]]
        entry["labelled"] += 1
        consensus = majority[row["task_id"]]
        if consensus is None:
            entry["tied_tasks"] += 1
        elif row["label"] == consensus:
            entry["agreed"] += 1

    report = {}
    for annotator, entry in stats.items():
        scored = entry["labelled"] - entry["tied_tasks"]
        report[annotator] = {
            "labelled": entry["labelled"],
            "agreement_with_majority": round(entry["agreed"] / scored, 3) if scored else None,
            "tied_tasks": entry["tied_tasks"],
        }
    return report


def render_markdown(rows):
    distribution = Counter(row["label"] for row in rows)
    lines = ["# Annotation QA Report", "", "## Label distribution", ""]
    for label, count in distribution.most_common():
        lines.append(f"- {label}: {count}")

    lines += ["", "## Annotators", "", "| Annotator | Labels | Agreement with majority | Tied tasks |", "|---|---|---|---|"]
    for name, s in sorted(annotator_stats(rows).items()):
        rate = "n/a" if s["agreement_with_majority"] is None else f"{s['agreement_with_majority']:.1%}"
        lines.append(f"| {name} | {s['labelled']} | {rate} | {s['tied_tasks']} |")

    majority = majority_labels(rows)
    tied = [task for task, label in majority.items() if label is None]
    lines += ["", "## Tasks needing review", ""]
    lines += [f"- {task}: no majority" for task in sorted(tied)] or ["None"]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 annotation_report.py annotations.csv")
    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        print(render_markdown(load_rows(f)))
