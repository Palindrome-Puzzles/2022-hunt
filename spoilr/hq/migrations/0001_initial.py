# Generated by Django 3.2.8 on 2022-03-08 06:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Handler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('discord', models.CharField(max_length=100, unique=True)),
                ('phone', models.CharField(blank=True, max_length=50, null=True)),
                ('activity_time', models.DateTimeField(blank=True, null=True)),
                ('sign_in_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('done', 'Done'), ('ignored', 'Ignored'), ('snoozed', 'Snoozed')], default='pending', max_length=20)),
                ('claim_time', models.DateTimeField(blank=True, null=True)),
                ('snooze_time', models.DateTimeField(blank=True, null=True)),
                ('snooze_until', models.DateTimeField(blank=True, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('handler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='spoilr_hq.handler')),
            ],
        ),
        migrations.CreateModel(
            name='HqLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('event_type', models.CharField(max_length=50)),
                ('object_id', models.CharField(blank=True, max_length=200, null=True)),
                ('message', models.TextField()),
                ('handler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='spoilr_hq.handler')),
            ],
            options={
                'verbose_name_plural': 'HQ log',
            },
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.CheckConstraint(check=models.Q(('status__in', ['pending', 'done', 'ignored', 'snoozed'])), name='spoilr_hq_task_status_valid'),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.CheckConstraint(check=models.Q(models.Q(models.Q(('status', 'snoozed'), _negated=True), ('snooze_time__isnull', True), ('snooze_until__isnull', True)), models.Q(('snooze_time__isnull', False), ('snooze_until__isnull', False), ('status', 'snoozed')), _connector='OR'), name='spoilr_hq_task_snooze_valid'),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('claim_time__isnull', False), ('handler__isnull', False)), ('handler__isnull', True), _connector='OR'), name='spoilr_hq_task_handler_has_claim_time'),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together={('content_type', 'object_id')},
        ),
    ]
