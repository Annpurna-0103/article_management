# Generated by Django 5.1.1 on 2024-09-12 06:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('subtitle', models.CharField(blank=True, max_length=255, null=True)),
                ('content', models.TextField()),
                ('email', models.EmailField(max_length=254)),
                ('image', models.ImageField(blank=True, null=True, upload_to='article_images/')),
                ('tags', models.CharField(choices=[('politics', 'Politics'), ('sports', 'Sports'), ('tech', 'Tech')], max_length=255)),
                ('category', models.CharField(choices=[('news', 'News'), ('opinion', 'Opinion'), ('feature', 'Feature')], max_length=20)),
                ('publish_date', models.DateField()),
                ('is_published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('journalist', 'Journalist'), ('editor', 'Editor'), ('admin', 'Admin')], default='journalist', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
