from django.urls import path
from . import views
from django.contrib.auth.views import login, logout

urlpatterns = [
    #path('', views.home),
    path('login/', login, {'template_name': 'rsvp/login.html'}),
    path('logout/', logout, {'template_name': 'rsvp/logout.html'}),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('add_event/', views.add_event, name='add_event'),
    path('<int:event_id>/', views.add_user, name='add_user'),
    path('<int:event_id>/accept_invite', views.accept_invite, name='accept_invite'),
    path('<int:event_id>/event_detail/', views.event_detail, name = 'event_detail'),
    path('<int:event_id>/expire_question/', views.expire_question, name = 'expire_question'),
    path('<int:event_id>/event_edit/', views.event_edit, name = 'event_edit'),
    path('<int:event_id>/question/',views.question_create, name='question'),
    path('<int:event_id>/<int:guest_val>/question_index', views.index, name='index'),
    path('<int:event_id>/<int:question_id>/<int:guest_val>/question_detail', views.question_detail, name='question_detail'),
    path('<int:event_id>/<int:question_id>/<int:guest_val>/question_vote', views.question_vote, name='question_vote'),
    path('<int:event_id>/<int:question_id>/change/',views.question_change, name='change'),
    path('<int:event_id>/<int:question_id>/<int:guest_val>/answeressay', views.question_essay, name='answeressay'),
    path('<int:event_id>/answer_detail', views.answer_detail, name='answer_detail'),
    path('<int:event_id>/view_event_detail', views.view_event_detail, name='view_event_detail'),
    path('<int:event_id>/<int:guest_id>/answer_sheet', views.answer_sheet, name='answer_sheet'),
]
