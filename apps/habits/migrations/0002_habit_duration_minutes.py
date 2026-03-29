from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_habits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='duration_minutes',
            field=models.PositiveIntegerField(
                default=30,
                verbose_name='Davomiylik (daqiqa)',
            ),
        ),
    ]