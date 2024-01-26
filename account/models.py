from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import  BaseUserManager

class CustomUser(AbstractUser):
    class USER_ROLES(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        JUDGE = 'judge', _('Judge')
        STUDENT = 'student', _('Student')
        
    class Gender(models.TextChoices):
        MALE = 'male'
        FEMALE = 'female'
        OTHER = 'other'
    
    class BRANCH(models.TextChoices):
        CSE = 'cse', _('Computer Science')
        ECE = 'ece', _('Electronics and Communication')
        EEE = 'eee', _('Electrical and Electronics')
        MECH = 'mech', _('Mechanical')
        CIVIL = 'civil', _('Civil')
        CHEM = 'chem', _('Chemical')
        BIOTECH = 'biotech', _('Biotechnology')
        IT = 'it', _('Information Technology')
        MCA = 'mca', _('MCA')
        MTECH = 'mtech', _('MTECH')
        MBA = 'mba', _('MBA')
        OTHER = 'other', _('Other')
        
    
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    role = models.CharField(max_length=20, choices=USER_ROLES.choices,default=USER_ROLES.STUDENT)
    gender = models.CharField(max_length=20, choices=Gender.choices,default=Gender.MALE)
    branch = models.CharField(max_length=20, choices=BRANCH.choices,default=BRANCH.CSE)
    mobile = models.CharField(max_length=10)
    image = models.ImageField(upload_to=f'profile/user/',default = 'user.png',blank=True)
    batch_year = models.IntegerField(null=True,blank=True)
    otp = models.IntegerField(null=True,blank=True)
    
    REQUIRED_FIELDS = ['first_name','last_name','role','mobile','username']
    USERNAME_FIELD = 'email'
      
    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['-date_joined']
        