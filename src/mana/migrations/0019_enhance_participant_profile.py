# Generated migration for enhanced participant profile

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_add_multiple_teams_to_stafftask'),
        ('mana', '0018_add_workshop_notification'),
    ]

    operations = [
        # Add demographic fields
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='age',
            field=models.PositiveIntegerField(
                null=True,
                blank=True,
                help_text="Participant's age"
            ),
        ),
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='sex',
            field=models.CharField(
                max_length=10,
                choices=[('male', 'Male'), ('female', 'Female')],
                blank=True,
                help_text="Participant's sex"
            ),
        ),

        # Add region for participant address
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='region',
            field=models.ForeignKey(
                to='common.Region',
                on_delete=models.CASCADE,
                related_name='workshop_participants_region',
                null=True,
                blank=True,
                help_text="Region of participant"
            ),
        ),

        # Add education fields
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='educational_level',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('graduate_degree', 'Graduate Degree Holder'),
                    ('bachelors_degree', "Bachelor's Degree Holder"),
                    ('college_level', 'College Level'),
                    ('high_school_graduate', 'High School Graduate'),
                    ('high_school_level', 'High School Level'),
                    ('elementary_level', 'Elementary Level'),
                    ('no_formal_education', 'No Formal Education'),
                ],
                blank=True,
                help_text="Educational attainment"
            ),
        ),
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='arabic_education_level',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('kulliyah_graduate', 'Kulliyah Graduate'),
                    ('thanawiyyah_level', 'Thanawiyyah Level'),
                    ('mutawassitah_level', 'Mutawassitah Level'),
                    ('ibtidaiyyah_level', 'Ibtidaiyyah Level'),
                    ('tahfidz_graduate', 'Tahfidz Graduate/Level'),
                    ('no_arabic_education', 'No Arabic Education'),
                ],
                blank=True,
                help_text="Arabic/Islamic education level"
            ),
        ),

        # Add occupation
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='occupation',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('government_employee', 'Government Employee'),
                    ('business_owner', 'Business Owner'),
                    ('private_sector', 'Private Sector Employee'),
                    ('ngo_worker', 'NGO Worker'),
                    ('farmer', 'Farmer'),
                    ('fisherfolk', 'Fisherfolk'),
                    ('teacher', 'Teacher/Educator'),
                    ('health_worker', 'Health Worker'),
                    ('religious_worker', 'Religious Worker/Imam'),
                    ('traditional_leader', 'Traditional/Community Leader'),
                    ('student', 'Student'),
                    ('self_employed', 'Self-Employed'),
                    ('unemployed', 'Unemployed'),
                    ('retired', 'Retired'),
                    ('other', 'Other'),
                ],
                blank=True,
                help_text="Current occupation"
            ),
        ),

        # Rename organization to office_business_name
        migrations.RenameField(
            model_name='workshopparticipantaccount',
            old_name='organization',
            new_name='office_business_name',
        ),
        migrations.AlterField(
            model_name='workshopparticipantaccount',
            name='office_business_name',
            field=models.CharField(
                max_length=200,
                blank=True,
                help_text="Name of office or business (optional)"
            ),
        ),

        # Add office address fields
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='office_region',
            field=models.ForeignKey(
                to='common.Region',
                on_delete=models.SET_NULL,
                related_name='office_participants',
                null=True,
                blank=True,
                help_text="Office region (optional)"
            ),
        ),
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='office_province',
            field=models.ForeignKey(
                to='common.Province',
                on_delete=models.SET_NULL,
                related_name='office_participants',
                null=True,
                blank=True,
                help_text="Office province (optional)"
            ),
        ),
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='office_municipality',
            field=models.ForeignKey(
                to='common.Municipality',
                on_delete=models.SET_NULL,
                related_name='office_participants',
                null=True,
                blank=True,
                help_text="Office municipality (optional)"
            ),
        ),
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='office_barangay',
            field=models.ForeignKey(
                to='common.Barangay',
                on_delete=models.SET_NULL,
                related_name='office_participants',
                null=True,
                blank=True,
                help_text="Office barangay (optional)"
            ),
        ),

        # Add office mandate field
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='office_mandate',
            field=models.TextField(
                blank=True,
                help_text="Mandate of office (if government agency, optional)"
            ),
        ),

        # Add mandate awareness field
        migrations.AddField(
            model_name='workshopparticipantaccount',
            name='aware_of_mandate',
            field=models.BooleanField(
                default=False,
                help_text="Aware of the Mandate for Assistance to Other Bangsamoro Communities"
            ),
        ),
    ]