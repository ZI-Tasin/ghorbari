from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import Http404

from .models import Listing, FlatListing, GroupFormationPost, ListingImage
from .forms import FlatListingForm, GroupFormationForm, ListingImageForm, FlatListingFilterForm


def _is_creator(user, listing):
    return user.is_authenticated and listing.creator == user

def _get_listing_or_404(queryset, pk):
    return get_object_or_404(queryset, pk=pk)


def flat_listing_list(request):
    listings = FlatListing.objects.select_related('creator').prefetch_related('images').order_by('-created_at')
    form = FlatListingFilterForm(request.GET or None)

    if form.is_valid():
        data = form.cleaned_data
        if data.get('min_rent'):
            listings = listings.filter(rent_amount__gte=data['min_rent'])
        if data.get('max_rent'):
            listings = listings.filter(rent_amount__lte=data['max_rent'])
        if data.get('has_elevator') == 'yes':
            listings = listings.filter(has_elevator=True)
        elif data.get('has_elevator') == 'no':
            listings = listings.filter(has_elevator=False)

    paginator = Paginator(listings, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'posts/flat_listing_list.html', {
        'page_obj': page_obj,
        'filter_form': form,
        'listing_type_plural': 'Flats'
    })

def group_post_list(request):
    group_posts_qs = GroupFormationPost.objects.all().order_by('-created_at')
    paginator = Paginator(group_posts_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    is_bracu_student = False
    if request.user.is_authenticated:
        try:
            if request.user.email and request.user.email.endswith('@g.bracu.ac.bd'):
                is_bracu_student = True
        except AttributeError:
            pass

    return render(request, 'posts/group_post_list.html', {
        'page_obj': page_obj,
        'is_bracu_student_for_view': is_bracu_student
    })


@login_required
def create_flat_listing(request):
    form = FlatListingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        flat = form.save(commit=False)
        flat.creator = request.user
        flat.save()
        messages.success(request, "Flat listing created successfully.")
        return redirect('posts:flat_listing_detail', pk=flat.pk)
    else:
        form = FlatListingForm()
    
    return render(request, 'posts/create_listing.html', {
        'form': form,
        'listing_type': 'Flat',
        'form_title': 'Create New Flat Listing'
    })


@login_required
def create_group_post(request):
    form = GroupFormationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.creator = request.user
        post.save()
        messages.success(request, "Group formation post created successfully.")
        return redirect('posts:group_post_detail', pk=post.pk)
    else:
        form = GroupFormationForm()

    return render(request, 'posts/create_listing.html', {
        'form': form,
        'listing_type': 'Group',
        'form_title': 'Create New Group Formation Post'
    })


def flat_listing_detail(request, pk):
    flat = _get_listing_or_404(FlatListing.objects.select_related('creator').prefetch_related('images'), pk=pk)
    is_creator_flag = _is_creator(request.user, flat)
    image_form_instance = None

    if is_creator_flag and not flat.initial_images_finalized:
        image_form_instance = ListingImageForm()
    
    return render(request, 'posts/listing_detail.html', {
        'listing': flat,
        'is_creator': is_creator_flag,
        'listing_type_lower': 'flat',
        'image_upload_form': image_form_instance 
    })


def group_post_detail(request, pk):
    post = _get_listing_or_404(GroupFormationPost.objects.select_related('creator').prefetch_related('images'), pk=pk)
    is_creator_flag = _is_creator(request.user, post)
    image_form_instance = None

    if is_creator_flag and not post.initial_images_finalized:
        image_form_instance = ListingImageForm()

    return render(request, 'posts/listing_detail.html', {
        'listing': post,
        'is_creator': is_creator_flag,
        'listing_type_lower': 'group',
        'image_upload_form': image_form_instance
    })


@login_required
@require_POST
def upload_listing_image(request, pk):
    parent_listing = get_object_or_404(Listing, pk=pk)

    specific_listing_instance = None
    edit_redirect_url_name = None
    detail_redirect_url_name = None

    if hasattr(parent_listing, 'flatlisting'):
        specific_listing_instance = parent_listing.flatlisting
        edit_redirect_url_name = 'posts:update_flat_listing'
        detail_redirect_url_name = 'posts:flat_listing_detail'
    elif hasattr(parent_listing, 'groupformationpost'):
        specific_listing_instance = parent_listing.groupformationpost
        edit_redirect_url_name = 'posts:update_group_post'
        detail_redirect_url_name = 'posts:group_post_detail'
    else:
        messages.error(request, "Unknown listing type for image upload.")
        return redirect('landing_home')

    if not _is_creator(request.user, parent_listing):
        messages.error(request, "You are not authorized to upload images for this listing.")
        return redirect(detail_redirect_url_name, pk=parent_listing.pk)

    if specific_listing_instance and specific_listing_instance.initial_images_finalized:
        pass

    form = ListingImageForm(request.POST, request.FILES)
    if form.is_valid():
        image_instance = form.save(commit=False)
        image_instance.listing = parent_listing
        image_instance.save()
        messages.success(request, "Image uploaded successfully!")
    else:
        error_list = []
        for field, errors_list in form.errors.items():
            for error_item in errors_list:
                if field == '__all__':
                    error_list.append(f"{error_item}")
                else:
                    field_label = form.fields.get(field).label if form.fields.get(field) else field
                    error_list.append(f"{field_label}: {error_item}")
        messages.error(request, f"Error uploading image: {'; '.join(error_list)}")
    
    if edit_redirect_url_name:
        return redirect(edit_redirect_url_name, pk=parent_listing.pk)
    else:
        return redirect('landing_home')

@login_required
@require_POST
def finalize_initial_flat_images(request, pk):
    flat = get_object_or_404(FlatListing, pk=pk)
    if not _is_creator(request.user, flat):
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('posts:flat_listing_detail', pk=pk)
    
    flat.initial_images_finalized = True
    flat.save()
    messages.info(request, "Initial image setup is now complete for this flat listing.")
    return redirect('posts:flat_listing_detail', pk=pk)

@login_required
@require_POST
def finalize_initial_group_images(request, pk):
    gfa_post = get_object_or_404(GroupFormationPost, pk=pk)
    if not _is_creator(request.user, gfa_post):
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('posts:group_post_detail', pk=pk)

    gfa_post.initial_images_finalized = True
    gfa_post.save()
    messages.info(request, "Initial image setup is now complete for this group post.")
    return redirect('posts:group_post_detail', pk=pk)

@login_required
def update_flat_listing(request, pk):
    flat_instance = get_object_or_404(FlatListing, pk=pk)

    if not _is_creator(request.user, flat_instance):
        messages.error(request, "You are not authorized to edit this listing.")
        return redirect('posts:flat_listing_detail', pk=flat_instance.pk)

    if request.method == 'POST':
        text_form = FlatListingForm(request.POST, request.FILES or None, instance=flat_instance)
        if text_form.is_valid():
            text_form.save()
            messages.success(request, "Flat listing details updated successfully.")
            return redirect('posts:flat_listing_detail', pk=flat_instance.pk)
        else:
            messages.error(request, "Please correct the errors in the listing details.")
            image_upload_form_instance = ListingImageForm()
    else:
        text_form = FlatListingForm(instance=flat_instance)
        image_upload_form_instance = ListingImageForm()

    return render(request, 'posts/update_listing_form.html', {
        'form': text_form,
        'listing': flat_instance,
        'image_upload_form': image_upload_form_instance,
        'form_title': f'Edit Listing: {flat_instance.address}'
    })

@login_required
def delete_flat_listing(request, pk):
    instance = get_object_or_404(FlatListing, pk=pk)

    if not _is_creator(request.user, instance):
        messages.error(request, "You are not authorized to delete this listing.")
        return redirect('posts:flat_listing_detail', pk=instance.pk)

    if request.method == 'POST':
        listing_identifier = instance.address
        instance.delete()
        messages.success(request, f"Flat listing '{listing_identifier}' has been deleted.")
        return redirect('posts:flat_listing_list')
    
    return render(request, 'posts/delete_confirm.html', {
        'listing': instance,
        'listing_type_display': 'Flat Listing'
    })

@login_required
def update_group_post(request, pk):
    gfa_post = get_object_or_404(GroupFormationPost, pk=pk)

    if not _is_creator(request.user, gfa_post):
        messages.error(request, "You are not authorized to edit this group post.")
        return redirect('posts:group_post_detail', pk=gfa_post.pk)

    if request.method == 'POST':
        form = GroupFormationForm(request.POST, instance=gfa_post)
        if form.is_valid():
            form.save()
            messages.success(request, "Group formation post updated successfully.")
            return redirect('posts:group_post_detail', pk=gfa_post.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = GroupFormationForm(instance=gfa_post)

    return render(request, 'posts/update_listing_form.html', {
        'form': form,
        'listing': gfa_post,
        'form_title': f'Edit Group Post'
    })

@login_required
def delete_group_post(request, pk):
    gfa_post = get_object_or_404(GroupFormationPost, pk=pk)

    if not _is_creator(request.user, gfa_post):
        messages.error(request, "You are not authorized to delete this group post.")
        return redirect('posts:group_post_detail', pk=gfa_post.pk)

    if request.method == 'POST':
        post_identifier = f"Group Post ID {gfa_post.pk}"
        gfa_post.delete()
        messages.success(request, f"'{post_identifier}' has been deleted.")
        return redirect('posts:group_post_list')
    
    return render(request, 'posts/delete_confirm.html', {
        'listing': gfa_post,
        'listing_type_display': 'Group Formation Post'
    })

@login_required
@require_POST
def delete_listing_image(request, image_pk):
    image_to_delete = get_object_or_404(ListingImage, pk=image_pk)
    parent_listing = image_to_delete.listing

    edit_redirect_url_name = None
    if hasattr(parent_listing, 'flatlisting'):
        edit_redirect_url_name = 'posts:update_flat_listing'
    elif hasattr(parent_listing, 'groupformationpost'):
        edit_redirect_url_name = 'posts:update_group_post'
    else:
        messages.error(request, "Cannot determine parent listing type for redirection.")
        return redirect('landing_home')

    if parent_listing.creator != request.user:
        messages.error(request, "You are not authorized to delete this image.")
        return redirect(edit_redirect_url_name, pk=parent_listing.pk) if edit_redirect_url_name else redirect('landing_home')


    image_filename = image_to_delete.image.name
    image_to_delete.delete()
    messages.success(request, f"Image '{image_filename}' deleted successfully.")
    
    return redirect(edit_redirect_url_name, pk=parent_listing.pk) if edit_redirect_url_name else redirect('landing_home')

