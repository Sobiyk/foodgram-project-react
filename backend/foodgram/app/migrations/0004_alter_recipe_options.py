# Generated by Django 3.2.19 on 2023-06-21 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['id'], 'verbose_name': 'рецепт', 'verbose_name_plural': 'рецепты'},
        ),
    ]
