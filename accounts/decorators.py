from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def management_required(function=None):
    """
    Decorator for views that checks that the user is logged in and has the
    'Management' role or is a Superuser. Raises 403 Forbidden otherwise.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and (u.role == 'Management' or u.is_superuser),
        login_url=None # Don't redirect, let PermissionDenied handle the 403 if they don't pass the check but are logged in
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# An alternative using a wrapper that explicitly raises PermissionDenied
def management_or_superuser_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            # Let login_required handle unauthenticated users, or raise 403 if preferred.
            # Assuming @login_required is used in conjunction, we just check roles here.
            raise PermissionDenied

        if request.user.role == 'Management' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return _wrapped_view
