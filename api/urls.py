from django.urls import path, include

from . import views

urlpatterns = [
    path('send', views.send),
    path('endpoint', views.endpoint),
    path('departments', views.departments),
    path('bases', views.bases),
    path('laborants', views.laborants),
    path('current-user-info', views.current_user_info),
    path('directive-from', views.directive_from),
    path('users', views.users_view),
    path('user', views.user_view),
    path('user-save', views.user_save_view),
    path('user-location', views.user_location),
    path('user-get-reserve', views.user_get_reserve),
    path('statistics-tickets/types', views.statistics_tickets_types),
    path('statistics-tickets/send', views.statistics_tickets_send),
    path('statistics-tickets/get', views.statistics_tickets_get),
    path('statistics-tickets/invalidate', views.statistics_tickets_invalidate),
    path('mkb10', views.mkb10),
    path('vich_code', views.vich_code),
    path('flg', views.flg),
    path('search-template', views.search_template),
    path('load-templates', views.load_templates),
    path('get-template', views.get_template),
    path('templates/update', views.update_template),
    path('modules', views.modules_view),
    path('autocomplete', views.autocomplete),
    path('researches/', include('api.researches.urls')),
    path('patients/', include('api.patients.urls')),
    path('directions/', include('api.directions.urls')),
]
