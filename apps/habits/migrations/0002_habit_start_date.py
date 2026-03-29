from datetime import date

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_habits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='start_date',
            field=models.DateField(default=date.today, verbose_name='Boshlanish sanasi'),
        ),
    ]
