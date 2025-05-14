# GhorBari/posts/urls.py
from django.urls import path
from . import views # Your views from posts/views.py

app_name = 'posts'

urlpatterns = [
    # List Views
    path('flats/', views.flat_listing_list, name='flat_listing_list'),
    path('groups/', views.group_post_list, name='group_post_list'),
    
    # Create Views
    path('flats/new/', views.create_flat_listing, name='create_flat_listing'),
    path('groups/new/', views.create_group_post, name='create_group_post'),

    # Detail Views
    path('flats/<int:pk>/', views.flat_listing_detail, name='flat_listing_detail'),
    path('groups/<int:pk>/', views.group_post_detail, name='group_post_detail'),

    # --- SINGLE GENERIC UPLOAD URL ---
    path('listing/<int:pk>/upload-image/', views.upload_listing_image, name='upload_listing_image'),
    
    # --- REMOVE OR COMMENT OUT THESE OLDER, SPECIFIC UPLOAD URLS ---
    # path('listings/flatlisting/<int:pk>/upload_image/', views.upload_listing_image, {'listing_model_name': 'flatlisting'}, name='upload_flat_image'),
    # path('listings/groupformationpost/<int:pk>/upload_image/', views.upload_listing_image, {'listing_model_name': 'groupformationpost'}, name='upload_group_image'),

    # Finalize Initial Images
    path('flats/<int:pk>/finalize-images/', views.finalize_initial_flat_images, name='finalize_initial_flat_images'),
    path('groups/<int:pk>/finalize-images/', views.finalize_initial_group_images, name='finalize_initial_group_images'),

    # Update Views
    path('flats/<int:pk>/edit/', views.update_flat_listing, name='update_flat_listing'),
    path('groups/<int:pk>/edit/', views.update_group_post, name='update_group_post'),

    # Delete Views
    path('flats/<int:pk>/delete/', views.delete_flat_listing, name='delete_flat_listing'),
    path('groups/<int:pk>/delete/', views.delete_group_post, name='delete_group_post'),

    path('listing/image/<int:image_pk>/delete/', views.delete_listing_image, name='delete_listing_image'),
]