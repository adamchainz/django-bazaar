from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from bazaar.listings.models import Listing
from bazaar.settings import bazaar_settings
from ..factories import ProductFactory, UserFactory


class TestListingApi(APITestCase):

    def test_that_listings_api_search_works_on_listing_title(self):
        """
        Make sure that the search works on listing title
        """
        # turn on automatic listing creation on product creation
        old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = True

        #self.client.login(username=self.user.username, password='123456')
        ProductFactory(name='test name')
        ProductFactory(name='another name')
        ProductFactory(name='TeSt')

        response = self.client.get(reverse('listing-list'), {'search': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = old_setting_value

    def test_that_listings_api_search_works_on_listing_title_when_there_are_no_results(self):
        """
        Make sure that the search works on listing title when there are no results
        """
        # turn on automatic listing creation on product creation
        old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = True

        ProductFactory(name='tast name')
        ProductFactory(name='another name')
        ProductFactory(name='TaSt')

        response = self.client.get(reverse('listing-list'), {'search': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = old_setting_value

    def test_that_listings_api_search_works_on_product_title(self):
        """
        Make sure that the search works on the listing's products name
        """
        # turn on automatic listing creation on product creation
        old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = True

        self.assertEqual(Listing.objects.count(), 0)
        ProductFactory(name='test name')
        listing = Listing.objects.all()[0]
        listing.title = 'toast name'

        response = self.client.get(reverse('listing-list'), {'search': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = old_setting_value

    def test_that_listings_api_search_works_on_product_title_when_there_are_no_results(self):
        """
        Make sure that the search works on the listing's products name. No results case.
        """
        # turn on automatic listing creation on product creation
        old_setting_value = bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION
        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = True

        self.assertEqual(Listing.objects.count(), 0)
        ProductFactory(name='test name')
        ProductFactory(name='test name')
        ProductFactory(name='test name')

        response = self.client.get(reverse('listing-list'), {'search': 'tast'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

        bazaar_settings.AUTOMATIC_LISTING_CREATION_ON_PRODUCT_CREATION = old_setting_value
