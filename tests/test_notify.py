import unittest

from mb.notify import message, timer_units


class NotifyTest(unittest.TestCase):
    # REQ MB-16
    def test_no_notification_when_the_record_is_current(self):
        self.assertIsNone(message([]))

    # REQ MB-16
    def test_notification_counts_and_shows_the_first_changes(self):
        title, body = message([f"apt + pkg{i}" for i in range(12)])
        self.assertIn("12", title)
        self.assertIn("apt + pkg0", body)
        self.assertIn("apt + pkg4", body)
        self.assertNotIn("apt + pkg5", body)
        self.assertIn("mb capture", body)

    # REQ MB-16
    def test_timer_runs_weekly_and_catches_up_after_the_laptop_was_off(self):
        service, timer = timer_units("/home/u/dev/machine-bootstrap")
        self.assertIn("ExecStart=/usr/bin/python3 -m mb status --notify", service)
        self.assertIn("WorkingDirectory=/home/u/dev/machine-bootstrap", service)
        self.assertIn("OnCalendar=weekly", timer)
        self.assertIn("Persistent=true", timer)


if __name__ == "__main__":
    unittest.main()
