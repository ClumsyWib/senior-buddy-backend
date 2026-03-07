from django.urls import path
from . import views

# =====================================================
# SENIOR BUDDY — App URLs
# All routes are prefixed with /api/ from project urls.py
# =====================================================

urlpatterns = [

    # --------------------------------------------------
    # AUTH
    # --------------------------------------------------
    path('login/',    views.login_view,    name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/',   views.logout_view,   name='logout'),
    path('me/',       views.me_view,       name='me'),
    path('my-seniors/', views.my_seniors, name='my-seniors'),

    # --------------------------------------------------
    # USERS (Admin only)
    # --------------------------------------------------
    path('users/',        views.UserListView.as_view(),   name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),

    # --------------------------------------------------
    # PROFILES
    # --------------------------------------------------
    path('seniors/',    views.SeniorProfileListView.as_view(),   name='senior-list'),
    path('seniors/<int:pk>/', views.SeniorProfileDetailView.as_view(), name='senior-detail'),
    path('caregivers/', views.CaregiverProfileListView.as_view(), name='caregiver-list'),
    path('family/',     views.FamilyProfileListView.as_view(),    name='family-list'),
    path('volunteers/', views.VolunteerProfileListView.as_view(), name='volunteer-list'),

    path('my-profile/senior/', views.my_senior_profile, name='my-senior-profile'),
    path('my-profile/caregiver/', views.my_caregiver_profile, name='my-caregiver-profile'),
    path('my-profile/family/',    views.my_family_profile,    name='my-family-profile'),
    path('my-profile/volunteer/', views.my_volunteer_profile, name='my-volunteer-profile'),

    # --------------------------------------------------
    # ASSIGNMENTS
    # --------------------------------------------------
    path('assignments/caregivers/',  views.SeniorCaregiverListView.as_view(), name='assign-caregiver'),
    path('assignments/family/',      views.SeniorFamilyListView.as_view(),    name='assign-family'),
    path('assignments/volunteers/',  views.SeniorVolunteerListView.as_view(), name='assign-volunteer'),

    # --------------------------------------------------
    # DOCTORS
    # --------------------------------------------------
    path('doctors/',              views.DoctorListView.as_view(),       name='doctor-list'),
    path('doctors/<int:pk>/',     views.DoctorDetailView.as_view(),     name='doctor-detail'),
    path('assignments/doctors/',  views.SeniorDoctorListView.as_view(), name='assign-doctor'),

    # --------------------------------------------------
    # REMINDERS
    # --------------------------------------------------
    path('reminders/',          views.ReminderListView.as_view(),   name='reminder-list'),
    path('reminders/<int:pk>/', views.ReminderDetailView.as_view(), name='reminder-detail'),

    # --------------------------------------------------
    # HEALTH NOTES
    # --------------------------------------------------
    path('health-notes/', views.HealthNoteListView.as_view(), name='health-note-list'),

    # --------------------------------------------------
    # SOS
    # --------------------------------------------------
    path('sos/',                          views.SOSListView.as_view(),  name='sos-list'),
    path('sos/trigger/',                  views.trigger_sos,            name='sos-trigger'),
    path('sos/<int:sos_id>/respond/',     views.respond_sos,            name='sos-respond'),
    path('sos/<int:sos_id>/resolve/',     views.resolve_sos,            name='sos-resolve'),
    path('sos/<int:sos_id>/escalate/',    views.escalate_sos,           name='sos-escalate'),

    # --------------------------------------------------
    # COMMUNITY EVENTS
    # --------------------------------------------------
    path('events/',                          views.CommunityEventListView.as_view(),   name='event-list'),
    path('events/<int:pk>/',                 views.CommunityEventDetailView.as_view(), name='event-detail'),
    path('events/<int:event_id>/attend/',    views.EventAttendanceListView.as_view(),  name='event-attend'),

    # --------------------------------------------------
    # CHAT
    # --------------------------------------------------
    path('chat/<int:user_id>/',       views.ChatListView.as_view(),   name='chat'),
    path('chat/<int:user_id>/read/',  views.mark_messages_read,       name='chat-read'),
    path('chat/unread-count/', views.unread_message_count, name='unread-count'),

    # --------------------------------------------------
    # ACTIVITY LOG
    # --------------------------------------------------
    path('activity/', views.ActivityLogListView.as_view(), name='activity-log'),
]
