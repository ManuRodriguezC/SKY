from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import Group
from django.db.models import Count
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required


from apps.accounts.models import CustomUser, VerificationToken, VerificationStatus
from apps.accounts.forms import GroupForm, CustomUserForm
from apps.accounts.utils import get_permissions
from apps.accounts.verification_service import send_verification_email

class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        
        if not user.is_verified and not user.is_superuser:
          form.add_error(
            None,
            "Su cuenta no ha sido verificada. Por favor, revise la bandeja de su correo."
          )
          return self.form_invalid(form)
        
        return super().form_valid(form)
    
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class VerifyAccountView(TemplateView):
    template_name = "verify_account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        token = VerificationToken.objects.filter(
            uuid=kwargs["uuid"]
        ).first()
        
        if token:
            context.update(token.verify(self.request))
        else:
            context.update({
                "response": False,
                "status": VerificationStatus.NOT_FOUND
            })
        
        return context


class UsersListView(ListView):
    model = CustomUser
    template_name = 'users_list.html'
    context_object_name = 'users_list'
    
    paginate_by = 10
    
    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by("-is_active", "-id")
        
        search = self.request.GET.get("search")
        
        if search:
            queryset = queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            ) | queryset.filter(
                document__icontains=search
            ) | queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                username__icontains=search
            )

        return queryset
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = CustomUser.objects.all()

        context.update({
            "title_page": "Usuarios",

            "num_users": users.count(),

            "actives": users.filter(
                is_active=True, is_verified=True
            ).count(),

            "inactives": users.filter(
                is_active=False
            ).count(),

            "not_verificate": users.filter(
                is_verified=False
            ).count(),
        })

        return context


class CreateUserView(CreateView):
    model = CustomUser
    form_class = CustomUserForm
    success_url = reverse_lazy("users")
    permission_required = "accounts.add_customuser"
    raise_exception = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["title"] = "Crear Usuario"
        context["message"] = "Registra un usuario y asigna grupos."
        context["button"] = "Crear usuario"
        
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        
        send_response = send_verification_email(
            self.request,
            self.object
        )
        if send_response:
            messages.success(self.request, "Usuario creado exitosamente. Se ha enviado un correo de verificacion de cuenta.")
        else:
            messages.warning(self.request, "Usuario creado exitosamente. Ha fallado el envio del correo de verificacion.")
        
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al crear el usuario.")
        return super().form_invalid(form)


class UpdateUserView(UpdateView):
    model = CustomUser
    form_class = CustomUserForm
    success_url = reverse_lazy("users")
    permission_required = "accounts.change_customuser"
    raise_exception = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["title"] = "Actualizar Usuario"
        context["message"] = "Edita o actualiza la informacion del usuario."
        context["button"] = "Guardar"
        
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Usuario creado exitosamente.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al crear el usuario.")
        return super().form_invalid(form)


class GroupsListView(ListView):
    model = Group
    template_name = 'groups_list.html'
    context_object_name = 'groups_list'

    def get_queryset(self):
        return (
            Group.objects
            .annotate(
                total_permissions=Count('permissions', distinct=True),
                total_users=Count('user', distinct=True)
            )
            .order_by('id')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            "title_page": "Grupos"
        })
        
        return context

class CreateGroupView(CreateView):
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy("groups")
    permission_required = "auth.add_group"
    raise_exception = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
    
        context["grouped_permissions"] = dict(
            get_permissions()
        )
        
        context["title"] = "Crear grupo"
        context["button_text"] = "Crear"
        
        return context

    def form_valid(self, form):
        messages.success(self.request, "Grupo creado exitosamente.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al crear el grupo.")
        return super().form_invalid(form)



class UpdateGroupView(UpdateView):
    model = Group
    form_class = GroupForm
    success_url = reverse_lazy("groups")
    permission_required = "auth.change_group"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["grouped_permissions"] = dict(
            get_permissions()
        )

        context["title"] = "Editar grupo"
        context["button_text"] = "Guardar cambios"

        return context

    def form_valid(self, form):
        messages.success(self.request, "Grupo actualizado exitosamente.")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "Ocurrió un error al actualizar el grupo.")
        return super().form_invalid(form)

@permission_required("accounts.change_customuser", raise_exception=True)
def desactiveUser(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    if not user:
        messages.error(request, "Usuario no encontrado")
        
    user.is_active = not user.is_active
    
    if user.is_active:
        messages.success(request, f"Se a activado el usuario {user.username}")
    else:
        messages.success(request, f"Se a desactivado el usuario {user.username}")
    
    user.save()
    
    return redirect('users')
    