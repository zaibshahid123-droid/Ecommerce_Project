from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_profile_is_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(
                choices=[('owner', 'Owner'), ('employee', 'Employee'), ('customer', 'Customer')],
                default='customer',
                max_length=20,
            ),
        ),
    ]
