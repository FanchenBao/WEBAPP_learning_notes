# Generated by Django 2.1.2 on 2018-10-25 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_notes', '0004_auto_20181024_2148'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='title',
            field=models.CharField(default='some title', max_length=200),
        ),
    ]
