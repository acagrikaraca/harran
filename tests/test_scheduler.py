import unittest
from datetime import date

from bulletins.scheduler import should_run


class SchedulerTests(unittest.TestCase):
    def test_runs_on_15(self):
        decision = should_run(date(2026, 1, 15))
        self.assertTrue(decision.run_today)

    def test_runs_on_30(self):
        decision = should_run(date(2026, 1, 30))
        self.assertTrue(decision.run_today)

    def test_runs_on_feb_last_day(self):
        decision = should_run(date(2026, 2, 28))
        self.assertTrue(decision.run_today)

    def test_non_schedule_day(self):
        decision = should_run(date(2026, 1, 18))
        self.assertFalse(decision.run_today)


if __name__ == "__main__":
    unittest.main()
