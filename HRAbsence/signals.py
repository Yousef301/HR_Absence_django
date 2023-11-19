# signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from HRAbsence.models import User, BusinessGroup


@receiver(post_save, sender=User)
def assign_to_group(sender, instance, created, **kwargs):
    if created:
        group_name = instance._role
        business_id = instance._business
        try:
            group_business = BusinessGroup.objects.get(business_id=business_id)
            group = Group.objects.get(id=group_business.group_id, name=group_name)
            instance.groups.add(group)
            print("Added__________________________________")

        except BusinessGroup.DoesNotExist:
            print(f"No object found with ID {business_id}")
