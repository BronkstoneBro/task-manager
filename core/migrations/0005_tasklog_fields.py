from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_tasklog'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklog',
            name='new_value',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='tasklog',
            name='message',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='action',
            field=models.CharField(max_length=16, choices=[
                ('update', 'Update'),
                ('comment', 'Comment'),
                ('file', 'File'),
                ('complete', 'Complete'),
                ('uncomplete', 'Uncomplete'),
            ]),
        ),
    ] 