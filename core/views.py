from django.shortcuts import render
from posts.models import FlatListing, GroupFormationPost

def new_homepage_view(request):
    print("\n--- Attempting to render homepage (core.views.new_homepage_view) ---")

    try:
        featured_flats = FlatListing.objects.order_by('-created_at')[:3]
        featured_groups = GroupFormationPost.objects.order_by('-created_at')[:2]
        print("Successfully fetched listings.")
    except Exception as e:
        print(f"Error fetching listings: {e}")
        featured_flats = []
        featured_groups = []


    is_bracu_student = False
    print(f"Initial is_bracu_student: {is_bracu_student}")

    if request.user.is_authenticated:
        print(f"User IS authenticated. Username: {request.user.username}")
        try:
            user_email = getattr(request.user, 'email', None)
            print(f"  User email: {user_email}")
            if user_email and isinstance(user_email, str) and user_email.lower().endswith('@g.bracu.ac.bd'):
                is_bracu_student = True
                print(f"  Email check PASSED. is_bracu_student set to: {is_bracu_student}")
            else:
                if not user_email:
                    print("  Email is None or empty.")
                elif not isinstance(user_email, str):
                    print(f"  Email is not a string, it is: {type(user_email)}")
                else:
                    print(f"  Email does not end with @g.bracu.ac.bd. Current ending: {user_email.split('@')[-1] if '@' in user_email else 'N/A'}")
                print(f"  Email check FAILED. is_bracu_student remains: {is_bracu_student}")
        except AttributeError:
            print("  AttributeError when accessing user.email (should be caught by getattr).")
    else:
        print("User IS NOT authenticated.")

    context = {
        'featured_flat_listings': featured_flats,
        'featured_group_posts': featured_groups,
        'is_bracu_student_for_view': is_bracu_student
    }
    print(f"Final context: is_bracu_student_for_view = {is_bracu_student}")
    print("--- Finished processing homepage view ---\n")
    return render(request, 'landing.html', context)