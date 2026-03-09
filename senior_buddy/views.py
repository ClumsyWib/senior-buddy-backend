from rest_framework              import generics, status
from rest_framework.decorators  import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response    import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import (
    User, SeniorProfile, CaregiverProfile, FamilyProfile, VolunteerProfile,
    SeniorCaregiver, SeniorFamily, SeniorVolunteer,
    Doctor, SeniorDoctor,
    Reminder, HealthNote, SOSRequest,
    CommunityEvent, EventAttendance,
    ChatMessage, ActivityLog,
)
from .serializers import (
    LoginSerializer, RegisterSerializer, UserSerializer,
    SeniorProfileSerializer, CaregiverProfileSerializer,
    FamilyProfileSerializer, VolunteerProfileSerializer,
    SeniorCaregiverSerializer, SeniorFamilySerializer, SeniorVolunteerSerializer,
    DoctorSerializer, SeniorDoctorSerializer,
    ReminderSerializer, HealthNoteSerializer, SOSRequestSerializer,
    CommunityEventSerializer, EventAttendanceSerializer,
    ChatMessageSerializer, ActivityLogSerializer,
)
from .permissions import (
    IsAdmin, IsAdminOrFamily, IsAdminOrCaregiver,
    IsCaregiverOrFamily, IsNotVolunteer, IsSeniorOrCaregiverOrFamily,
)


# =====================================================
# SENIOR BUDDY — views.py
# All API endpoints
# =====================================================


# =====================================================
# AUTH ENDPOINTS
# =====================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST /api/login/
    Body: { "email": "...", "password": "..." }
    Returns: { "access": "...", "refresh": "...", "user": {...} }

    The Android app saves the access token and sends it
    in every future request as:
    Header → Authorization: Bearer <access_token>
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
    )

    user    = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)

    return Response({
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user':    UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        if 'email' in serializer.errors:
            return Response(
                {'error': 'An account with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if 'phone' in serializer.errors:
            phone_error = str(serializer.errors['phone'][0])
            if 'valid phone' in phone_error:
                return Response(
                    {'error': phone_error},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': 'An account with this phone number already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'user':    UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token so it can't be reused.
    """
    try:
        token = RefreshToken(request.data['refresh'])
        token.blacklist()
        return Response({'message': 'Logged out successfully.'})
    except Exception:
        return Response({'error': 'Invalid token.'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /api/me/
    Returns the currently logged-in user's details.
    Android uses this to know which role dashboard to show.
    """
    return Response(UserSerializer(request.user).data)


# =====================================================
# USER ENDPOINTS (Admin only)
# =====================================================

class UserListView(generics.ListAPIView):
    """GET /api/users/ — List all users (Admin only)"""
    queryset           = User.objects.all().order_by('-created_at')
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class UserDetailView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/users/<id>/ — View or update a user (Admin only)"""
    queryset           = User.objects.all()
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# =====================================================
# PROFILE ENDPOINTS
# =====================================================

class SeniorProfileListView(generics.ListCreateAPIView):
    """
    GET  /api/seniors/        — List all seniors
    POST /api/seniors/        — Create a senior profile
    Only Admin, Caregiver, Family can see this.
    Volunteers are blocked (no medical data access).
    """
    queryset           = SeniorProfile.objects.select_related('senior').all()
    serializer_class   = SeniorProfileSerializer
    permission_classes = [IsAuthenticated, IsNotVolunteer]


class SeniorProfileDetailView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/seniors/<id>/"""
    queryset           = SeniorProfile.objects.all()
    serializer_class   = SeniorProfileSerializer
    permission_classes = [IsAuthenticated, IsNotVolunteer]


class CaregiverProfileListView(generics.ListCreateAPIView):
    """GET/POST /api/caregivers/ — Admin can see all caregivers, others cannot see this endpoint"""
    queryset           = CaregiverProfile.objects.select_related('caregiver').all()
    serializer_class   = CaregiverProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class FamilyProfileListView(generics.ListCreateAPIView):
    """GET/POST /api/family/"""
    queryset           = FamilyProfile.objects.select_related('family').all()
    serializer_class   = FamilyProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class VolunteerProfileListView(generics.ListCreateAPIView):
    """GET/POST /api/volunteers/ — Admin can see all volunteers, others cannot see this endpoint"""
    queryset           = VolunteerProfile.objects.select_related('volunteer').all()
    serializer_class   = VolunteerProfileSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


# =====================================================
# RELATIONSHIP ENDPOINTS
# =====================================================

class SeniorCaregiverListView(generics.ListCreateAPIView):
    """GET/POST /api/assignments/caregivers/"""
    queryset           = SeniorCaregiver.objects.select_related('senior', 'caregiver').all()
    serializer_class   = SeniorCaregiverSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFamily]


class SeniorFamilyListView(generics.ListCreateAPIView):
    """GET/POST /api/assignments/family/"""
    queryset           = SeniorFamily.objects.select_related('senior', 'family').all()
    serializer_class   = SeniorFamilySerializer
    permission_classes = [IsAuthenticated, IsAdminOrFamily]


class SeniorVolunteerListView(generics.ListCreateAPIView):
    """GET/POST /api/assignments/volunteers/"""
    queryset           = SeniorVolunteer.objects.select_related('senior', 'volunteer').all()
    serializer_class   = SeniorVolunteerSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFamily]

    def perform_create(self, serializer):
        volunteer_id = serializer.validated_data['volunteer'].pk

        # Warn but don't block if volunteer is unverified
        from .models import VolunteerProfile
        warning = None
        try:
            profile = VolunteerProfile.objects.get(volunteer_id=volunteer_id)
            if not profile.is_verified:
                warning = 'This volunteer has not been verified yet. Assignment saved.'
        except VolunteerProfile.DoesNotExist:
            warning = 'Volunteer profile not found. Assignment saved anyway.'

        instance = serializer.save()

        # Attach warning to instance so create() can pick it up
        if warning:
            instance._warning = warning

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        data = serializer.data

        # Inject warning into response if volunteer is unverified
        if hasattr(instance, '_warning'):
            data['warning'] = instance._warning

        return Response(data, status=status.HTTP_201_CREATED)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unassign_caregiver(request, pk):
    """
    DELETE /api/assignments/caregivers/<pk>/
    Admin or Family can unassign a caregiver from a senior.
    """
    roles = list(request.user.userrole_set.values_list('role__role_name', flat=True))
    if not any(role in roles for role in ['ADMIN', 'FAMILY']):
        return Response(
            {'error': 'Only Admin or Family can unassign a caregiver.'},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        assignment = SeniorCaregiver.objects.get(pk=pk)
    except SeniorCaregiver.DoesNotExist:
        return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

    assignment.delete()
    return Response({'message': 'Caregiver unassigned successfully.'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unassign_family(request, pk):
    """
    DELETE /api/assignments/family/<pk>/
    Admin or Family can remove a family member link.
    """
    roles = list(request.user.userrole_set.values_list('role__role_name', flat=True))
    if not any(role in roles for role in ['ADMIN', 'FAMILY']):
        return Response(
            {'error': 'Only Admin or Family can unassign a family member.'},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        assignment = SeniorFamily.objects.get(pk=pk)
    except SeniorFamily.DoesNotExist:
        return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

    assignment.delete()
    return Response({'message': 'Family member unassigned successfully.'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unassign_volunteer(request, pk):
    """
    DELETE /api/assignments/volunteers/<pk>/
    Admin or Family can unassign a volunteer from a senior.
    """
    roles = list(request.user.userrole_set.values_list('role__role_name', flat=True))
    if not any(role in roles for role in ['ADMIN', 'FAMILY']):
        return Response(
            {'error': 'Only Admin or Family can unassign a volunteer.'},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        assignment = SeniorVolunteer.objects.get(pk=pk)
    except SeniorVolunteer.DoesNotExist:
        return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)

    assignment.delete()
    return Response({'message': 'Volunteer unassigned successfully.'}, status=status.HTTP_200_OK)

# =====================================================
# DOCTOR ENDPOINTS
# =====================================================

class DoctorListView(generics.ListCreateAPIView):
    """GET/POST /api/doctors/"""
    queryset           = Doctor.objects.all()
    serializer_class   = DoctorSerializer
    permission_classes = [IsAuthenticated, IsNotVolunteer]

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/doctors/<id>/"""
    queryset           = Doctor.objects.all()
    serializer_class   = DoctorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrFamily]


class SeniorDoctorListView(generics.ListCreateAPIView):
    """GET/POST /api/assignments/doctors/"""
    queryset           = SeniorDoctor.objects.select_related('senior', 'doctor').all()
    serializer_class   = SeniorDoctorSerializer
    permission_classes = [IsAuthenticated, IsNotVolunteer]

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


# =====================================================
# REMINDER ENDPOINTS
# =====================================================

class ReminderListView(generics.ListCreateAPIView):
    """
    GET  /api/reminders/       — List reminders
    POST /api/reminders/       — Create a reminder
    Senior/Caregiver/Family can create.
    Each user only sees reminders relevant to them.
    """
    serializer_class   = ReminderSerializer
    permission_classes = [IsAuthenticated, IsSeniorOrCaregiverOrFamily]

    def get_queryset(self):
        user  = self.request.user
        roles = list(user.userrole_set.values_list('role__role_name', flat=True))

        if 'SENIOR' in roles:
            # Senior sees their own reminders
            return Reminder.objects.filter(senior=user)
        elif 'CAREGIVER' in roles:
            # Caregiver sees reminders for their assigned seniors
            senior_ids = SeniorCaregiver.objects.filter(
                caregiver=user
            ).values_list('senior_id', flat=True)
            return Reminder.objects.filter(senior_id__in=senior_ids)
        elif 'FAMILY' in roles:
            # Family sees reminders for their linked seniors
            senior_ids = SeniorFamily.objects.filter(
                family=user
            ).values_list('senior_id', flat=True)
            return Reminder.objects.filter(senior_id__in=senior_ids)
        elif 'ADMIN' in roles:
            return Reminder.objects.all()
        return Reminder.objects.none()


class ReminderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/reminders/<id>/"""
    queryset           = Reminder.objects.all()
    serializer_class   = ReminderSerializer
    permission_classes = [IsAuthenticated]


# =====================================================
# HEALTH NOTE ENDPOINTS
# =====================================================

class HealthNoteListView(generics.ListCreateAPIView):
    """
    GET  /api/health-notes/    — List health notes
    POST /api/health-notes/    — Write a note
    Volunteers cannot see this.
    """
    serializer_class   = HealthNoteSerializer
    permission_classes = [IsAuthenticated, IsNotVolunteer]

    def perform_create(self, serializer):
        # Only Caregiver or Family can write notes
        roles = list(self.request.user.userrole_set.values_list('role__role_name', flat=True))
        from rest_framework.exceptions import PermissionDenied
        if not any(role in roles for role in ['CAREGIVER', 'FAMILY']):
            raise PermissionDenied('Only caregivers or family members can write health notes.')
        serializer.save(writer=self.request.user)


# =====================================================
# SOS ENDPOINTS
# =====================================================

class SOSListView(generics.ListAPIView):
    """GET /api/sos/ — List SOS requests"""
    serializer_class   = SOSRequestSerializer
    permission_classes = [IsAuthenticated, IsNotVolunteer]

    def get_queryset(self):
        user  = self.request.user
        roles = list(user.userrole_set.values_list('role__role_name', flat=True))

        if 'SENIOR' in roles:
            return SOSRequest.objects.filter(senior=user)
        elif 'CAREGIVER' in roles:
            # Only show SOS requests for their assigned seniors, Not all pending SOS requests
            senior_ids = SeniorCaregiver.objects.filter(
                caregiver=user
            ).values_list('senior_id', flat=True)
            return SOSRequest.objects.filter(
                senior_id__in=senior_ids,
                status__in=['PENDING', 'IN_PROGRESS']
            )
        elif 'FAMILY' in roles:
            senior_ids = SeniorFamily.objects.filter(
                family=user
            ).values_list('senior_id', flat=True)
            return SOSRequest.objects.filter(senior_id__in=senior_ids)
        elif 'ADMIN' in roles:
            return SOSRequest.objects.all()
        return SOSRequest.objects.none()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_sos(request):
    """
    POST /api/sos/trigger/
    Senior triggers an emergency SOS alert.
    No body needed — uses the logged-in user as the senior.
    """
    # Only seniors can trigger SOS
    roles = list(request.user.userrole_set.values_list('role__role_name', flat=True))
    if 'SENIOR' not in roles:
        return Response(
            {'error': 'Only seniors can trigger an SOS.'},
            status=status.HTTP_403_FORBIDDEN
        )
    sos = SOSRequest.objects.create(
        senior=request.user,
        status='PENDING'
    ) 
    return Response(
        SOSRequestSerializer(sos).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def respond_sos(request, sos_id):
    """
    PATCH /api/sos/<id>/respond/
    Caregiver/Admin picks up the SOS.
    Sets handled_by to the current user and status to IN_PROGRESS.
    """
    try:
        sos = SOSRequest.objects.get(sos_id=sos_id)
    except SOSRequest.DoesNotExist:
        return Response({'error': 'SOS not found.'}, status=404)
    
    if sos.status == 'RESOLVED':
        return Response(
            {'error': 'This SOS has already been resolved.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    sos.handled_by = request.user
    sos.status     = 'IN_PROGRESS'
    sos.save()
    return Response(SOSRequestSerializer(sos).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def resolve_sos(request, sos_id):
    """
    PATCH /api/sos/<id>/resolve/
    Marks the SOS as RESOLVED with a timestamp.
    """
    try:
        sos = SOSRequest.objects.get(sos_id=sos_id)
    except SOSRequest.DoesNotExist:
        return Response({'error': 'SOS not found.'}, status=404)
    
    if sos.status == 'RESOLVED':
        return Response(
            {'error': 'This SOS is already resolved.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    sos.status      = 'RESOLVED'
    sos.resolved_at = timezone.now()
    sos.save()
    return Response(SOSRequestSerializer(sos).data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def escalate_sos(request, sos_id):
    """
    PATCH /api/sos/<id>/escalate/
    Family member escalates an unresolved SOS.
    """
    try:
        sos = SOSRequest.objects.get(sos_id=sos_id)
    except SOSRequest.DoesNotExist:
        return Response({'error': 'SOS not found.'}, status=404)

    sos.escalated_by = request.user
    sos.escalated_at = timezone.now()
    sos.save()
    return Response(SOSRequestSerializer(sos).data)


# =====================================================
# COMMUNITY EVENT ENDPOINTS
# =====================================================

class CommunityEventListView(generics.ListCreateAPIView):
    """GET/POST /api/events/"""
    serializer_class   = CommunityEventSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show upcoming events, past events are filtered out
        return CommunityEvent.objects.filter(
            date__gte=timezone.now()
        ).order_by('event_date')


class CommunityEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/events/<id>/"""
    queryset           = CommunityEvent.objects.all()
    serializer_class   = CommunityEventSerializer
    permission_classes = [IsAuthenticated]


class EventAttendanceListView(generics.ListCreateAPIView):
    """GET/POST /api/events/<id>/attend/"""
    serializer_class   = EventAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EventAttendance.objects.filter(event_id=self.kwargs['event_id'])

    def perform_create(self, serializer):
        event = CommunityEvent.objects.get(event_id=self.kwargs['event_id'])
        serializer.save(user=self.request.user, event=event)


# =====================================================
# CHAT ENDPOINTS
# =====================================================

class ChatListView(generics.ListCreateAPIView):
    """
    GET  /api/chat/<user_id>/  — Get conversation with a specific user
    POST /api/chat/<user_id>/  — Send a message to that user
    """
    serializer_class   = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        other_user_id = self.kwargs['user_id']
        me = self.request.user
        # Returns all messages between me and the other user
        return (
            ChatMessage.objects.filter(
                sender_id=me.pk, receiver_id=other_user_id
            ) | ChatMessage.objects.filter(
                sender_id=other_user_id, receiver_id=me.pk
            )
        ).order_by('sent_at')

    def perform_create(self, serializer):
        serializer.save(
            sender=self.request.user,
            receiver_id=self.kwargs['user_id']
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_messages_read(request, user_id):
    """
    PATCH /api/chat/<user_id>/read/
    Marks all messages from this user as read.
    """
    ChatMessage.objects.filter(
        sender_id=user_id,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    return Response({'message': 'Messages marked as read.'})


# =====================================================
# ACTIVITY LOG ENDPOINTS
# =====================================================

class ActivityLogListView(generics.ListCreateAPIView):
    """
    GET  /api/activity/   — View activity logs
    POST /api/activity/   — Log an activity (Caregiver or Volunteer)
    """
    serializer_class   = ActivityLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user  = self.request.user
        roles = list(user.userrole_set.values_list('role__role_name', flat=True))

        if 'SENIOR' in roles:
            # Seniors see all logs related to them
            return ActivityLog.objects.filter(senior=user)
        elif 'CAREGIVER' in roles or 'VOLUNTEER' in roles:
            # Show logs they personally performed
            return ActivityLog.objects.filter(performed_by=user)
        elif 'FAMILY' in roles:
            # Show logs for their linked seniors
            senior_ids = SeniorFamily.objects.filter(
                family=user
            ).values_list('senior_id', flat=True)
            return ActivityLog.objects.filter(senior_id__in=senior_ids)
        elif 'ADMIN' in roles:
            return ActivityLog.objects.all()
        return ActivityLog.objects.none()
    
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_senior_profile(request):
    """
    GET /api/my-profile/senior/  — Get my senior profile
    PUT /api/my-profile/senior/  — Update my senior profile
    """
    try:
        profile = SeniorProfile.objects.get(senior=request.user)
    except SeniorProfile.DoesNotExist:
        return Response(
            {'error': 'Senior profile not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if request.method == 'GET':
        return Response(SeniorProfileSerializer(profile).data)

    serializer = SeniorProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_caregiver_profile(request):
    try:
        profile = CaregiverProfile.objects.get(caregiver=request.user)
    except CaregiverProfile.DoesNotExist:
        return Response({'error': 'Caregiver profile not found.'}, status=404)

    if request.method == 'GET':
        return Response(CaregiverProfileSerializer(profile).data)

    serializer = CaregiverProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_family_profile(request):
    try:
        profile = FamilyProfile.objects.get(family=request.user)
    except FamilyProfile.DoesNotExist:
        return Response({'error': 'Family profile not found.'}, status=404)

    if request.method == 'GET':
        return Response(FamilyProfileSerializer(profile).data)

    serializer = FamilyProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def my_volunteer_profile(request):
    try:
        profile = VolunteerProfile.objects.get(volunteer=request.user)
    except VolunteerProfile.DoesNotExist:
        return Response({'error': 'Volunteer profile not found.'}, status=404)

    if request.method == 'GET':
        return Response(VolunteerProfileSerializer(profile).data)

    serializer = VolunteerProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_seniors(request):
    """
    GET /api/my-seniors/
    Returns only the seniors linked to the logged-in user.
    Works for Caregiver, Family, and Volunteer.
    """
    user  = request.user
    roles = list(user.userrole_set.values_list('role__role_name', flat=True))

    if 'CAREGIVER' in roles:
        senior_ids = SeniorCaregiver.objects.filter(
            caregiver=user
        ).values_list('senior_id', flat=True)
    elif 'FAMILY' in roles:
        senior_ids = SeniorFamily.objects.filter(
            family=user
        ).values_list('senior_id', flat=True)
    elif 'VOLUNTEER' in roles:
        senior_ids = SeniorVolunteer.objects.filter(
            volunteer=user
        ).values_list('senior_id', flat=True)
    else:
        return Response({'error': 'Only Caregiver, Family, or Volunteer can use this endpoint.'}, status=403)

    seniors = SeniorProfile.objects.filter(senior_id__in=senior_ids)
    return Response(SeniorProfileSerializer(seniors, many=True).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_message_count(request):
    """
    GET /api/chat/unread-count/
    Returns total unread messages and a breakdown per sender.
    Android uses this to show notification badges.
    """
    unread = ChatMessage.objects.filter(
        receiver=request.user,
        is_read=False
    )

    total = unread.count()

    # Breakdown by sender so Android can show badge per conversation
    from django.db.models import Count
    per_sender = unread.values(
        'sender_id',
        'sender__full_name'
    ).annotate(count=Count('message_id'))

    breakdown = [
        {
            'sender_id':   item['sender_id'],
            'sender_name': item['sender__full_name'],
            'unread':      item['count']
        }
        for item in per_sender
    ]

    return Response({
        'total_unread': total,
        'breakdown':    breakdown
    })
