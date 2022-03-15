# Generated by Django 3.2.8 on 2022-03-08 06:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hunt_data', '0001_initial'),
        ('spoilr_core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='p555ctsprogressmodel',
            name='puzzle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.puzzle'),
        ),
        migrations.AddField(
            model_name='p555ctsprogressmodel',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.team'),
        ),
        migrations.AddField(
            model_name='p555ctsbookmodel',
            name='progress',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='books', to='hunt_data.p555ctsprogressmodel'),
        ),
        migrations.AddField(
            model_name='p44trustnobodyprogressmodel',
            name='puzzle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.puzzle'),
        ),
        migrations.AddField(
            model_name='p44trustnobodyprogressmodel',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.team'),
        ),
        migrations.AddField(
            model_name='p318messyroommodel',
            name='puzzle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.puzzle'),
        ),
        migrations.AddField(
            model_name='p318messyroommodel',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.team'),
        ),
        migrations.AddField(
            model_name='p318messyroomgameusedindexmodel',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='used_indices', to='hunt_data.p318messyroomgamemodel'),
        ),
        migrations.AddField(
            model_name='p318messyroomgamemodel',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hunt_data.p318messyroommodel'),
        ),
        migrations.AddField(
            model_name='p318messyroomgamecellmodel',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cells', to='hunt_data.p318messyroomgamemodel'),
        ),
        migrations.AddField(
            model_name='p246strangegarnetsprogressmodel',
            name='puzzle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.puzzle'),
        ),
        migrations.AddField(
            model_name='p246strangegarnetsprogressmodel',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.team'),
        ),
        migrations.AddField(
            model_name='p246strangegarnetsopenpassprogressmodel',
            name='progress',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='open_pass_levels', to='hunt_data.p246strangegarnetsprogressmodel'),
        ),
        migrations.AddField(
            model_name='p156gearspegmodel',
            name='gear',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pegs', to='hunt_data.p156gearsgearmodel'),
        ),
        migrations.AddField(
            model_name='p156gearsmodel',
            name='puzzle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.puzzle'),
        ),
        migrations.AddField(
            model_name='p156gearsmodel',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.team'),
        ),
        migrations.AddField(
            model_name='p156gearsgearmodel',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gears', to='hunt_data.p156gearsgamemodel'),
        ),
        migrations.AddField(
            model_name='p156gearsgamemodel',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hunt_data.p156gearsmodel'),
        ),
        migrations.AddField(
            model_name='p1004countingmodel',
            name='puzzle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.puzzle'),
        ),
        migrations.AddField(
            model_name='p1004countingmodel',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spoilr_core.team'),
        ),
        migrations.AddField(
            model_name='p1002blackjackcardsmodel',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards', to='hunt_data.p1002blackjackgamemodel'),
        ),
        migrations.AlterUniqueTogether(
            name='p555ctsprogressmodel',
            unique_together={('team', 'puzzle')},
        ),
        migrations.AlterUniqueTogether(
            name='p555ctsbookmodel',
            unique_together={('progress', 'book')},
        ),
        migrations.AlterUniqueTogether(
            name='p44trustnobodyprogressmodel',
            unique_together={('team', 'puzzle')},
        ),
        migrations.AlterUniqueTogether(
            name='p318messyroomgameusedindexmodel',
            unique_together={('game', 'board', 'col', 'index')},
        ),
        migrations.AlterUniqueTogether(
            name='p318messyroomgamemodel',
            unique_together={('scope', 'abandoned_time')},
        ),
        migrations.AlterUniqueTogether(
            name='p318messyroomgamecellmodel',
            unique_together={('game', 'board', 'row', 'col')},
        ),
        migrations.AlterUniqueTogether(
            name='p246strangegarnetsprogressmodel',
            unique_together={('team', 'puzzle')},
        ),
        migrations.AlterUniqueTogether(
            name='p246strangegarnetsopenpassprogressmodel',
            unique_together={('progress', 'level')},
        ),
        migrations.AlterUniqueTogether(
            name='p156gearspegmodel',
            unique_together={('gear', 'index')},
        ),
        migrations.AlterUniqueTogether(
            name='p156gearsgearmodel',
            unique_together={('game', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='p156gearsgamemodel',
            unique_together={('scope', 'abandoned_time')},
        ),
    ]