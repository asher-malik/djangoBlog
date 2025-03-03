# Generated by Django 5.1.6 on 2025-02-18 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_last_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pictures/Default-profile.png', max_length=555, null=True, upload_to='profile_pictures'),
        ),
    ]
