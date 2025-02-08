# Generated by Django 5.1.1 on 2024-10-07 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0005_alter_article_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(choices=[('Submitted', 'Submitted'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Submitted', max_length=10),
        ),
    ]
