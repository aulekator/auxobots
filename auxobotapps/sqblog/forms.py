# blog/forms.py
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'content']
        widgets = {
            'author': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'content': forms.Textarea(attrs={'placeholder': 'Your comment'}),
        }