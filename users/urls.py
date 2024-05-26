from django.urls import path
from django.views.generic import TemplateView

from book_flow.views import BookList
from users.views import RegisterView, CustomLoginView, custom_logout_view, ProfileView

app_name = 'users'

urlpatterns = [
    path('', BookList.as_view(), name="home"),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
