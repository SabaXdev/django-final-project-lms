from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView

from book_flow.models import BorrowHistory
from users.forms import CustomUserCreationForm, CustomLoginForm


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:logout')

    def form_valid(self, form):
        user = form.save(commit=False)
        email = form.cleaned_data['email']
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']

        if password1 == password2:
            user.set_password(password1)
            user.save()

            messages.success(self.request, f'Your Account has been created {email} ! Proceed to log in.')
            login(self.request, user)
            return redirect('users:login')
        form.add_error('password2', 'Passwords entered do not match')
        return super(RegisterView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('users:login')
        return super(RegisterView, self).get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success_message'] = messages.get_messages(self.request)
        return context


class CustomLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'users/login.html'
    form_class = CustomLoginForm

    def get(self, request):
        form = self.form_class()
        message = ''
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user:
                login(request, user)
                return redirect('users:home')
        message = 'Login failed!'
        return render(request, self.template_name, {'form': form, 'message': message})


def custom_logout_view(request):
    logout(request)
    return redirect('users:home')


class ProfileView(LoginRequiredMixin, ListView):
    model = BorrowHistory
    template_name = 'users/profile.html'
    context_object_name = 'books'
    login_url = '/users/login/'

    def get_queryset(self):
        user = self.request.user
        return BorrowHistory.objects.filter(borrower=user, returned=False)
