from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from carmakes.models import Manufacturer, Car
from travels.models import Travel
from vehicles.models import Vehicle


@override_settings(CELERY_ALWAYS_EAGER=True)
class VehicleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Test database is created and populated here
        """
        cls.driver1 = get_user_model().objects.create_user('mushfig',
            'mexanik@bakililar.az', 'kalbilator', phone='0557324598',
            is_driver=True)
        cls.driver2 = get_user_model().objects.create_user('orik',
            'orxan555@tuning.az', 'basovik', phone='0503183223',
            is_driver=True)
        cls.driver3 = get_user_model().objects.create_user('kelenter',
            'qarpiz@yemish.az', 'bagban', phone='0125641278',
            is_driver=True)
        cls.just_user = get_user_model().objects.create_user('mamed',
            'mamed_kachok@chat.az', 'qozdaq', phone='0518765412')
        make = Manufacturer.objects.create(
            make='BMW'
        )
        car = Car.objects.create(
            manufacturer=make,
            model="318"
        )
        cls.vehicle = Vehicle.objects.create(
            car_id='001',
            car_instance=car,
            year=2001,
            engine=1800,
            fuel_type=0,
            number_of_passenger_seats=3,
            description='Minor scratches on right door',
            registration_number='10-SP-318',
        )
        cls.vehicle.drivers.add(cls.driver1)
        cls.vehicle.drivers.add(cls.driver2)
        cls.vehicle_no_drivers = Vehicle.objects.create(
            car_id='002',
            car_instance=car,
            year=2003,
            engine=3200,
            fuel_type=0,
            number_of_passenger_seats=3,
            description='Getteze, garajda saxlamisham.',
            registration_number='10-DP-155',
        )
        cls.today = timezone.now()
        cls.travel = Travel.objects.create(
            traveller=cls.just_user,
            pickup='Poxlu Dere',
            dropoff='Sangachal',
            date_time=cls.today,
            notes='Nisye kitaba yaz',
        )

    def test_get_active_driver(self):
        """
        Tests to retrieve the active driver string
        """
        self.vehicle.active_driver = self.driver1
        self.assertEqual('mushfig, 0557324598', self.vehicle.get_active_driver())

    def test_str(self):
        """
        Tests string method of Vehicle
        """
        self.assertEqual(('001 - BMW 318 - 10-SP-318'), str(self.vehicle))

    def test_get_driver_str(self):
        """
        Tests private method which generates driver name and their phone
        """
        self.assertEqual('mushfig, 0557324598',
            self.vehicle.get_driver_str(self.vehicle.drivers.filter(
                username='mushfig')[0]))


    def test_get_guest_str(self):
        """
        Tests guest compatible Vehicle str representation
        """
        self.assertEqual('BMW 318 10-SP-318', self.vehicle.get_guest_str())

    def test_get_forbidden_user(self):
        """
        Tests if regular user gets permission denied while trying to
        issue a location update call
        """
        login = self.client.login(username='mamed', password='qozdaq')
        self.assertTrue(login)
        response = self.client.get(
            '/vehicles/vehicle_location_update/{}/{}'.format(self.vehicle.id,
            self.travel.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_get_forbidden_no_driver(self):
        """
        Tests if a driver user gets forbidden to the vehicle location update
        when there are no drivers set
        """
        login = self.client.login(username='mushfig', password='kalbilator')
        self.assertTrue(login)
        response = self.client.get(
            '/vehicles/vehicle_location_update/{}/{}'.format(
            self.vehicle_no_drivers.id, self.travel.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_get_wrong_driver(self):
        """
        Tests if driver could update the location of another
        vehicle
        """
        login = self.client.login(username='kelenter', password='bagban')
        self.assertTrue(login)
        response = self.client.get(
            '/vehicles/vehicle_location_update/{}/{}'.format(
            self.vehicle.id, self.travel.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_get_location_update(self):
        """
        Tests successfull call to celery task about the location update
        """
        login = self.client.login(username='mushfig', password='kalbilator')
        self.assertTrue(login)
        response = self.client.get(
            '/vehicles/vehicle_location_update/{}/{}'.format(
            self.vehicle.id, self.travel.id), {'lat': '49', 'lng': '50'})
        self.assertEqual(response.status_code, 200)
        self.client.logout()
