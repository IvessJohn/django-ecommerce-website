"""Define custom signals."""
from django.db.models.signals import post_save  # Connect via a connection command
from django.dispatch import receiver  # Connect via a decorator
from django.contrib.auth.models import User, Group

from .models import Customer

# @receiver(post_save, sender=User) # An alternative to running post_save() after
                                    # the method
def customer_create(sender, instance, created, **kwargs):
    """Create a customer tied to the user that has just been created (registered)."""
    if created:
        Customer.objects.create(
            user=instance,
            name=instance.username,
            email=instance.email,
        )

        # print(
        #    f"""customer_create() method has been successfully called!
        #    A Customer profile for the user {instance.username} has been created!
        #    """)


post_save.connect(customer_create, sender=User)
