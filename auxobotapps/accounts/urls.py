from django.urls import path
from auxobotapps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path("signup/", view=views.UserSignupView.as_view(), name="signup"),
]