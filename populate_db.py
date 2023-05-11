import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AirlineAPI.settings')
from datetime import date
from faker import Faker
from AirlineAPI.models import Location, Passenger, Reservation, Price, Plane, Flight
import random

current_date = date.today()  # Get the current date

fake = Faker()

Passenger.objects.all().delete()
Flight.objects.all().delete()
Reservation.objects.all().delete()
Price.objects.all().delete()
Plane.objects.all().delete()
Location.objects.all().delete()

# Define a list of cities and airport codes
cities = [ ('New York', 'JFK'), ('Los Angeles', 'LAX'), ('London', 'LHR'), ('Paris', 'CDG'), ('Dubai', 'DXB'), ('Abu Dhabi', 'AUH'), ('Hong Kong', 'HKG'), ('Tokyo', 'HND'), ('Toronto', 'YYZ'), ('Dehli', 'DEL')]

# Create locations
locations = []
for city, airport_id in cities:
    location = Location.objects.create(airport_id=city)
    locations.append(location)

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

flights = []
for i in range(50):
    departure_location = random.choice(locations)
    arrival_location = random.choice(locations)
    while departure_location == arrival_location:
        arrival_location = random.choice(locations)
    fake_date = fake.future_date(end_date='+1y', tzinfo=None)  # Generate a random date after the current date
    plane = random.choice(planes)
    flight = Flight.objects.create(
        flight_id=i + 1,
        departure_airport=departure_location,
        arrival_airport=arrival_location,
        airline="Emirates",
        passengers=0,
        available_seats_economy=plane.num_economy_seats,
        available_seats_business=plane.num_business_seats,
        available_seats_first=plane.num_first_class_seats,
        flight_duration=fake.time(),
        dateOfDeparture=fake_date,
        eta=fake.time(),
        etd=fake.time(),
        plane=plane,
        price=random.choice(prices)
    )
    flights.append(flight)