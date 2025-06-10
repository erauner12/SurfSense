import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock
from datetime import datetime, timezone

from surfsense_backend.app.connectors.todoist_connector import TodoistConnector


class TestTodoistConnector(unittest.TestCase):
    D1 = "2025-01-01"
    D2 = "2025-01-31"

    # ---------- helpers ----------
    @staticmethod
    def _mk_task(task_id, is_recurring=False, completed=False):
        """Return a Mock that mimics todoist_api_python.models.Task."""
        mock_task = Mock()
        mock_task.task_id = task_id
        mock_task.id = task_id
        mock_task.content = f"Task {task_id}"
        mock_task.url = f"https://app.todoist.com/showTask?id={task_id}"
        mock_task.completed_at = datetime.now(timezone.utc).isoformat() if completed else None
        mock_task.due = SimpleNamespace(is_recurring=is_recurring, date="2025-01-02")
        # The SDK’s `.to_dict()` is what our code relies on.
        mock_task.to_dict.return_value = {
            "id": task_id,
            "content": mock_task.content,
            "completed_at": mock_task.completed_at,
            "due": {"date": "2025-01-02", "is_recurring": is_recurring},
        }
        return mock_task

    # ---------- tests ----------
    @patch("surfsense_backend.app.connectors.todoist_connector.TodoistAPI")
    def test_get_tasks_filters_recurring_and_builds_url(self, MockAPI):
        api = MockAPI.return_value
        # page 1 active tasks
        api.filter_tasks.return_value = [
            [self._mk_task("T1", is_recurring=False)],
            [self._mk_task("T2", is_recurring=True)],       # should be FILTERED OUT
        ]
        # completed tasks page
        api.get_completed_tasks_by_completion_date.return_value = [
            [self._mk_task("T3", is_recurring=False, completed=True)]
        ]

        conn = TodoistConnector(token="x")
        tasks, err = conn.get_tasks_by_date_range(self.D1, self.D2, include_completed=True)

        self.assertIsNone(err)
        self.assertEqual({t["id"] for t in tasks}, {"T1", "T3"})
        # Completed task URL should be rewritten
        t3 = next(t for t in tasks if t["id"] == "T3")
        self.assertEqual(t3["url"], "https://todoist.com/showTask?id=T3")

        # Active task keeps original url
        t1 = next(t for t in tasks if t["id"] == "T1")
        self.assertTrue(t1["url"].startswith("https://app.todoist.com"))

        # Ensure completed‐tasks endpoint was queried once
        api.get_completed_tasks_by_completion_date.assert_called_once()

    @patch("surfsense_backend.app.connectors.todoist_connector.TodoistAPI")
    def test_date_validation_error(self, MockAPI):
        conn = TodoistConnector(token="x")
        tasks, err = conn.get_tasks_by_date_range("2024-13-01", self.D2)
        self.assertEqual(tasks, [])
        self.assertIn("Invalid date format", err)

    def test_missing_token_error(self):
        conn = TodoistConnector()                # no token
        tasks, err = conn.get_tasks_by_date_range(self.D1, self.D2)
        self.assertEqual(tasks, [])
        self.assertIn("token not initialized", err.lower())

    def test__is_recurring_helper(self):
        task_recurring = SimpleNamespace(due=SimpleNamespace(is_recurring=True))
        task_not_recurring = SimpleNamespace(due=SimpleNamespace(is_recurring=False))
        task_due_no_recurring_attr = SimpleNamespace(due=SimpleNamespace()) # no is_recurring attr
        task_due_is_none = SimpleNamespace(due=None)
        task_no_due_attr = SimpleNamespace() # no due attr

        self.assertTrue(TodoistConnector._is_recurring(task_recurring))
        self.assertFalse(TodoistConnector._is_recurring(task_not_recurring))
        self.assertFalse(TodoistConnector._is_recurring(task_due_no_recurring_attr))
        self.assertFalse(TodoistConnector._is_recurring(task_due_is_none))
        self.assertFalse(TodoistConnector._is_recurring(task_no_due_attr))

    # --- Optional tests from instructions ---

    @patch("surfsense_backend.app.connectors.todoist_connector.TodoistAPI")
    def test_include_completed_false_skips_completed_call(self, MockAPI):
        api = MockAPI.return_value
        api.filter_tasks.return_value = [
            [self._mk_task("T1")]
        ]

        conn = TodoistConnector(token="x")
        tasks, err = conn.get_tasks_by_date_range(self.D1, self.D2, include_completed=False)

        self.assertIsNone(err)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['id'], 'T1')
        api.get_completed_tasks_by_completion_date.assert_not_called()

    @patch("surfsense_backend.app.connectors.todoist_connector.TodoistAPI")
    def test_handles_api_exception_gracefully(self, MockAPI):
        api = MockAPI.return_value
        api.filter_tasks.side_effect = Exception("Active tasks API failed")
        api.get_completed_tasks_by_completion_date.side_effect = Exception("Completed tasks API failed")

        conn = TodoistConnector(token="x")
        tasks, err = conn.get_tasks_by_date_range(self.D1, self.D2, include_completed=True)

        self.assertEqual(tasks, [])
        self.assertIn("Error fetching active tasks: Active tasks API failed", err)
        self.assertIn("Error fetching completed tasks: Completed tasks API failed", err)


if __name__ == "__main__":
    unittest.main()