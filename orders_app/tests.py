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