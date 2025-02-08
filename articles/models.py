from django.db import models
from django.contrib.auth.models import User

# Define choices for user roles
ROLE_CHOICES = [
    ('journalist', 'Journalist'),
    ('editor', 'Editor'),
    ('admin', 'Admin'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='journalist')

    def __str__(self):
        return (f"{self.user.username} - {self.role}")
    
    


# Define choices for article categories and tags
CATEGORY_CHOICES = [
    ('news', 'News'),
    ('opinion', 'Opinion'),
    ('feature', 'Feature'),
]

TAG_CHOICES = [
    ('politics', 'Politics'),
    ('sports', 'Sports'),
    ('tech', 'Tech'),
]

STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
class Article(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the user (journalist)
    email = models.EmailField()  # Email of the author
    image = models.ImageField(upload_to='article_images/', blank=True, null=True)
    tags = models.CharField(max_length=255, choices=TAG_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    publish_date = models.DateField()
    is_published = models.BooleanField(default=False)  # Will be updated by Editor/Admin
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.title
