from django.db import models
from encrypted_model_fields.fields import EncryptedTextField
import uuid

# a function that generates a unique referral code for new users
def generate_referral_code(model):
    referral_code = uuid.uuid4().hex[:12].upper() # 12-character code all uppercase

    if model.objects.filter(referral_code=referral_code).exists():
        return generate_referral_code(model)
    return referral_code

class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    referral_code = models.CharField(max_length=12, unique=True, editable=False)
    refered_by = models.CharField(max_length=12, blank=True, null=True)
    binance_api_key = EncryptedTextField(verbose_name="Binance API Key", blank=True, null=True)
    binance_api_secret = EncryptedTextField(verbose_name="Binance API Secret", blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username
    
    class Meta:
        ordering = ['username']
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

# class LoginAttempt(models.Model):
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='login_attempts')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     successful = models.BooleanField(default=False)
#     ip_address = models.GenericIPAddressField()

#     def __str__(self):
#         status = "Successful" if self.successful else "Failed"
#         return f"{self.user.username} - {status} at {self.timestamp}"

#     class Meta:
#         ordering = ['-timestamp']
#         verbose_name = "Login Attempt"
#         verbose_name_plural = "Login Attempts"

# class PasswordResetRequest(models.Model):
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='password_reset_requests')
#     token = models.CharField(max_length=64, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     used = models.BooleanField(default=False)

#     def __str__(self):
#         return f"Password Reset for {self.user.username} at {self.created_at}"

#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Password Reset Request"
#         verbose_name_plural = "Password Reset Requests"

# class LoginHistory(models.Model):
#     user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='login_history')
#     login_time = models.DateTimeField(auto_now_add=True)
#     logout_time = models.DateTimeField(null=True, blank=True)
#     ip_address = models.GenericIPAddressField()

#     def __str__(self):
#         return f"{self.user.username} logged in at {self.login_time}"

#     class Meta:
#         ordering = ['-login_time']
#         verbose_name = "Login History"
#         verbose_name_plural = "Login Histories"
