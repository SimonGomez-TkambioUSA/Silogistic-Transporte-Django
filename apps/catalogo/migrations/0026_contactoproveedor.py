# Generated by Django 4.0.3 on 2023-04-20 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0025_proveedor_calle_proveedor_cp_proveedor_cuidad_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactoProveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=150, null=True)),
                ('puesto', models.CharField(blank=True, max_length=150, null=True)),
                ('celular', models.CharField(blank=True, max_length=150, null=True)),
                ('email', models.CharField(blank=True, max_length=150, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
                ('register_by', models.IntegerField(blank=True, null=True)),
                ('proveedor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogo.proveedor')),
            ],
        ),
    ]
