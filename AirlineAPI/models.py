from django.db import models

class Location(models.Model):
    airport_id = models.CharField(max_length=100, primary_key=True)

class Passenger(models.Model):
    email = models.CharField(max_length=100, primary_key=True)

class Reservation(models.Model):
    reservation_id = models.IntegerField(primary_key=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE)
    num_seats_economy = models.IntegerField()
    num_seats_business = models.IntegerField()
    num_seats_first = models.IntegerField()
    confirmed_status = models.BooleanField()
    time_started = models.DateTimeField()

class Price(models.Model):
    price_id = models.IntegerField(primary_key=True)
    economy_price = models.FloatField()
    business_price = models.FloatField()
    first_class_price = models.FloatField()
    currency = models.CharField(max_length=100)

class Plane(models.Model):
    plane_id = models.IntegerField(primary_key=True)
    num_economy_seats = models.IntegerField()
    num_business_seats = models.IntegerField()
    num_first_class_seats = models.IntegerField()

class Flight(models.Model):
    flight_id = models.IntegerField(primary_key=True)
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)
    price = models.ForeignKey(Price, on_delete=models.CASCADE)
    departure_airport = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='departure_flights')
    arrival_airport = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='arrival_flights')
    airline = models.CharField(max_length=100)
    passengers = models.IntegerField(default = 0)
    available_seats_economy = models.IntegerField()
    available_seats_business = models.IntegerField()
    available_seats_first = models.IntegerField()
    flight_duration = models.TimeField()
    dateOfDeparture = models.DateField()
    eta = models.TimeField()
    etd = models.TimeField()
