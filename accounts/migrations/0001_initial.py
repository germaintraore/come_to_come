from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apprenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom')),
                ('prenom', models.CharField(max_length=100, verbose_name='Prénom')),
                ('whatsapp', models.CharField(
                    help_text='Ex: +22670000000',
                    max_length=20,
                    unique=True,
                    verbose_name='Numéro WhatsApp',
                )),
                ('date_inscription', models.DateTimeField(
                    default=django.utils.timezone.now,
                    verbose_name="Date d'inscription",
                )),
                ('is_active', models.BooleanField(default=True, verbose_name='Compte actif')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Membre du staff')),
                ('groups', models.ManyToManyField(
                    blank=True,
                    help_text='The groups this user belongs to.',
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.group',
                    verbose_name='groups',
                )),
                ('user_permissions', models.ManyToManyField(
                    blank=True,
                    help_text='Specific permissions for this user.',
                    related_name='user_set',
                    related_query_name='user',
                    to='auth.permission',
                    verbose_name='user permissions',
                )),
            ],
            options={
                'verbose_name': 'Apprenant',
                'verbose_name_plural': 'Apprenants',
                'db_table': 'apprenant',
                'ordering': ['-date_inscription'],
            },
        ),
    ]
