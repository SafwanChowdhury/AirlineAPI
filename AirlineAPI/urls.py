from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # Endpoint to list all available flights
    path('airline/form', views.list_flights, name='list_flights'),

    # Endpoint to reserve a seat on a flight
    path('airline/reserve', views.book_flight, name='book_flight'),

    # Endpoint to cancel a reservation
    path('airline/cancel_reservation', views.cancel_reservation, name='cancel_reservation'),

    path('airline/confirm_booking', views.confirm_reservation, name='confirm_reservation'),
]
