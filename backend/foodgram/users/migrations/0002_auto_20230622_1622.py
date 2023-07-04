# Generated by Django 3.2.19 on 2023-06-22 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_recipe_options'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cart',
            field=models.ManyToManyField(blank=True, related_name='user_cart', to='app.Recipe'),
        ),
        migrations.AddField(
            model_name='user',
            name='favorite_list',
            field=models.ManyToManyField(blank=True, related_name='user_favorite', to='app.Recipe'),
        ),
    ]
