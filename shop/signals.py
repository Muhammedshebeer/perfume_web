from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import Product, ProductImage

def delete_file(file_field):
    if file_field and file_field.name:
        storage, name = file_field.storage, file_field.name
        # Keep other database records independent; unique filenames prevent collisions.
        transaction.on_commit(lambda: storage.delete(name))

@receiver(post_delete, sender=Product)
def cleanup_product(sender,instance,**kwargs):
    delete_file(instance.image)

@receiver(post_delete, sender=ProductImage)
def cleanup_gallery(sender,instance,**kwargs):
    delete_file(instance.image)
