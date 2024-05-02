from itertools import count
import secrets
import uuid
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
# import uuid
from django.contrib.postgres.fields import ArrayField
import random
import string
import datetime
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
import graphene
from django.contrib.auth.models import AbstractUser, Group, Permission
from core.settings import AUTH_USER_MODEL
from django.db.models.signals import pre_save , post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.db.models import F
from collections import Counter
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_email

phone_regex = RegexValidator(
    regex=r"^\d{10}", message="Phone number must be 10 digits only."
)
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)

        user.set_password(password)

        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff being True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(email=email, password=password, **extra_fields)


class Userkap(AbstractUser):
    email = models.CharField(max_length=80, unique=True)
    PRIORITY_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),

)   
    usertypes = (
    ('Student', 'Student'),
    ('Institute', 'Institute'),
    ('Other', 'Other'),
    

)
    # boards = (('West Bengal Board of Secondary Education (WBBSE)','West Bengal Board of Secondary Education (WBBSE)'),('West Bengal Council for Higher Secondary Education (WBCHSE)','West Bengal Council for Higher Secondary Education (WBCHSE)'),('Karnataka School Examination and Assessment Board (KSEAB)','Karnataka School Examination and Assessment Board (KSEAB)'),('Goa Board of Secondary and Higher Secondary Education (GBSHSE)','Goa Board of Secondary and Higher Secondary Education (GBSHSE)'),('Directorate of Higher Secondary Education, Kerala(DHSE)','Directorate of Higher Secondary Education, Kerala(DHSE)'),('DGE, Tamil Nadu','DGE, Tamil Nadu'),('Jharkhand Academic Council(JAC)','Jharkhand Academic Council(JAC)'),
    #           ('Board of Intermediate Education, Andhra Pradesh (BIEAP)','Board of Intermediate Education, Andhra Pradesh (BIEAP)'),('Board of Secondary Education, Assam (SEBA)','Board of Secondary Education, Assam (SEBA)'),('Tripura Board of Secondary Education (TBSE)','Tripura Board of Secondary Education (TBSE)'),('Council of Higher Secondary Education, Odisha','Council of Higher Secondary Education, Odisha'),('Chhattisgarh Board of Secondary Education (CGBSE)','Chhattisgarh Board of Secondary Education (CGBSE)'),('Telangana State Board of Intermediate Education (TSBIE)','Telangana State Board of Intermediate Education (TSBIE)'),('Board of Secondary Education, Odisha','Board of Secondary Education, Odisha'),('Board of Secondary Education, Madhya Pradesh (MPBSE)','Board of Secondary Education, Madhya Pradesh (MPBSE)'),('Board of School Education, Haryana (HBSE)','Board of School Education, Haryana (HBSE)'),('Bihar School Examination Board (BSEB)','Bihar School Examination Board (BSEB)'),('Nagaland Board of School Education (NBSE)','Nagaland Board of School Education (NBSE)'),('Council of Higher Secondary Education, Manipur (COHSEM)','Council of Higher Secondary Education, Manipur (COHSEM)'),('Board of Secondary Education, Rajasthan (RBSE)','Board of Secondary Education, Rajasthan (RBSE)'),('Maharashtra State Board of Secondary and Higher Secondary Education (MSBSHSE)','Maharashtra State Board of Secondary and Higher Secondary Education (MSBSHSE)'),('Uttarakhand Board of School Education (UBSE)','Uttarakhand Board of School Education (UBSE)'),('Assam Higher Secondary Education Council (AHSEC)','Assam Higher Secondary Education Council (AHSEC)'),('Mizoram Board of School Education (MBSE)','Mizoram Board of School Education (MBSE)'),('Himachal Pradesh Board of School Education (HPBOSE)','Himachal Pradesh Board of School Education (HPBOSE)'),('Board of Secondary Education, Manipur (BSEM)','Board of Secondary Education, Manipur (BSEM)')('Meghalaya Board of School Education (MBOSE)','Meghalaya Board of School Education (MBOSE)'),('Jammu and Kashmir Board of School Education (JKBOSE)','Jammu and Kashmir Board of School Education (JKBOSE)'),)
    username = models.CharField(max_length=45)
    custom_id = models.CharField(max_length=8,blank = True,editable=False,unique=True)
    date_of_birth = models.DateField(null=True)
    
    
    objects = CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    groups = models.ManyToManyField(
        Group,
        related_name="userkap_groups",  # unique related_name
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups"
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="userkap_user_permissions",  # unique related_name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions"
    )

    def __str__(self):
        return self.username

@receiver(pre_save, sender=Userkap)
def generate_custom_id(sender, instance, **kwargs):
    # Check if custom_id is not set
    if not instance.custom_id:
        for i in count(start=1):
            # Format the count as a 4-digit string
            formatted_count = f"{i:05}"
            custom_id = f"12{formatted_count}"
            if not Userkap.objects.filter(custom_id=custom_id).exists():

                instance.custom_id = custom_id
                break

class FriendRequest(models.Model):
    sender = models.ForeignKey(Userkap, on_delete=models.CASCADE, related_name='sent_friend_requests',editable=False)
    receiver = models.ForeignKey(Userkap, on_delete=models.CASCADE, related_name='received_friend_requests')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"

    def decline(self):
        self.delete()  

