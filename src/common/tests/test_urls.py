"""URL routing regressions for community CRUD views."""

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from common.views.communities import (
    communities_delete,
    communities_delete_municipal,
    communities_edit,
    communities_edit_municipal,
)


class CommunityUrlTests(SimpleTestCase):
    """Ensure barangay and municipal CRUD URLs route to the expected views."""

    def test_barangay_edit_url(self) -> None:
        url = reverse("common:communities_edit", args=[1])
        self.assertEqual(url, "/communities/1/edit/")
        self.assertIs(resolve(url).func, communities_edit)

    def test_barangay_delete_url(self) -> None:
        url = reverse("common:communities_delete", args=[1])
        self.assertEqual(url, "/communities/1/delete/")
        self.assertIs(resolve(url).func, communities_delete)

    def test_municipal_edit_url(self) -> None:
        url = reverse("common:communities_edit_municipal", args=[2])
        self.assertEqual(url, "/communities/municipal/2/edit/")
        self.assertIs(resolve(url).func, communities_edit_municipal)

    def test_municipal_delete_url(self) -> None:
        url = reverse("common:communities_delete_municipal", args=[2])
        self.assertEqual(url, "/communities/municipal/2/delete/")
        self.assertIs(resolve(url).func, communities_delete_municipal)
