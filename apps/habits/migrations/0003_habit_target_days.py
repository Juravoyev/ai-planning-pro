from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_habits', '0002_habit_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='target_days',
            field=models.PositiveIntegerField(default=66, verbose_name='Shakllanish muddati (kun)'),
        ),
    ]
