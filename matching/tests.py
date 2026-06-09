from django.test import SimpleTestCase
from django.urls import resolve, reverse

from matching.views import WorkflowMatcher


class MatchingApiContractTests(SimpleTestCase):
    """Guards the matching API surface during refactors and extraction."""

    def test_route_resolves_to_expected_view(self):
        self.assertEqual(
            resolve("/api/match/fabrication-workflow").func.view_class,
            WorkflowMatcher,
        )

    def test_named_route_reverses_to_expected_path(self):
        self.assertEqual(reverse("fabrication_workflow"), "/api/match/fabrication-workflow")

    def test_method_contracts_and_basic_validation_behavior(self):
        allowed = self.client.post(
            "/api/match/fabrication-workflow",
            data={},
            content_type="application/json",
        )
        self.assertNotEqual(allowed.status_code, 405)

        disallowed = self.client.get("/api/match/fabrication-workflow")
        self.assertIn(disallowed.status_code, {401, 403, 405})
