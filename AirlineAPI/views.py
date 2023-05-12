from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from datetime import timedelta
from .models import Flight, Passenger, Reservation
from django.db import models
from django.utils import timezone

import json

@api_view(['GET'])
@parser_classes([JSONParser])
def list_flights(request):
    cancel_old_reservations()
    data = JSONParser().parse(request)

    departure_date = data.get('dateOfDeparture', '')
    city_of_departure = data.get('cityOfDeparture', '')
    city_of_arrival = data.get('cityOfArrival', '')
    available_seats = data.get('totalNoOfTickets', '')

    flights = Flight.objects.all()
    if departure_date:
        flights = flights.filter(dateOfDeparture__gte=departure_date)
    if city_of_departure:
        flights = flights.filter(departure_airport=city_of_departure)
    if city_of_arrival:
        flights = flights.filter(arrival_airport=city_of_arrival)
    
    # Filter flights where combined available seats are greater than noOfSeats
    if available_seats:
        flights = flights.annotate(total_seats=models.F('available_seats_economy') + models.F('available_seats_business') + models.F('available_seats_first')).filter(total_seats__gt=available_seats)



    flightsList = {}
    for flight in flights:
        flightDict = {        
            'airline': flight.airline,
            'cityOfDeparture': flight.departure_airport.airport_id,
            'cityOfArrival': flight.arrival_airport.airport_id,
            'flightDuration': flight.flight_duration,
            'dateOfDeparture': flight.dateOfDeparture,
            'timeOfDeparture': flight.etd,
            'timeOfArrival': flight.eta,
            'seats':{
                'noOfEconomy': flight.available_seats_economy,
                'noOfBusiness': flight.available_seats_business,
                'noOfFirstClass': flight.available_seats_first,
            },
            'price': {
            'priceOfEconomy': flight.price.economy_price,
            'priceOfBusiness': flight.price.business_price,
            'priceOfFirstClass': flight.price.first_class_price,
            }
        }
        flight_id = '03' + str(flight.flight_id)
        flightsList[flight_id] = flightDict
    if not flights.exists():
        return JsonResponse({"message": "No Flights Available"}, safe=False)
    
    return JsonResponse(flightsList, safe=False)

@api_view(['POST'])
def book_flight(request):
    cancel_old_reservations()
    data = json.loads(request.body)
    flight_id = data.get('flightID')
    flight_id = flight_id[2:]
    no_of_seats = data.get('seats', 0)
    no_of_seats_economy = no_of_seats.get('noOfEconomy', 0)
    no_of_seats_business = no_of_seats.get('noOfBusiness', 0)
    no_of_seats_first = no_of_seats.get('noOfFirstClass', 0)


    flight = get_object_or_404(Flight, flight_id=flight_id)

    if (no_of_seats_economy != "" and no_of_seats_economy is not None and flight.available_seats_economy is not None and flight.available_seats_economy < no_of_seats_economy) or \
    (no_of_seats_business != "" and no_of_seats_business is not None and flight.available_seats_business is not None and flight.available_seats_business < no_of_seats_business) or \
    (no_of_seats_first != "" and no_of_seats_first is not None and flight.available_seats_first is not None and flight.available_seats_first < no_of_seats_first):
        return JsonResponse({"message": "Not enough seats available for this flight."}, status=400)

    
    if no_of_seats_economy is None or no_of_seats_economy == "":
        no_of_seats_economy = 0
    if no_of_seats_business is None or no_of_seats_business == "":
        no_of_seats_business = 0
    if no_of_seats_first is None or no_of_seats_first == "":
        no_of_seats_first = 0

    passenger_id=data.get('email')
    
    passenger, created = Passenger.objects.get_or_create(email=passenger_id)

    max_reservation_id = Reservation.objects.aggregate(max_reservation_id=models.Max('reservation_id'))['max_reservation_id']

    # Calculate the next reservation ID
    next_reservation_id = max_reservation_id + 1 if max_reservation_id is not None else 1

    reservation = Reservation.objects.create(
        reservation_id=next_reservation_id,
        flight=flight,
        passenger=passenger,
        num_seats_economy=no_of_seats_economy,
        num_seats_business=no_of_seats_business,
        num_seats_first=no_of_seats_first,
        confirmed_status=False,
        time_started=timezone.now(),
    )

    flight.available_seats_economy -= no_of_seats_economy
    flight.available_seats_business -= no_of_seats_business
    flight.available_seats_first -= no_of_seats_first
    flight.passengers += (no_of_seats_economy + no_of_seats_business + no_of_seats_first)
    flight.save()
    reservation_id = '03' + str(reservation.reservation_id)

    response_data = {
        'bookingID': reservation_id
    }
    return JsonResponse(response_data)

@api_view(['POST'])
def confirm_reservation(request):
    cancel_old_reservations()
    data = json.loads(request.body)
    reservation_id = data.get('bookingID')
    reservation_id = reservation_id[2:]
    total_price = data.get('price')
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)

    flight = reservation.flight
    seat_price_economy = flight.price.economy_price
    seat_price_business = flight.price.business_price
    seat_price_first = flight.price.first_class_price
    calculated_price = (seat_price_economy * reservation.num_seats_economy) + (seat_price_business * reservation.num_seats_business) + (seat_price_first * reservation.num_seats_first)

    if calculated_price != total_price:
        return JsonResponse({"message": "Price does not match."}, status=400)
    
    reservation.confirmed_status = True
    reservation.save()

    status = (calculated_price == total_price)
    response_data = {"status": "success" if status else "failed"}
    return JsonResponse(response_data)


@api_view(['POST'])
def cancel_reservation(request):
    cancel_old_reservations()
    data = json.loads(request.body)
    reservation_id = data.get('bookingID')
    reservation_id = reservation_id[2:]
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    reservation.delete()

    flight = reservation.flight
    flight.available_seats_economy += reservation.num_seats_economy
    flight.available_seats_business += reservation.num_seats_business
    flight.available_seats_first += reservation.num_seats_first
    flight.save()

    status = True
    response_data = {"status": "success" if status else "failed"}
    return JsonResponse(response_data)

def cancel_old_reservations():
    current_time = timezone.now()
    fifteen_minutes_ago = current_time - timedelta(minutes=15)
    old_reservations = Reservation.objects.filter(time_started__lte=fifteen_minutes_ago)
    for reservation in old_reservations:
        if reservation.confirmed_status == False:
            flight = reservation.flight
            flight.available_seats_economy += reservation.num_seats_economy
            flight.available_seats_business += reservation.num_seats_business
            flight.available_seats_first += reservation.num_seats_first
            flight.save()
            reservation.delete()