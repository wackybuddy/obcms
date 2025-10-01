"""Authentication and account management views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from ..forms import CustomLoginForm, UserRegistrationForm
from ..models import User


class CustomLoginView(LoginView):
    """Custom login view with OBC branding and approval check."""

    template_name = "common/login.html"
    form_class = CustomLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_approved and not user.is_superuser:
            messages.error(
                self.request,
                "Your account is pending approval. Please contact the administrator.",
            )
            return self.form_invalid(form)
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view."""

    next_page = reverse_lazy("common:login")

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    """User registration view with approval workflow."""

    model = User
    form_class = UserRegistrationForm
    template_name = "common/register.html"
    success_url = reverse_lazy("common:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Registration successful! Your account is pending approval. "
            "You will be notified once your account is approved.",
        )
        return response


@login_required
def profile(request):
    """User profile view."""
    return render(request, "common/profile.html", {"user": request.user})


@login_required
def page_restricted(request):
    """Render the restricted-access placeholder screen."""
    return render(request, "common/page_restricted.html")


__all__ = [
    "CustomLoginView",
    "CustomLogoutView",
    "UserRegistrationView",
    "profile",
    "page_restricted",
]
