import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AirlineAPI.settings')
from datetime import date, datetime, timedelta
from faker import Faker
from AirlineAPI.models import Location, Passenger, Reservation, Price, Plane, Flight
import random
from FlightRadar24.api import FlightRadar24API

current_date = date.today()  
fr_api = FlightRadar24API()
fake = Faker()

Passenger.objects.all().delete()
Flight.objects.all().delete()
Reservation.objects.all().delete()
Price.objects.all().delete()
Plane.objects.all().delete()
Location.objects.all().delete()

flights_info = fr_api.get_flights(airline = 'UAE')

# Create passengers
passengers = []
for i in range(50):
    passenger = Passenger.objects.create(
        email=fake.email(),
    )
    passengers.append(passenger)

# Create prices
prices = []
for i in range(10):
    price = Price.objects.create(
        price_id=i+1,
        economy_price=random.uniform(100, 500),
        business_price=random.uniform(500, 1000),
        first_class_price=random.uniform(1000, 2000),
        currency='USD'
    )
    prices.append(price)

# Create planes
planes = []
for i in range(10):
    plane = Plane.objects.create(
        plane_id=i+1,
        num_economy_seats=random.randint(100, 200),
        num_business_seats=random.randint(20, 40),
        num_first_class_seats=random.randint(10, 20)
    )
    planes.append(plane)

# Create flights with real-world data
for i, flight_info in enumerate(flights_info):
    try:
        details = fr_api.get_flight_details(flight_info.id)
        flight_info.set_flight_details(details)
        
        duration = int(flight_info.time_details['historical']['flighttime'])
        arrival = fr_api.get_airport(flight_info.destination_airport_icao)
        departure = fr_api.get_airport(flight_info.origin_airport_icao)
        
        departureCity, created = Location.objects.get_or_create(airport_id=departure['position']['region']['city'])
        arrivalCity, created = Location.objects.get_or_create(airport_id=arrival['position']['region']['city'])
        etd = str(fake.time())  
        etd_datetime = datetime.strptime(etd, "%H:%M:%S")
        flight_duration_timedelta = timedelta(seconds=duration)
        duration = str(flight_duration_timedelta)
        eta_datetime = etd_datetime + flight_duration_timedelta
        eta = eta_datetime.strftime("%H:%M:%S")
        fake_date = fake.future_date(end_date='+1y', tzinfo=None)  # Generate a random date after the current date
        plane = random.choice(planes)
        flight = Flight.objects.create(
            flight_id=i + 1,
            departure_airport=departureCity,
            arrival_airport=arrivalCity,
            airline="Emirates",
            passengers=0,
            available_seats_economy=plane.num_economy_seats,
            available_seats_business=plane.num_business_seats,
            available_seats_first=plane.num_first_class_seats,
            flight_duration=duration,
            dateOfDeparture=fake_date,
            eta=eta,
            etd=etd,
            plane=plane,
            price=random.choice(prices)
        )
    except Exception as e:
        print(f"Failed to create flight: {e}")
