from django.db import models
from django.conf import settings


class Listing(models.Model):
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)ss_created'
    )
    description = models.TextField()
    size = models.PositiveIntegerField(help_text="Number of people")
    contact_number = models.CharField(max_length=11, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def listing_type(self):
        return self.__class__.__name__

    def __str__(self):
        creator_username = self.creator.username if self.creator else 'deleted_user'
        desc_snippet = (self.description[:30] + '...') if self.description and len(self.description) > 30 else self.description
        return f"{self.listing_type} {self.id} by {creator_username} (Desc: {desc_snippet})"


class FlatListing(Listing):
    address = models.CharField(max_length=255)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    has_elevator = models.BooleanField(default=False)
    initial_images_finalized = models.BooleanField(default=True)

    def __str__(self):
        creator_username = self.creator.username if self.creator else 'deleted_user'
        return f"Flat {self.id} at {self.address} (Creator: {creator_username})"


class GroupFormationPost(Listing):
    initial_images_finalized = models.BooleanField(default=True)

    def __str__(self):
        creator_username = self.creator.username if self.creator else 'deleted_user'
        desc_snippet = (self.description[:30] + '...') if self.description and len(self.description) > 30 else self.description
        return f"Group Post {self.id} by {creator_username} (Desc: {desc_snippet})"


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='listing_pics/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        listing_identifier = ""
        if hasattr(self.listing, 'flatlisting') and self.listing.flatlisting.address:
            listing_identifier = f"at {self.listing.flatlisting.address}"
        elif hasattr(self.listing, 'groupformationpost'):
             listing_identifier = f"by {self.listing.creator.username}"
        else:
            listing_identifier = str(self.listing.id)

        return f"Image for {self.listing.listing_type} {listing_identifier}"

