from django import forms
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


# same as AuthenticationForm but with a custom error message for nonexistent users
class LoginForm(AuthenticationForm):
    error_messages = AuthenticationForm.error_messages
    error_messages.update(
        {"invalid_user": _("The user '%(username)s' does not exist.")}
    )

    def confirm_user_exists(self):
        username = self.cleaned_data.get("username")
        try:
            User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ValidationError(
                self.error_messages["invalid_user"],
                code="invalid_user",
                params={"username": username},
            )

    def clean(self):
        try:
            super().clean()

        except ValidationError as e:
            if e.code == "invalid_login":
                self.confirm_user_exists()

            raise e
