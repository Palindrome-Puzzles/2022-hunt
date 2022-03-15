from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import auth_views, register_views, top_views

urlpatterns = [
    path('', top_views.index_view, name='registration_index'),

    path('login', auth_views.login_view, name='registration_login'),
    path('logout', auth_views.logout_view, name='registration_logout'),

    path('register/team', register_views.register_team_view, name='register_team'),
    path('register/team/lock', register_views.registration_lock_view, name='registration_lock'),
    path('register/solver', register_views.register_solver_view, name='register_solver'),
    path('team', register_views.update_registration_view, name='update_registration'),
]
