from __future__ import unicode_literals
from ..models import Store
from ...settings import bazaar_settings, import_from_string


class StoresLoader(object):

    store_managers = {}

    def __init__(self):
        for store_slug, store_manager in bazaar_settings.STORES.items():
            self.store_managers.update({store_slug: import_from_string(store_manager, "Store Manager")()})

    def get_store_manager(self, store_slug):
        try:
            return self.store_managers[store_slug]
        except KeyError:
            raise StoresLoaderException("Cannot find a store manager for slug: %s!" % store_slug)

    def get_all_store_managers(self):
        return self.store_managers.values()


stores_loader = StoresLoader()


def create_stores(app, created_models, verbosity, interactive, db, **kwargs):
    for store_slug, store_manager in stores_loader.store_managers.items():

        if verbosity >= 2:
            print("Creating %s Store object" % store_manager.get_store_name())

        store = Store(
            slug=store_slug,
            name=store_manager.get_store_name(),
            url=store_manager.get_store_url()
        )
        try:
            store.save(using=db)
        except Exception:
            if verbosity >= 2:
                print("Store %s already exists" % store_manager.get_store_name())


class StoresLoaderException(Exception):
    pass