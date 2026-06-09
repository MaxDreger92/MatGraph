from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from importing.tasks import task_cancelled as importing_task_cancelled
from matching.tasks import task_cancelled as matching_task_cancelled
from tasks.models import ProcessKeys, ProcessStatus
from tasks.utils import callback as callback_module
from tasks.utils.callback import send_callback


class ProcessStateTransitionTests(SimpleTestCase):
	"""Locks cancellation state transitions for importing and matching flows."""

	def test_importing_task_cancelled_sets_cancelled_status_and_message(self):
		process = SimpleNamespace(
			process_id="import-cancel-1",
			status=ProcessStatus.PROCESSING,
			error_message="",
			save=Mock(),
		)

		importing_task_cancelled(process)

		self.assertEqual(process.status, ProcessStatus.CANCELLED)
		self.assertEqual(process.error_message, "Task was cancelled by the user.")
		process.save.assert_called_once()

	def test_matching_task_cancelled_sets_cancelled_status_and_message(self):
		process = SimpleNamespace(
			process_id="match-cancel-1",
			status=ProcessStatus.PROCESSING,
			error_message="",
			save=Mock(),
		)

		matching_task_cancelled(process)

		self.assertEqual(process.status, ProcessStatus.CANCELLED)
		self.assertEqual(process.error_message, "Task was cancelled by the user.")
		process.save.assert_called_once()


class CallbackContractTests(SimpleTestCase):
	"""Verifies callback payload format so external integrations stay stable."""

	@patch("tasks.utils.callback.requests.post")
	@patch("tasks.utils.callback.ImportProcess.objects.get")
	@patch("tasks.utils.callback.ExtractProcess.objects.get")
	def test_importing_callback_sends_json_payload(self, mock_extract_get, mock_import_get, mock_post):
		mock_response = Mock()
		mock_response.raise_for_status.return_value = None
		mock_post.return_value = mock_response
		mock_extract_get.side_effect = Exception("Should not query extract process")

		process = SimpleNamespace(
			process_id="import-callback-1",
			user_id="101",
			labels={"col": "Matter"},
			status=ProcessStatus.COMPLETED,
			callback_url="https://callback.example/hook",
			error_message="",
		)
		mock_import_get.return_value = process

		send_callback(process.process_id, ProcessKeys.LABELS)

		mock_post.assert_called_once()
		args, kwargs = mock_post.call_args
		self.assertEqual(args[0], "https://callback.example/hook/")
		self.assertIn("headers", kwargs)
		self.assertIn("X-API-KEY", kwargs["headers"])
		self.assertEqual(kwargs["timeout"], 15)

		payload = kwargs["json"]
		self.assertEqual(payload["process_id"], process.process_id)
		self.assertEqual(payload["user_id"], 101)
		self.assertEqual(payload["key"], ProcessKeys.LABELS)
		self.assertEqual(payload["status"], ProcessStatus.COMPLETED)
		self.assertEqual(payload["results"], {"col": "Matter"})

	@patch("tasks.utils.callback.requests.post")
	@patch("tasks.utils.callback.ImportProcess.objects.get")
	@patch("tasks.utils.callback.ExtractProcess.objects.get")
	def test_matching_dataset_callback_sends_csv_file_payload(self, mock_extract_get, mock_import_get, mock_post):
		mock_response = Mock()
		mock_response.raise_for_status.return_value = None
		mock_post.return_value = mock_response

		process = SimpleNamespace(
			process_id="match-callback-1",
			user_id="202",
			dataset="a,b\n1,2\n",
			status=ProcessStatus.COMPLETED,
			callback_url="https://callback.example/dataset",
			error_message="",
		)
		mock_import_get.side_effect = callback_module.ImportProcess.DoesNotExist
		mock_extract_get.return_value = process

		send_callback(process.process_id, ProcessKeys.DATASET)

		mock_post.assert_called_once()
		args, kwargs = mock_post.call_args
		self.assertEqual(args[0], "https://callback.example/dataset/")
		self.assertIn("data", kwargs)
		self.assertEqual(kwargs["data"]["key"], ProcessKeys.DATASET)
		self.assertNotIn("json", kwargs)
		self.assertIn("files", kwargs)

		file_name, file_obj, mime_type = kwargs["files"]["results"]
		self.assertEqual(file_name, "data_extract.csv")
		self.assertEqual(mime_type, "text/csv")
		self.assertEqual(file_obj.read(), b"a,b\n1,2\n")

	@patch("tasks.utils.callback.requests.post")
	@patch("tasks.utils.callback.ImportProcess.objects.get")
	def test_callback_is_skipped_when_no_callback_url(self, mock_import_get, mock_post):
		process = SimpleNamespace(
			process_id="import-callback-2",
			user_id="303",
			labels={"col": "Matter"},
			status=ProcessStatus.COMPLETED,
			callback_url=None,
			error_message="",
		)
		mock_import_get.return_value = process

		send_callback(process.process_id, ProcessKeys.LABELS)

		mock_post.assert_not_called()
