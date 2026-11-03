from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile
from .models import Review


class ReviewAPITestBase(APITestCase):
    def setUp(self):
        ''' Create customers and business users shared by review endpoint tests. '''
        self.customer = User.objects.create_user(username="customer")
        self.other_customer = User.objects.create_user(username="other_customer")
        self.business = User.objects.create_user(username="business")
        self.other_business = User.objects.create_user(username="other_business")
        for user, profile_type in (
            (self.customer, "customer"),
            (self.other_customer, "customer"),
            (self.business, "business"),
            (self.other_business, "business"),
        ):
            Profile.objects.create(user=user, type=profile_type)
        self.url = reverse("reviews")

    def create_review(self, reviewer=None, business=None, rating=4):
        return Review.objects.create(
            reviewer=reviewer or self.customer,
            business_user=business or self.business,
            rating=rating,
            description="Professional service.",
        )

    def detail_url(self, review_id):
        return reverse("review-details", kwargs={"id": review_id})


class ReviewListTest(ReviewAPITestBase):
    def setUp(self):
        super().setUp()
        self.first = self.create_review(rating=5)
        self.second = self.create_review(reviewer=self.other_customer, rating=1)
        self.third = self.create_review(business=self.other_business, rating=3)
        self.client.force_authenticate(user=self.customer)

    def test_authenticated_users_can_list_all_reviews(self):
        ''' Customers and business users can read reviews, including other users' reviews. '''
        for user in (self.customer, self.business):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertCountEqual(
                    [item["id"] for item in response.data],
                    [self.first.id, self.second.id, self.third.id],
                )
                self.assertEqual(set(response.data[0]), {
                    "id", "business_user", "reviewer", "rating", "description",
                    "created_at", "updated_at",
                })

    def test_filter_by_business_user(self):
        response = self.client.get(self.url, {"business_user_id": self.business.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [item["id"] for item in response.data], [self.first.id, self.second.id],
        )

    def test_filter_by_reviewer(self):
        response = self.client.get(self.url, {"reviewer_id": self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            [item["id"] for item in response.data], [self.first.id, self.third.id],
        )

    def test_filters_can_be_combined(self):
        response = self.client.get(self.url, {
            "business_user_id": self.business.id, "reviewer_id": self.customer.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [self.first.id])

    def test_filter_without_matches_returns_empty_list(self):
        for field in ("business_user_id", "reviewer_id"):
            with self.subTest(field=field):
                response = self.client.get(self.url, {field: 0})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data, [])

    def test_invalid_filter_values_return_400(self):
        for field in ("business_user_id", "reviewer_id"):
            for value in ("abc", "1.5", ""):
                with self.subTest(field=field, value=value):
                    response = self.client.get(self.url, {field: value})
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                    self.assertIn(field, response.data)

    def test_order_by_rating(self):
        response = self.client.get(self.url, {"ordering": "rating"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.data],
            [self.second.id, self.third.id, self.first.id],
        )

    def test_order_by_updated_at(self):
        ''' Use explicit timestamps so the result does not depend on execution speed. '''
        now = timezone.now()
        Review.objects.filter(id=self.third.id).update(updated_at=now - timedelta(days=2))
        Review.objects.filter(id=self.first.id).update(updated_at=now - timedelta(days=1))
        Review.objects.filter(id=self.second.id).update(updated_at=now)
        response = self.client.get(self.url, {"ordering": "updated_at"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["id"] for item in response.data],
            [self.third.id, self.first.id, self.second.id],
        )

    def test_get_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewCreateTest(ReviewAPITestBase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.customer)
        self.payload = {
            "business_user": self.business.id,
            "rating": 4,
            "description": "Excellent service.",
        }

    def test_customer_can_create_review(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get()
        self.assertEqual(review.reviewer, self.customer)
        self.assertEqual(review.business_user, self.business)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.description, self.payload["description"])
        self.assertEqual(response.data["id"], review.id)
        self.assertEqual(response.data["reviewer"], self.customer.id)
        self.assertEqual(set(response.data), {
            "id", "business_user", "reviewer", "rating", "description",
            "created_at", "updated_at",
        })

    def test_reviewer_cannot_be_impersonated(self):
        payload = {**self.payload, "reviewer": self.other_customer.id}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.get().reviewer, self.customer)

    def test_duplicate_review_is_rejected(self):
        original = self.create_review()
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Review.objects.count(), 1)
        original.refresh_from_db()
        self.assertEqual(original.description, "Professional service.")

    def test_customer_can_review_another_business(self):
        self.create_review()
        payload = {**self.payload, "business_user": self.other_business.id}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_other_customer_can_review_same_business(self):
        self.create_review()
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_business_and_users_without_profiles_cannot_create_reviews(self):
        no_profile = User.objects.create_user(username="no_profile")
        for user in (self.business, no_profile):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.post(self.url, self.payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(Review.objects.count(), 0)

    def test_invalid_business_user_is_rejected(self):
        no_profile = User.objects.create_user(username="no_profile")
        missing_id = no_profile.id + 1
        for user_id in (self.customer.id, no_profile.id, missing_id):
            with self.subTest(user_id=user_id):
                payload = {**self.payload, "business_user": user_id}
                response = self.client.post(self.url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("business_user", response.data)
                self.assertEqual(Review.objects.count(), 0)

    def test_invalid_rating_is_rejected(self):
        for rating in (-1, 6, "invalid", 2.5):
            with self.subTest(rating=rating):
                response = self.client.post(
                    self.url, {**self.payload, "rating": rating}, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("rating", response.data)
                self.assertEqual(Review.objects.count(), 0)

    def test_required_fields(self):
        for field in self.payload:
            with self.subTest(field=field):
                payload = self.payload.copy()
                del payload[field]
                response = self.client.post(self.url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)
                self.assertEqual(Review.objects.count(), 0)

    def test_post_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), 0)


class ReviewUpdateTest(ReviewAPITestBase):
    def setUp(self):
        super().setUp()
        self.review = self.create_review()
        self.url = self.detail_url(self.review.id)
        self.client.force_authenticate(user=self.customer)

    def test_owner_can_update_review_with_full_response(self):
        created_at = self.review.created_at
        previous_update = timezone.now() - timedelta(days=1)
        Review.objects.filter(id=self.review.id).update(updated_at=previous_update)
        response = self.client.patch(
            self.url, {"rating": 5, "description": "Even better!"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.description, "Even better!")
        self.assertEqual(self.review.created_at, created_at)
        self.assertGreater(self.review.updated_at, previous_update)
        self.assertEqual(response.data["id"], self.review.id)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["description"], "Even better!")
        self.assertEqual(set(response.data), {
            "id", "business_user", "reviewer", "rating", "description",
            "created_at", "updated_at",
        })

    def test_each_editable_field_can_be_updated_individually(self):
        for payload in ({"rating": 5}, {"description": "Updated text"}):
            with self.subTest(payload=payload):
                before_rating = self.review.rating
                before_description = self.review.description
                response = self.client.patch(self.url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.review.refresh_from_db()
                self.assertEqual(self.review.rating, payload.get("rating", before_rating))
                self.assertEqual(
                    self.review.description, payload.get("description", before_description),
                )

    def test_other_users_cannot_update_review(self):
        for user in (self.other_customer, self.business):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.patch(self.url, {"rating": 5}, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.review.refresh_from_db()
                self.assertEqual(self.review.rating, 4)

    def test_forbidden_fields_are_rejected(self):
        for field, value in (
            ("business_user", self.other_business.id),
            ("reviewer", self.other_customer.id),
            ("id", 999), ("created_at", "2020-01-01T00:00:00Z"),
            ("updated_at", "2020-01-01T00:00:00Z"), ("unknown", "value"),
        ):
            with self.subTest(field=field):
                response = self.client.patch(
                    self.url, {"rating": 5, field: value}, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.review.refresh_from_db()
                self.assertEqual(self.review.rating, 4)
                self.assertEqual(self.review.business_user, self.business)
                self.assertEqual(self.review.reviewer, self.customer)

    def test_invalid_rating_is_rejected(self):
        for rating in (-1, 6, "invalid", 2.5):
            with self.subTest(rating=rating):
                response = self.client.patch(self.url, {"rating": rating}, format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.review.refresh_from_db()
                self.assertEqual(self.review.rating, 4)

    def test_missing_review_returns_404(self):
        self.review.delete()
        response = self.client.patch(self.url, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url, {"rating": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)


class ReviewDeleteTest(ReviewAPITestBase):
    def setUp(self):
        super().setUp()
        self.review = self.create_review()
        self.url = self.detail_url(self.review.id)
        self.client.force_authenticate(user=self.customer)

    def test_owner_can_delete_review(self):
        other_review = self.create_review(reviewer=self.other_customer)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
        self.assertTrue(Review.objects.filter(id=other_review.id).exists())

    def test_other_users_cannot_delete_review(self):
        for user in (self.other_customer, self.business):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.delete(self.url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertTrue(Review.objects.filter(id=self.review.id).exists())

    def test_missing_review_returns_404(self):
        self.review.delete()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
