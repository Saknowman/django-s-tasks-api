# Generated by Django 3.0 on 2019-12-11 03:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('s_tasks_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lock_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(63)])),
                ('assign_lock_level', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)])),
                ('assignee', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_tasks', to='auth.Group')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='group_task', to='s_tasks_api.Task')),
            ],
        ),
    ]
