import io
import unittest

from annotation_report import annotator_stats, load_rows, majority_labels, render_markdown


CSV_TEXT = """task_id,annotator,label
t1,ann_a,good
t1,ann_b,good
t1,ann_c,bad
t2,ann_a,bad
t2,ann_b,bad
t2,ann_c,bad
t3,ann_a,good
t3,ann_b,bad
t3,ann_c,neutral
"""


class AnnotationReportTests(unittest.TestCase):
    def setUp(self):
        self.rows = load_rows(io.StringIO(CSV_TEXT))

    def test_majority_labels_and_ties(self):
        majority = majority_labels(self.rows)
        self.assertEqual(majority["t1"], "good")
        self.assertEqual(majority["t2"], "bad")
        self.assertIsNone(majority["t3"])  # three-way tie

    def test_agreement_skips_tied_tasks(self):
        stats = annotator_stats(self.rows)
        self.assertEqual(stats["ann_a"]["agreement_with_majority"], 1.0)
        self.assertEqual(stats["ann_c"]["agreement_with_majority"], 0.5)  # agreed on t2 only, out of t1 and t2
        self.assertEqual(stats["ann_c"]["tied_tasks"], 1)

    def test_report_lists_tied_tasks_for_review(self):
        report = render_markdown(self.rows)
        self.assertIn("- t3: no majority", report)
        self.assertIn("| ann_b |", report)

    def test_missing_columns_are_rejected(self):
        with self.assertRaises(ValueError):
            load_rows(io.StringIO("task,person,tag\n1,a,x\n"))


if __name__ == "__main__":
    unittest.main()
