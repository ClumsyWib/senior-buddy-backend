from django.contrib.auth.models import AbstractUser
from django.db import models


# =====================================================
# SENIOR BUDDY — models.py
# Matches: senior_buddy_final.sql exactly
# App: senior_buddy
# =====================================================


# =====================================================
# USER TABLE
# =====================================================

class User(AbstractUser):
    """
    Extends Django's AbstractUser.
    AbstractUser already gives us:
      - password (hashed), is_active, date_joined, last_login
      - is_staff, is_superuser (needed for Django admin)
    We add full_name, phone, created_at on top.
    email is made unique and used as the login field.
    """
    full_name  = models.CharField(max_length=100)
    email      = models.EmailField(max_length=100, unique=True)
    phone      = models.CharField(max_length=15, unique=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Use email to log in instead of username
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'full_name', 'phone']

    class Meta:
        db_table = 'User'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


# =====================================================
# ROLE TABLE
# =====================================================

class Role(models.Model):
    ADMIN     = 'ADMIN'
    SENIOR    = 'SENIOR'
    CAREGIVER = 'CAREGIVER'
    FAMILY    = 'FAMILY'
    VOLUNTEER = 'VOLUNTEER'

    ROLE_CHOICES = [
        (ADMIN,     'Admin'),
        (SENIOR,    'Senior'),
        (CAREGIVER, 'Caregiver'),
        (FAMILY,    'Family'),
        (VOLUNTEER, 'Volunteer'),
    ]

    role_id   = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)

    class Meta:
        db_table = 'Role'

    def __str__(self):
        return self.role_name


# =====================================================
# USER ROLE MAPPING
# =====================================================

class UserRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        db_column='role_id'
    )

    class Meta:
        db_table = 'User_Role'
        unique_together = ('user', 'role')

    def __str__(self):
        return f"{self.user.full_name} → {self.role.role_name}"


# =====================================================
# PROFILE TABLES
# =====================================================

class SeniorProfile(models.Model):
    senior            = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='senior_id',
        related_name='senior_profile'
    )
    age               = models.IntegerField(null=True, blank=True)
    medical_history   = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100)

    class Meta:
        db_table = 'Senior_Profile'

    def __str__(self):
        return f"{self.senior.full_name} — Age {self.age}"


class CaregiverProfile(models.Model):
    caregiver        = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='caregiver_id',
        related_name='caregiver_profile'
    )
    qualification    = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)

    class Meta:
        db_table = 'Caregiver_Profile'

    def __str__(self):
        return f"{self.caregiver.full_name} — {self.qualification}"


class FamilyProfile(models.Model):
    family   = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='family_id',
        related_name='family_profile'
    )
    relation = models.CharField(max_length=100)

    class Meta:
        db_table = 'Family_Profile'

    def __str__(self):
        return f"{self.family.full_name} ({self.relation})"


class VolunteerProfile(models.Model):
    volunteer    = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='volunteer_id',
        related_name='volunteer_profile'
    )
    skills       = models.TextField(blank=True, null=True)
    availability = models.CharField(max_length=200, blank=True, null=True)
    is_verified  = models.BooleanField(default=False)

    class Meta:
        db_table = 'Volunteer_Profile'

    def __str__(self):
        status = 'Verified' if self.is_verified else 'Unverified'
        return f"{self.volunteer.full_name} ({status})"


# =====================================================
# RELATIONSHIP TABLES
# =====================================================

class SeniorCaregiver(models.Model):
    senior      = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='caregiver_assignments'
    )
    caregiver   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='caregiver_id',
        related_name='senior_assignments'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='assigned_by',
        related_name='caregiver_assignments_made',
        null=True,
        blank=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_primary  = models.BooleanField(default=False)

    class Meta:
        db_table = 'Senior_Caregiver'
        unique_together = ('senior', 'caregiver')

    def __str__(self):
        primary = ' (Primary)' if self.is_primary else ''
        return f"{self.senior.full_name} ← {self.caregiver.full_name}{primary}"


class SeniorFamily(models.Model):
    senior   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='family_links'
    )
    family   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='family_id',
        related_name='senior_links'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Senior_Family'
        unique_together = ('senior', 'family')

    def __str__(self):
        return f"{self.senior.full_name} ← {self.family.full_name}"


class SeniorVolunteer(models.Model):
    senior      = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='volunteer_assignments'
    )
    volunteer   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='volunteer_id',
        related_name='senior_volunteer_assignments'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='assigned_by',
        related_name='volunteer_assignments_made',
        null=True,
        blank=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Senior_Volunteer'
        unique_together = ('senior', 'volunteer')

    def __str__(self):
        return f"{self.senior.full_name} ← {self.volunteer.full_name}"


# =====================================================
# DOCTOR MODULE
# =====================================================

class Doctor(models.Model):
    doctor_id      = models.AutoField(primary_key=True)
    full_name      = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    phone          = models.CharField(max_length=20)
    hospital_name  = models.CharField(max_length=100)
    added_by       = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='added_by',
        related_name='doctors_added',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'Doctor'

    def __str__(self):
        return f"Dr. {self.full_name} — {self.specialization}"


class SeniorDoctor(models.Model):
    senior     = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='doctor_assignments'
    )
    doctor     = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        db_column='doctor_id',
        related_name='senior_assignments'
    )
    is_primary = models.BooleanField(default=False)
    added_by   = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='added_by',
        related_name='doctor_mappings_added',
        null=True,
        blank=True
    )
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Senior_Doctor'
        unique_together = ('senior', 'doctor')

    def __str__(self):
        primary = ' (Primary)' if self.is_primary else ''
        return f"{self.senior.full_name} → Dr. {self.doctor.full_name}{primary}"


# =====================================================
# REMINDER SYSTEM
# =====================================================

class Reminder(models.Model):
    MEDICATION  = 'MEDICATION'
    APPOINTMENT = 'APPOINTMENT'
    DAILY_TASK  = 'DAILY_TASK'

    TYPE_CHOICES = [
        (MEDICATION,  'Medication'),
        (APPOINTMENT, 'Appointment'),
        (DAILY_TASK,  'Daily Task'),
    ]

    reminder_id   = models.AutoField(primary_key=True)
    senior        = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='reminders'
    )
    created_by    = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='created_by',
        related_name='reminders_created'
    )
    title         = models.CharField(max_length=100)
    description   = models.TextField(blank=True, null=True)
    reminder_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DAILY_TASK)
    reminder_time = models.DateTimeField()
    is_completed  = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Reminder'
        ordering = ['reminder_time']

    def __str__(self):
        status = '✓' if self.is_completed else '○'
        return f"{status} [{self.reminder_type}] {self.title} — {self.senior.full_name}"


# =====================================================
# HEALTH NOTES
# =====================================================

class HealthNote(models.Model):
    note_id    = models.AutoField(primary_key=True)
    senior     = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='health_notes'
    )
    written_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='written_by',
        related_name='health_notes_written'
    )
    note_text  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Health_Note'
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.senior.full_name} by {self.written_by.full_name}"


# =====================================================
# SOS SYSTEM
# =====================================================

class SOSRequest(models.Model):
    PENDING     = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    RESOLVED    = 'RESOLVED'

    STATUS_CHOICES = [
        (PENDING,     'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (RESOLVED,    'Resolved'),
    ]

    sos_id       = models.AutoField(primary_key=True)
    senior       = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='sos_requests'
    )
    handled_by   = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='handled_by',
        related_name='sos_handled',
        null=True,
        blank=True
    )
    escalated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='escalated_by',
        related_name='sos_escalated',
        null=True,
        blank=True
    )
    escalated_at = models.DateTimeField(null=True, blank=True)
    triggered_at = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    resolved_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'SOS_Request'
        ordering = ['-triggered_at']

    def __str__(self):
        return f"SOS #{self.sos_id} — {self.senior.full_name} [{self.status}]"


# =====================================================
# COMMUNITY EVENTS
# =====================================================

class CommunityEvent(models.Model):
    event_id    = models.AutoField(primary_key=True)
    title       = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location    = models.CharField(max_length=150, blank=True, null=True)
    event_date  = models.DateTimeField()
    created_by  = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_column='created_by',
        related_name='events_created',
        null=True,
        blank=True
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Community_Event'
        ordering = ['event_date']

    def __str__(self):
        return f"{self.title} on {self.event_date.date()}"


class EventAttendance(models.Model):
    REGISTERED = 'REGISTERED'
    ATTENDED   = 'ATTENDED'
    CANCELLED  = 'CANCELLED'

    STATUS_CHOICES = [
        (REGISTERED, 'Registered'),
        (ATTENDED,   'Attended'),
        (CANCELLED,  'Cancelled'),
    ]

    event     = models.ForeignKey(
        CommunityEvent,
        on_delete=models.CASCADE,
        db_column='event_id',
        related_name='attendances'
    )
    user      = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='event_attendances'
    )
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default=REGISTERED)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Event_Attendance'
        unique_together = ('event', 'user')

    def __str__(self):
        return f"{self.user.full_name} → {self.event.title} [{self.status}]"


# =====================================================
# CHAT SYSTEM
# =====================================================

class ChatMessage(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender     = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='sender_id',
        related_name='messages_sent'
    )
    receiver   = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='receiver_id',
        related_name='messages_received'
    )
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    sent_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Chat_Message'
        ordering = ['sent_at']

    def __str__(self):
        read = '✓' if self.is_read else '○'
        return f"{read} {self.sender.full_name} → {self.receiver.full_name}"


# =====================================================
# ACTIVITY LOG
# =====================================================

class ActivityLog(models.Model):
    CAREGIVER_ACTION = 'CAREGIVER_ACTION'
    VOLUNTEER_VISIT  = 'VOLUNTEER_VISIT'

    LOG_TYPE_CHOICES = [
        (CAREGIVER_ACTION, 'Caregiver Action'),
        (VOLUNTEER_VISIT,  'Volunteer Visit'),
    ]

    log_id       = models.AutoField(primary_key=True)
    senior       = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='senior_id',
        related_name='activity_logs'
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='performed_by',
        related_name='activities_performed'
    )
    log_type     = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    action       = models.CharField(max_length=100)
    notes        = models.TextField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Activity_Log'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.log_type}] {self.action} — {self.senior.full_name}"
