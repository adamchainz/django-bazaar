from __future__ import unicode_literals

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ..settings import bazaar_settings

# TODO: this dependency should be optional, maybe based on INSTALLED APPS
from ..warehouse.models import RealGood

@python_2_unicode_compatible
class AbstractGood(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)

    elements = generic.GenericRelation("ProductElement")
    real_goods = generic.GenericRelation(RealGood)

    class Meta:
        abstract = True

    @property
    def stock(self):
        stock = 0
        for rg in self.real_goods.all():
            for movement in rg.movements.all():
                stock += movement.quantity
        return stock

    @property
    def cost(self):
        """
        Defines the cost of the good
        """
        raise NotImplementedError

    def __str__(self):
        return self.name


class PriceListManager(models.Manager):
    use_for_related_fields = True

    def get_default(self):
        """
        Return the default price list instance
        """
        try:
            return self.get_query_set().get(pk=bazaar_settings.DEFAULT_PRICE_LIST_ID)
        except PriceList.DoesNotExist:
            raise ImproperlyConfigured("A default price list must exists. Please create one")


@python_2_unicode_compatible
class PriceList(models.Model):
    name = models.CharField(max_length=100, unique=True)

    objects = PriceListManager()

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price_lists = models.ManyToManyField("PriceList", through="ProductPrice", related_name="products")

    @property
    def price(self):
        """
        The price for the product on the default price list
        """
        # Use .all() to allow access to prefetched queryset
        for product_price in self.prices.all():
            if product_price.price_list_id == bazaar_settings.DEFAULT_PRICE_LIST_ID:
                return product_price.price

        return 0

    @property
    def cost(self):
        """
        The cost of the product as the sum of the costs of its goods
        """
        return sum(element.good.cost * element.quantity for element in self.elements.all())

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductElement(models.Model):
    product = models.ForeignKey(Product, related_name="elements")
    quantity = models.IntegerField(default=1)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    good = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('product', 'content_type', 'object_id')

    def __str__(self):
        return ""


@python_2_unicode_compatible
class ProductPrice(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=bazaar_settings.CURRENCIES)

    product = models.ForeignKey(Product, related_name="prices")
    price_list = models.ForeignKey(PriceList)

    class Meta:
        unique_together = ('product', 'price_list')

    def __str__(self):
        return ""
