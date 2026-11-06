from rest_framework.test import APITestCase


from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from profiles_app.models import Profile
from .models import Order


class OrderAPITestBase(APITestCase):
    def setUp(self):
        ''' Create shared users, profiles, an offer, and an offer detail for order tests. '''
        self.customer_user = User.objects.create_user(
            username="customer",
            password="TestPassword123",
        )
        Profile.objects.create(user=self.customer_user, type="customer")

        self.business_user = User.objects.create_user(
            username="business",
            password="TestPassword123",
        )
        Profile.objects.create(user=self.business_user, type="business")

        self.other_user = User.objects.create_user(
            username="other_customer",
            password="TestPassword123",
        )
        Profile.objects.create(user=self.other_user, type="customer")

        self.offer = Offer.objects.create(
            user=self.business_user,
            title="Design offer",
            description="A test offer.",
        )
        self.offer_detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Design",
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=["Logo"],
            offer_type="basic",
        )
        self.url = reverse("orders")  # Reuse the orders URL in every test.

    def create_order(self, customer):
        ''' Create and return an order for the given customer. '''
        return Order.objects.create(  # Create an order for the given customer.
            customer_user=customer,
            business_user=self.business_user,
            title=self.offer_detail.title,
            revisions=self.offer_detail.revisions,
            delivery_time_in_days=self.offer_detail.delivery_time_in_days,
            price=self.offer_detail.price,
            features=self.offer_detail.features,
            offer_type=self.offer_detail.offer_type,
        )


class OrderListTest(OrderAPITestBase):
    def test_customer_sees_only_own_orders(self):
        ''' Verify that customers can only retrieve their own orders. '''
        own_order = self.create_order(self.customer_user)
        self.create_order(self.other_user)  # This order must remain hidden.
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_order.id)

    def test_business_user_sees_own_orders(self):
        ''' Verify that business users can retrieve orders associated with them. '''
        order = self.create_order(self.customer_user)
        self.client.force_authenticate(user=self.business_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], order.id)

    def test_unrelated_user_sees_no_orders(self):
        ''' Verify that users cannot retrieve orders they are not involved in. '''
        self.create_order(self.customer_user)
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])  # Unrelated orders must remain hidden.

    def test_get_requires_authentication(self):
        ''' Verify that unauthenticated users cannot retrieve orders. '''
        response = self.client.get(self.url)  # No user is authenticated.

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderCreateTest(OrderAPITestBase):
    def test_customer_can_create_three_orders(self):
        ''' Verify that three POST requests create three distinct customer orders. '''
        self.client.force_authenticate(user=self.customer_user)
        data = {"offer_detail_id": self.offer_detail.id}
        order_ids = []

        for request_number in range(1, 4):
            with self.subTest(request_number=request_number):
                response = self.client.post(self.url, data, format="json")

                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                order = Order.objects.get(id=response.data["id"])
                self.assertEqual(order.customer_user, self.customer_user)
                self.assertEqual(order.business_user, self.business_user)
                self.assertEqual(order.status, "in_progress")
                self.assertEqual(response.data["customer_user"], self.customer_user.id)
                self.assertEqual(response.data["business_user"], self.business_user.id)
                self.assertEqual(response.data["status"], "in_progress")
                order_ids.append(order.id)

        self.assertEqual(len(set(order_ids)), 3)
        self.assertEqual(Order.objects.count(), 3)

    def test_customer_can_create_order(self):
        ''' Verify that customers can create orders with the selected offer detail data. '''
        self.client.force_authenticate(user=self.customer_user)
        data = {"offer_detail_id": self.offer_detail.id}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)  # Check actual database creation.
        order = Order.objects.get()
        self.assertEqual(response.data["id"], order.id)
        self.assertEqual(order.customer_user, self.customer_user)
        self.assertEqual(order.business_user, self.business_user)
        self.assertEqual(order.title, self.offer_detail.title)
        self.assertEqual(order.revisions, self.offer_detail.revisions)
        self.assertEqual(
            order.delivery_time_in_days,
            self.offer_detail.delivery_time_in_days,
        )
        self.assertEqual(order.price, self.offer_detail.price)
        self.assertEqual(order.features, self.offer_detail.features)
        self.assertEqual(order.offer_type, self.offer_detail.offer_type)
        self.assertEqual(order.status, "in_progress")

    def test_business_user_cannot_create_order(self):
        ''' Verify that business users cannot create orders. '''
        self.client.force_authenticate(user=self.business_user)
        data = {"offer_detail_id": self.offer_detail.id}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 0)  # No order should be created.

    def test_post_requires_authentication(self):
        ''' Verify that unauthenticated users cannot create orders. '''
        data = {"offer_detail_id": self.offer_detail.id}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)

    def test_missing_offer_detail_id(self):
        ''' Verify that order creation requires an offer detail ID. '''
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("offer_detail_id", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_invalid_offer_detail_id(self):
        ''' Verify that an invalid offer detail ID is rejected. '''
        self.client.force_authenticate(user=self.customer_user)
        data = {"offer_detail_id": "invalid"}  # The ID must be an integer.

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_offer_detail_not_found(self):
        ''' Verify that a nonexistent offer detail ID returns HTTP 404. '''
        self.client.force_authenticate(user=self.customer_user)
        missing_id = self.offer_detail.id
        self.offer_detail.delete()  # Ensure this ID no longer exists.

        response = self.client.post(
            self.url,
            {"offer_detail_id": missing_id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Order.objects.count(), 0)


class OrderUpdateTest(OrderAPITestBase):
    def setUp(self):
        super().setUp()
        self.order = self.create_order(self.customer_user)
        self.url = reverse("order-status", kwargs={"id": self.order.id})

    def test_business_user_can_update_order_status(self):
        ''' Verify that the assigned business user can update the status. '''
        self.client.force_authenticate(user=self.business_user)
        created_at = self.order.created_at

        response = self.client.patch(
            self.url, {"status": "completed"}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")
        self.assertEqual(self.order.created_at, created_at)
        self.assertEqual(response.data["id"], self.order.id)
        self.assertEqual(response.data["status"], "completed")

    def test_customer_cannot_update_order_status(self):
        ''' Verify that a customer cannot update an order's status. '''
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.patch(
            self.url, {"status": "completed"}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_unrelated_business_user_cannot_update_order_status(self):
        ''' Verify that business users cannot update another business user's order. '''
        other_business_user = User.objects.create_user(
            username="other_business", password="TestPassword123",
        )
        Profile.objects.create(user=other_business_user, type="business")
        self.client.force_authenticate(user=other_business_user)

        response = self.client.patch(
            self.url, {"status": "completed"}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_patch_requires_authentication(self):
        ''' Verify that unauthenticated status updates are rejected. '''
        response = self.client.patch(
            self.url, {"status": "completed"}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_invalid_status_is_rejected(self):
        ''' Verify that an unsupported status returns HTTP 400. '''
        self.client.force_authenticate(user=self.business_user)

        response = self.client.patch(
            self.url, {"status": "invalid"}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_unexpected_fields_are_rejected(self):
        ''' Verify that extra fields prevent the entire status update. '''
        self.client.force_authenticate(user=self.business_user)
        original_title = self.order.title

        response = self.client.patch(
            self.url,
            {"status": "completed", "title": "Changed title"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")
        self.assertEqual(self.order.title, original_title)

    def test_missing_status_is_rejected(self):
        ''' Verify that even a partial update requires a status. '''
        self.client.force_authenticate(user=self.business_user)

        response = self.client.patch(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")

    def test_nonexistent_order_returns_404(self):
        ''' Verify that an authorized business user receives HTTP 404 for a missing order. '''
        self.client.force_authenticate(user=self.business_user)
        self.order.delete()

        response = self.client.patch(
            self.url, {"status": "completed"}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_order_returns_404_for_all_authenticated_roles(self):
        ''' Resolve missing orders before checking the user's profile or role. '''
        user_without_profile = User.objects.create_user(username="no_profile")
        self.order.delete()

        for user in (self.customer_user, self.business_user, user_without_profile):
            with self.subTest(username=user.username):
                self.client.force_authenticate(user=user)

                response = self.client.patch(
                    self.url, {"status": "completed"}, format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_assigned_user_requires_business_profile(self):
        ''' Order ownership alone must not allow users without a business profile. '''
        self.client.force_authenticate(user=self.business_user)
        profile = self.business_user.profile
        profile.type = "customer"
        profile.save()

        response = self.client.patch(
            self.url, {"status": "completed"}, format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "in_progress")


class OrderDeleteTest(OrderAPITestBase):
    def test_staff_user_can_delete_order(self):
        ''' Verify that staff can delete an order and receive an empty HTTP 204 response. '''
        staff_user = User.objects.create_user(
            username="staff", password="TestPassword123", is_staff=True,
        )
        order = self.create_order(self.customer_user)
        other_order = self.create_order(self.other_user)
        self.client.force_authenticate(user=staff_user)
        url = reverse("order-status", kwargs={"id": order.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Order.objects.filter(id=order.id).exists())
        self.assertTrue(Order.objects.filter(id=other_order.id).exists())


class OrderCountTest(OrderAPITestBase):
    def setUp(self):
        super().setUp()
        self.url = f"/api/order-count/{self.business_user.id}/"

    def test_counts_only_matching_orders_for_requested_business_user(self):
        ''' Count only the requested business user's orders with the required status. '''
        for order_status in ("in_progress", "in_progress", "completed", "completed", "cancelled"):
            order = self.create_order(self.customer_user)
            order.status = order_status
            order.save()

        other_business = User.objects.create_user(username="other_business")
        Profile.objects.create(user=other_business, type="business")
        other_order = self.create_order(self.customer_user)
        other_order.business_user = other_business
        other_order.status = "in_progress"
        other_order.save()

        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"order_count": 2})

    def test_returns_zero_without_orders(self):
        ''' Return zero for an existing business user without orders. '''
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"order_count": 0})

    def test_returns_zero_when_no_orders_have_required_status(self):
        ''' Return zero when all existing orders have a different status. '''
        order = self.create_order(self.customer_user)
        order.status = "cancelled"
        order.save()
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"order_count": 0})

    def test_business_user_can_retrieve_count(self):
        ''' Allow authenticated business users to retrieve the count. '''
        self.client.force_authenticate(user=self.business_user)
        url = f"/api/order-count/{self.business_user.id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"order_count": 0})

    def test_requires_authentication(self):
        ''' Reject requests without authentication. '''
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_business_user_returns_404(self):
        ''' Return HTTP 404 when the requested user does not exist. '''
        missing_id = max(User.objects.values_list("id", flat=True)) + 1
        self.client.force_authenticate(user=self.customer_user)
        url = f"/api/order-count/{missing_id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_id_returns_404(self):
        ''' Return HTTP 404 when the requested user has a customer profile. '''
        self.client.force_authenticate(user=self.business_user)
        url = f"/api/order-count/{self.customer_user.id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_without_profile_returns_404(self):
        ''' Return HTTP 404 when the requested user has no profile. '''
        user_without_profile = User.objects.create_user(username="no_profile")
        self.client.force_authenticate(user=self.customer_user)
        url = f"/api/order-count/{user_without_profile.id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CompletedOrderCountTest(OrderAPITestBase):
    def setUp(self):
        super().setUp()
        self.url = f"/api/completed-order-count/{self.business_user.id}/"

    def test_counts_only_matching_orders_for_requested_business_user(self):
        ''' Count only the requested business user's orders with the required status. '''
        for order_status in ("in_progress", "in_progress", "completed", "completed", "cancelled"):
            order = self.create_order(self.customer_user)
            order.status = order_status
            order.save()

        other_business = User.objects.create_user(username="other_business")
        Profile.objects.create(user=other_business, type="business")
        other_order = self.create_order(self.customer_user)
        other_order.business_user = other_business
        other_order.status = "completed"
        other_order.save()

        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"completed_order_count": 2})

    def test_returns_zero_without_orders(self):
        ''' Return zero for an existing business user without orders. '''
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"completed_order_count": 0})

    def test_returns_zero_when_no_orders_have_required_status(self):
        ''' Return zero when all existing orders have a different status. '''
        order = self.create_order(self.customer_user)
        order.status = "cancelled"
        order.save()
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"completed_order_count": 0})

    def test_business_user_can_retrieve_count(self):
        ''' Allow authenticated business users to retrieve the count. '''
        self.client.force_authenticate(user=self.business_user)
        url = f"/api/completed-order-count/{self.business_user.id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"completed_order_count": 0})

    def test_requires_authentication(self):
        ''' Reject requests without authentication. '''
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_business_user_returns_404(self):
        ''' Return HTTP 404 when the requested user does not exist. '''
        missing_id = max(User.objects.values_list("id", flat=True)) + 1
        self.client.force_authenticate(user=self.customer_user)
        url = f"/api/completed-order-count/{missing_id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_id_returns_404(self):
        ''' Return HTTP 404 when the requested user has a customer profile. '''
        self.client.force_authenticate(user=self.business_user)
        url = f"/api/completed-order-count/{self.customer_user.id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_without_profile_returns_404(self):
        ''' Return HTTP 404 when the requested user has no profile. '''
        user_without_profile = User.objects.create_user(username="no_profile")
        self.client.force_authenticate(user=self.customer_user)
        url = f"/api/completed-order-count/{user_without_profile.id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

