# Generated by Django 5.0.4 on 2024-05-10 06:00

import encrypted_model_fields.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.TextField()),
                ('text', encrypted_model_fields.fields.EncryptedTextField()),
                ('timestamp', models.DateTimeField()),
                ('read', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Head', models.TextField()),
                ('Description', models.TextField()),
                ('Timestamp', models.DateTimeField()),
            ],
        ),
    ]
