from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField


# Create your models here.

STATES = (
    ("Province 1","Province 1"),
    ("Province 2","Province 2"),
    ("Bagmati","Bagmati"),
    ("Gandaki","Gandaki"),
    ("Lumbini","Lumbini"),
    ("Karnali","Karnali"),
    ("Sudur Paschim","Sudur Paschim")
)

SECONDARY_BUSINESS_CHOICES = (
    ("Importer", "Importer"),
    ("Exporter", "Exporter"),
    ("Manufacturer", "Manufacturer"),
    ("Wholesaler/Dealer/Distributor", "Wholesaler/Dealer/Distributor"),
    ("Retailer", "Retailer"),
)


class Supplier(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE) #Request.user
    # not editable
    name = models.CharField(max_length=50) #Name of the user who filled 'become a seller page'
    verified = models.BooleanField(default=False) #Verified the PAN?
    # telephone number
    phone_number = models.PositiveIntegerField(null=True,blank=True) #Strictly only Landline
    
    # internal use mobile number, should not be editable
    # make this one to one with profile
    mobile_number = models.BigIntegerField() #Phone number of the user creating the account

    # not editable
    company_name = models.CharField(max_length=200, unique=True)
    # not editable
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True) 
    establishment_year = models.CharField(max_length=10)
    ceo_name = models.CharField(max_length=100)
    
    # user shouldn't be able to edit this email field
    email = models.CharField(max_length=150)
    
    website = models.CharField(max_length=150)
    
    # details that can be seen by retailer or public
    contact_name = models.CharField(max_length=50)
    contact_phone = models.BigIntegerField()
    contact_email = models.CharField(max_length=50)

    state = models.CharField(max_length=50,choices=STATES)
    address1 = models.CharField(max_length=150, default='Nepal,Nepal')
    address2 = models.CharField(max_length=150, null=True,blank=True)

    exim = models.CharField(max_length=20, null=True, blank=True)
    pan = models.CharField(max_length=20, null=True, blank=True)
    vat = models.CharField(max_length=20, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    
    def get_image_path(self, filename):
        path = ''.join(['suppliers/',str(self.id),'/',filename])
        return path

    profile_picture = models.ImageField(upload_to=get_image_path, default='default.jpg', blank=True, null=True)
    qr_code = models.ImageField(upload_to=get_image_path, default='default.jpg', blank=True, null=True)
    bio = models.CharField(max_length=250, blank=True, null=True)
    secondary_business = MultiSelectField(choices=SECONDARY_BUSINESS_CHOICES, max_choices = 3, default='Wholesaler/Dealer/Distributor')


    def __str__(self):
        return self.company_name

    
class Company(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    establishment_year = models.CharField(max_length=10)
    ceo_name = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    website = models.CharField(max_length=150)

    def __str__(self) -> str:
        return self.company_name


class CompanyAddress(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    pin_code = models.CharField(max_length=15)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    building_number = models.CharField(max_length=10, null=True, blank=True)
    street = models.CharField(max_length=20, null=True, blank=True)
    locality = models.CharField(max_length=30, null=True, blank=True)
    landmark = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self) -> str:
        return self.company.name


class CompanyStatutory(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    exim = models.CharField(max_length=20)
    pan = models.CharField(max_length=20)
    vat = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.company.name
