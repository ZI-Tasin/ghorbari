from django.contrib import admin
from .models import FlatListing, GroupFormationPost, ListingImage


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(FlatListing)
class FlatListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'creator', 'rent_amount', 'size', 'created_at')
    list_filter = ('has_elevator', 'created_at')
    search_fields = ('address', 'description', 'creator__username')
    inlines = [ListingImageInline]
    readonly_fields = ('creator', 'created_at', 'updated_at')


@admin.register(GroupFormationPost)
class GroupFormationPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'size', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('description', 'creator__username')
    inlines = [ListingImageInline]
    readonly_fields = ('creator', 'created_at', 'updated_at')


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'uploaded_at')
    list_filter = ('uploaded_at',)
    raw_id_fields = ('listing',)

