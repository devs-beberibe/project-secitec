# Generated by Django 4.1 on 2023-04-16 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('called', '0004_call_status_alter_secretary_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='status',
            field=models.CharField(choices=[('OPN', 'abertos'), ('IMP', 'emAndamento'), ('CLS', 'encerrados')], default='OPN', max_length=3),
        ),
    ]
