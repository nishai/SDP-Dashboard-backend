from typing import Type
from django.contrib import admin
from django.db.models import Model


def admin_site_register(cls: Type[Model]):
    """
    Annotate your model classes to register them.
    Normally this is done manually for each model in an 'admin.py' file inside each app... but I keep forgetting...
    eg.

    @admin_site_register
    class MyModel(Model):
        pass

    :param cls: The model to register
    :return: The same cls as the input arg, we do not modify it.
    """
    admin.site.register(cls)
    return cls
