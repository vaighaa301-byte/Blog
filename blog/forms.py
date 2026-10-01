from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "featured_image"]
        error_messages = {
            "title": {"required": "Please enter a title."},
            "content": {"required": "Please enter the post content."},
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Post title"}),
            "content": forms.Textarea(
                attrs={"rows": 8, "placeholder": "Write your post..."}
            ),
            "featured_image": forms.ClearableFileInput(),
        }
