from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
import html
from ckeditor_uploader.fields import RichTextUploadingField 
from PIL import Image
import io

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    pub_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(unique=True, max_length=200)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category')
    tags = models.ManyToManyField('Tag')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                img = Image.open(self.image)

                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')

                target_size = (784, 800)

                img.thumbnail(target_size, Image.Resampling.LANCZOS)

                new_img = Image.new('RGB', target_size, (255, 255, 255))  # White background
                offset = (
                    (target_size[0] - img.size[0]) // 2,
                    (target_size[1] - img.size[1]) // 2
                )
                new_img.paste(img, offset)

                buffer = io.BytesIO()
                new_img.save(buffer, format='JPEG', quality=85) 
                buffer.seek(0)

                new_filename = self.image.name
                self.image.save(new_filename, ContentFile(buffer.getvalue()), save=False)

                super().save(*args, **kwargs)
            except Exception as e:
                print(f"Error resizing image: {e}")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('sqblog:post_detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['-pub_date']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'