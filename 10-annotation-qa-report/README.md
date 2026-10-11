# Annotation QA Report

Feed in a CSV of labels from your annotators and get a Markdown report. It shows:

- how often each label was used
- how often each annotator matches the majority label
- which tasks have no majority and need a second look

This is the sort of check that catches a bad annotator or unclear guidelines before the data goes into training.

**Skills shown:** data analysis, quality control for AI training data, clear reporting.

## Run the tests

```
python3 -m unittest -v
```

## Run on the sample data

```
python3 annotation_report.py sample_annotations.csv
```

## Input format

```
task_id,annotator,label
t1,ann_a,good
t1,ann_b,bad
```
