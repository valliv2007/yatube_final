# Generated by Django 2.2.16 on 2022-07-02 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_create_model_comment_20220701'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='created',
            new_name='pub_date',
        ),
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(verbose_name='comment text'),
        ),
    ]