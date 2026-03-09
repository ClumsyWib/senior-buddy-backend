from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User, Role, UserRole,
    SeniorProfile, CaregiverProfile, FamilyProfile, VolunteerProfile,
    SeniorCaregiver, SeniorFamily, SeniorVolunteer,
    Doctor, SeniorDoctor,
    Reminder, HealthNote,
    SOSRequest,
    CommunityEvent, EventAttendance,
    ChatMessage, ActivityLog,
)


# =====================================================
# SENIOR BUDDY — serializers.py
# Converts Django models → JSON for the Android app
# =====================================================


# =====================================================
# AUTH SERIALIZERS
# =====================================================

class LoginSerializer(serializers.Serializer):
    """Handles login — takes email + password, returns user."""
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been disabled.')
        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Creates a new user account."""
    password  = serializers.CharField(write_only=True, min_length=6)
    role_name = serializers.ChoiceField(
        choices=['SENIOR', 'CAREGIVER', 'FAMILY', 'VOLUNTEER'],
        write_only=True
    )

    class Meta:
        model  = User
        fields = ['full_name', 'email', 'phone', 'password', 'role_name']

    def validate_phone(self, value):
        import re
        if not re.match(r'^\+?[0-9]{7,15}$', value):
            raise serializers.ValidationError(
                'Enter a valid phone number.'
                )
        return value

    def create(self, validated_data):
        from django.db import transaction #<- Handles rollback if any step fails
        role_name = validated_data.pop('role_name')
        password  = validated_data.pop('password')

         # ─────────────────────────────────────────────────────────────────
        # transaction.atomic() ensures ALL of the following happen together:
        # create user → assign role → create profile
        # If ANY step fails, NOTHING is saved to the database.
        # This prevents orphan users from being left behind.
        # ─────────────────────────────────────────────────────────────────
        with transaction.atomic():

            # 1. Create the user
            user = User.objects.create(
                username=validated_data['email'],  # Set username = email for authentication
                email=validated_data['email'],
                phone=validated_data['phone'],
                full_name=validated_data['full_name'],
                password=password 
            )
            user.phone = validated_data['phone']
            user.full_name = validated_data['full_name']
            user.save()

            # 2. Assign the role to user
            role = Role.objects.get(role_name=role_name)
            UserRole.objects.create(user=user, role=role)

            # 3. Create role-specific profile
            # if this fails for any reason, user + role are rolled back and NOT saved to the database
            if role_name == 'SENIOR':
                SeniorProfile.objects.create(senior=user)
            elif role_name == 'CAREGIVER':
                CaregiverProfile.objects.create(caregiver=user)
            elif role_name == 'FAMILY':
                FamilyProfile.objects.create(family=user)
            elif role_name == 'VOLUNTEER':
                VolunteerProfile.objects.create(volunteer=user)

        return user

            

# =====================================================
# USER SERIALIZERS
# =====================================================

class UserSerializer(serializers.ModelSerializer):
    """Basic user info — safe to return in API responses."""
    roles = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'full_name', 'email', 'phone', 'is_active', 'created_at', 'roles']

    def get_roles(self, obj):
        return list(
            UserRole.objects.filter(user=obj)
            .values_list('role__role_name', flat=True)
        )


# =====================================================
# PROFILE SERIALIZERS
# =====================================================

class SeniorProfileSerializer(serializers.ModelSerializer):
    senior_name = serializers.CharField(source='senior.full_name', read_only=True)

    class Meta:
        model  = SeniorProfile
        fields = ['senior_id', 'senior_name', 'age', 'medical_history', 'emergency_contact']


class CaregiverProfileSerializer(serializers.ModelSerializer):
    caregiver_name = serializers.CharField(source='caregiver.full_name', read_only=True)

    class Meta:
        model  = CaregiverProfile
        fields = ['caregiver_id', 'caregiver_name', 'qualification', 'experience_years']


class FamilyProfileSerializer(serializers.ModelSerializer):
    family_name = serializers.CharField(source='family.full_name', read_only=True)

    class Meta:
        model  = FamilyProfile
        fields = ['family_id', 'family_name', 'relation']


class VolunteerProfileSerializer(serializers.ModelSerializer):
    volunteer_name = serializers.CharField(source='volunteer.full_name', read_only=True)

    class Meta:
        model  = VolunteerProfile
        fields = ['volunteer_id', 'volunteer_name', 'skills', 'availability', 'is_verified']


# =====================================================
# RELATIONSHIP SERIALIZERS
# =====================================================

class SeniorCaregiverSerializer(serializers.ModelSerializer):
    senior_name    = serializers.CharField(source='senior.full_name',    read_only=True)
    caregiver_name = serializers.CharField(source='caregiver.full_name', read_only=True)

    class Meta:
        model  = SeniorCaregiver
        fields = ['id', 'senior', 'senior_name', 'caregiver', 'caregiver_name',
                  'is_primary', 'assigned_at']
        read_only_fields = ['assigned_at']


class SeniorFamilySerializer(serializers.ModelSerializer):
    senior_name = serializers.CharField(source='senior.full_name', read_only=True)
    family_name = serializers.CharField(source='family.full_name', read_only=True)

    class Meta:
        model  = SeniorFamily
        fields = ['id', 'senior', 'senior_name', 'family', 'family_name', 'added_at']
        read_only_fields = ['added_at']


class SeniorVolunteerSerializer(serializers.ModelSerializer):
    senior_name    = serializers.CharField(source='senior.full_name',    read_only=True)
    volunteer_name = serializers.CharField(source='volunteer.full_name', read_only=True)

    class Meta:
        model  = SeniorVolunteer
        fields = ['id', 'senior', 'senior_name', 'volunteer', 'volunteer_name',
                  'assigned_by', 'assigned_at']
        read_only_fields = ['assigned_at']


# =====================================================
# DOCTOR SERIALIZERS
# =====================================================

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Doctor
        fields = ['doctor_id', 'full_name', 'specialization', 'phone',
                  'hospital_name', 'added_by']
        read_only_fields = ['added_by']


class SeniorDoctorSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.full_name',      read_only=True)
    senior_name = serializers.CharField(source='senior.full_name',      read_only=True)
    hospital    = serializers.CharField(source='doctor.hospital_name',  read_only=True)
    phone       = serializers.CharField(source='doctor.phone',          read_only=True)

    class Meta:
        model  = SeniorDoctor
        fields = ['id', 'senior', 'senior_name', 'doctor', 'doctor_name',
                  'hospital', 'phone', 'is_primary', 'added_at']
        read_only_fields = ['added_at']


# =====================================================
# REMINDER SERIALIZER
# =====================================================

class ReminderSerializer(serializers.ModelSerializer):
    senior_name     = serializers.CharField(source='senior.full_name',     read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model  = Reminder
        fields = ['reminder_id', 'senior', 'senior_name', 'created_by',
                  'created_by_name', 'title', 'description', 'reminder_type',
                  'reminder_time', 'is_completed', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        # Automatically set created_by to the logged-in user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


# =====================================================
# HEALTH NOTE SERIALIZER
# =====================================================

class HealthNoteSerializer(serializers.ModelSerializer):
    senior_name     = serializers.CharField(source='senior.full_name',     read_only=True)
    written_by_name = serializers.CharField(source='written_by.full_name', read_only=True)

    class Meta:
        model  = HealthNote
        fields = ['note_id', 'senior', 'senior_name', 'written_by',
                  'written_by_name', 'note_text', 'created_at']
        read_only_fields = ['written_by', 'created_at']

    def create(self, validated_data):
        validated_data['written_by'] = self.context['request'].user
        return super().create(validated_data)


# =====================================================
# SOS SERIALIZER
# =====================================================

class SOSRequestSerializer(serializers.ModelSerializer):
    senior_name      = serializers.CharField(source='senior.full_name',       read_only=True)
    handled_by_name  = serializers.CharField(source='handled_by.full_name',   read_only=True)
    escalated_by_name = serializers.CharField(source='escalated_by.full_name', read_only=True)

    class Meta:
        model  = SOSRequest
        fields = ['sos_id', 'senior', 'senior_name', 'handled_by', 'handled_by_name',
                  'escalated_by', 'escalated_by_name', 'escalated_at',
                  'triggered_at', 'status', 'resolved_at']
        read_only_fields = ['triggered_at']


# =====================================================
# COMMUNITY EVENT SERIALIZERS
# =====================================================

class EventAttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model  = EventAttendance
        fields = ['id', 'event', 'user', 'user_name', 'status', 'joined_at']
        read_only_fields = ['user', 'joined_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommunityEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    attendee_count  = serializers.SerializerMethodField()

    class Meta:
        model  = CommunityEvent
        fields = ['event_id', 'title', 'description', 'location', 'event_date',
                  'created_by', 'created_by_name', 'created_at', 'attendee_count']
        read_only_fields = ['created_by', 'created_at']

    def get_attendee_count(self, obj):
        return obj.attendances.exclude(status='CANCELLED').count()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


# =====================================================
# CHAT SERIALIZER
# =====================================================

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name   = serializers.CharField(source='sender.full_name',   read_only=True)
    receiver_name = serializers.CharField(source='receiver.full_name', read_only=True)

    class Meta:
        model  = ChatMessage
        fields = ['message_id', 'sender', 'sender_name', 'receiver',
                  'receiver_name', 'message', 'is_read', 'sent_at']
        read_only_fields = ['sender', 'sent_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


# =====================================================
# ACTIVITY LOG SERIALIZER
# =====================================================

class ActivityLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.full_name', read_only=True)
    senior_name       = serializers.CharField(source='senior.full_name',       read_only=True)

    class Meta:
        model  = ActivityLog
        fields = ['log_id', 'senior', 'senior_name', 'performed_by',
                  'performed_by_name', 'log_type', 'action', 'notes', 'created_at']
        read_only_fields = ['performed_by', 'created_at']

    def create(self, validated_data):
        validated_data['performed_by'] = self.context['request'].user
        return super().create(validated_data)
