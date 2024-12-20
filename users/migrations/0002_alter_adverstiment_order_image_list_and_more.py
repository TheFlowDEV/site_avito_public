# Generated by Django 5.0.4 on 2024-05-12 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adverstiment',
            name='order_image_list',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='oauth2token',
            name='expires_at',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='oauth2token',
            name='refresh_token',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='oauth2token',
            name='token_type',
            field=models.TextField(null=True),
        ),
    ]
