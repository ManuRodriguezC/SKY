from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


from apps.accounts.models import CustomUser


class CustomUserForm(forms.ModelForm):
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "checkbox checkbox-primary"
            }
        )
    )
    
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "document",
            "address",
            "groups",
        ]

        widgets = {

            "username": forms.TextInput(
                attrs={
                    "class": """
                        input input-bordered w-full
                        bg-base-300
                        rounded-xl
                        border border-base-content/10
                        focus:border-primary
                        focus:outline-none
                    """,
                    "placeholder": "Nombre de usuario"
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": """
                        input input-bordered w-full
                        bg-base-300
                        rounded-xl
                        border border-base-content/10
                        focus:border-primary
                        focus:outline-none
                    """,
                    "placeholder": "Nombre"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": """
                        input input-bordered w-full
                        bg-base-300
                        rounded-xl
                        border border-base-content/10
                        focus:border-primary
                        focus:outline-none
                    """,
                    "placeholder": "Apellido"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": """
                        input input-bordered w-full
                        bg-base-300
                        rounded-xl
                        border border-base-content/10
                        focus:border-primary
                        focus:outline-none
                    """,
                    "placeholder": "correo@ejemplo.com"
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": """
                        input input-bordered w-full
                        bg-base-300
                        rounded-xl
                        border border-base-content/10
                        focus:border-primary
                        focus:outline-none
                    """,
                    "placeholder": "Teléfono"
                }
            ),

            "document": forms.TextInput(
                attrs={
                    "class": """
                        input input-bordered w-full
                        bg-base-300
                        rounded-xl
                        border border-base-content/10
                        focus:border-primary
                        focus:outline-none
                    """,
                    "placeholder": "Documento"
                }
            ),

            "address": forms.TextInput(
                attrs={
                    "class": """
                        input input-bordered w-full
                        bg-base-300
                        rounded-xl
                        border border-base-content/10
                        focus:border-primary
                        focus:outline-none
                    """,
                    "placeholder": "Dirección"
                }
            ),

        }

    def save(self, commit=True):

        user = super().save(commit=False)

        if commit:
            user.save()
            user.groups.set(
                self.cleaned_data["groups"]
            )

        return user


class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.select_related("content_type").all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]
        
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "bg-base-300 p-2 rounded-lg border-1 border-bg-content",
                    "placeholder": "Nombre del grupo"
                }
            )
        }
        

class CustomPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": (
                    "input "
                    "input-bordered "
                    "w-full "
                    "bg-base-100"
                ),
                "placeholder": "correo@ejemplo.com",
                "autocomplete": "email",
            }
        )
    )

    def get_users(self, email):

        users = super().get_users(email)

        return (
            user
            for user in users
            if (
                user.is_active and
                user.is_verified
            )
        )
        

class CustomSetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": (
                    "input "
                    "input-bordered "
                    "w-full "
                    "bg-base-100"
                ),
                "placeholder": "Nueva contraseña",
            }
        )
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": (
                    "input "
                    "input-bordered "
                    "w-full "
                    "bg-base-100"
                ),
                "placeholder": "Confirmar contraseña",
            }
        )
    )