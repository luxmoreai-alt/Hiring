from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health),
    path("candidates/register/", views.register),
    path("candidates/me/", views.me),
    path("rounds/<str:round_type>/start/", views.start_round),
    path("rounds/<str:round_type>/state/", views.round_state),
    path("rounds/<str:round_type>/answer/", views.submit_answer),
    path("rounds/<str:round_type>/run/", views.try_code),
    path("proctor/events/", views.proctor_event),
    path("proctor/recordings/start/", views.recording_start),
    path("proctor/recordings/<int:recording_id>/chunks/", views.recording_chunk),
    path("proctor/recordings/<int:recording_id>/finish/", views.recording_finish),
    path("staff/login/", views.admin_login),
    path("staff/dashboard/", views.admin_dashboard),
    path("staff/candidates/<uuid:candidate_id>/", views.admin_candidate),
    path("staff/candidates/<uuid:candidate_id>/resume/", views.admin_candidate_resume),
    path("staff/recordings/<int:recording_id>/", views.admin_recording),
    path("staff/candidates/<uuid:candidate_id>/delete/", views.admin_candidate_delete),
    path("staff/selected/delete-all/", views.admin_selected_delete_all),
    path("staff/candidates/<uuid:candidate_id>/reset/", views.admin_candidate_reset),
    path("staff/candidates/<uuid:candidate_id>/status/", views.admin_candidate_status),
]
