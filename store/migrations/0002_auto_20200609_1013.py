# Generated by Django 2.2 on 2020-06-09 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='related_default_category',
            new_name='default_category',
        ),
        migrations.AlterField(
            model_name='product',
            name='related_categories',
            field=models.ManyToManyField(blank=True, related_name='default_categories', to='store.Category'),
        ),
    ]
