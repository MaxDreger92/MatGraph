from django.test import SimpleTestCase
from django.urls import resolve, reverse

from importing.views import (
	AttributeExtractView,
	CancelTaskView,
	GraphExtractView,
	GraphImportView,
	LabelExtractView,
	NodeExtractView,
	ProcessDeleteView,
	ProcessReportView,
)


class ImportingApiContractTests(SimpleTestCase):
	"""Guards the importing API surface during refactors and extraction."""

	def test_routes_resolve_to_expected_views(self):
		self.assertEqual(resolve("/api/import/label-extract").func.view_class, LabelExtractView)
		self.assertEqual(resolve("/api/import/attribute-extract").func.view_class, AttributeExtractView)
		self.assertEqual(resolve("/api/import/node-extract").func.view_class, NodeExtractView)
		self.assertEqual(resolve("/api/import/graph-extract").func.view_class, GraphExtractView)
		self.assertEqual(resolve("/api/import/graph-import").func.view_class, GraphImportView)
		self.assertEqual(resolve("/api/import/cancel").func.view_class, CancelTaskView)
		self.assertEqual(resolve("/api/import/report").func.view_class, ProcessReportView)
		self.assertEqual(resolve("/api/import/delete").func.view_class, ProcessDeleteView)

	def test_named_routes_reverse_to_expected_paths(self):
		self.assertEqual(reverse("label-extract"), "/api/import/label-extract")
		self.assertEqual(reverse("attribute-extract"), "/api/import/attribute-extract")
		self.assertEqual(reverse("node-extract"), "/api/import/node-extract")
		self.assertEqual(reverse("graph-extract"), "/api/import/graph-extract")
		self.assertEqual(reverse("graph-import"), "/api/import/graph-import")
		self.assertEqual(reverse("process-cancel"), "/api/import/cancel")
		self.assertEqual(reverse("process-report"), "/api/import/report")
		self.assertEqual(reverse("process-delete"), "/api/import/delete")

	def test_method_contracts_and_basic_validation_behavior(self):
		post_paths = [
			"/api/import/label-extract",
			"/api/import/attribute-extract",
			"/api/import/node-extract",
			"/api/import/graph-extract",
			"/api/import/graph-import",
		]

		for path in post_paths:
			allowed = self.client.post(path, data={}, content_type="application/json")
			self.assertNotEqual(allowed.status_code, 405, msg=f"POST should be allowed for {path}")

			disallowed = self.client.get(path)
			self.assertIn(
				disallowed.status_code,
				{401, 403, 405},
				msg=f"GET should be rejected for {path}",
			)

		cancel_patch = self.client.patch("/api/import/cancel", data={}, content_type="application/json")
		self.assertNotEqual(cancel_patch.status_code, 405)
		self.assertIn(self.client.get("/api/import/cancel").status_code, {401, 403, 405})

		report_get = self.client.get("/api/import/report")
		self.assertNotEqual(report_get.status_code, 405)
		self.assertIn(
			self.client.post("/api/import/report", data={}, content_type="application/json").status_code,
			{401, 403, 405},
		)

		delete_call = self.client.delete("/api/import/delete")
		self.assertNotEqual(delete_call.status_code, 405)
		self.assertIn(self.client.get("/api/import/delete").status_code, {401, 403, 405})
