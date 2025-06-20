# Generated by Django 4.0.3 on 2022-05-27 14:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0013_orden_us_driver_two'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonaSistema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('ap_paterno', models.CharField(blank=True, max_length=100, null=True)),
                ('ap_materno', models.CharField(blank=True, max_length=100, null=True)),
                ('correo', models.CharField(blank=True, max_length=200, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('register_by', models.IntegerField(blank=True, null=True)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
