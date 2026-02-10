from django.views.generic import FormView
from .forms import UserProfileForm
from django.urls import reverse_lazy
from django.contrib import messages

class UserSignupView(FormView):
    template_name = 'accounts/signup.html'
    form_class = UserProfileForm
    success_url = reverse_lazy("accounts:signin")

    def form_valid(self, form):
        # form.save()
        return super(UserSignupView, self).form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "There were errors in your submission. Please correct them and try again.")
        return super(UserSignupView, self).form_invalid(form)