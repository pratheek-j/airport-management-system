from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('index', views.index),
    path('index-flight', views.index_flight),
    path('account-bookings', views.account_bookings),
    path('account-delete', views.account_delete),
    path('account-profile', views.account_profile, name="accountprofile"),
    path('account-settings', views.account_settings),
    path('add-listing-minimal', views.add_listing_minimal),
    path('add-listing', views.add_listing),
    path('update-listing-minimal', views.update_listing_minimal, name="update-emp"),
    path('admin-agent-detail', views.admin_agent_detail),
    path('admin-agent-list', views.admin_agent_list),
    path('admin-dashboard', views.admin_dashboard, name="airport-index"),
    path('admin-guest-list', views.admin_guest_list, name='emp_list'),
    path('agent-bookings', views.agent_bookings),
    path('agent-dashboard', views.agent_dashboard, name="airline-index"),
    path('agent-listings', views.agent_listings),
    path('flight-detail/<int:FL_ID>/<int:travelers>/confirm', views.booking_confirm),
    path('flight-detail/<int:FL_ID>/<int:travelers>/booking', views.flight_booking),
    path('flight-detail-raw', views.flight_detail_raw),
    path('flight-detail/<int:FL_ID>/<int:travelers>/', views.flight_detail),
    path('flight-list', views.flight_list),
    path('listing-added', views.listing_added),
    path('error', views.error, name="error"),
    path('listing-added2', views.listing_added2),
    path('sign-in', views.sign_in, name="login"),
    path('sign-up', views.sign_up, name="signup"),
    path('logout', views.log_out, name='logout'),
]
