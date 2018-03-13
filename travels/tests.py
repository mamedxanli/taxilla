from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from carmakes.models import Manufacturer, Car
from travels.models import Travel
from travels.forms import TravelForm
from vehicles.models import Vehicle


class TravelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Test database is created and populated here
        """
        cls.user = get_user_model().objects.create_user('prez',
            'dev@null.az', 'onlyme')
        cls.user2 = get_user_model().objects.create_user('mohprez',
            'noreply@random.az', 'allofus')
        cls.user_driver = get_user_model().objects.create_user('rusik',
            'avtosh@mail.az', 'ceshka777', is_driver=True)
        cls.user_driver2 = get_user_model().objects.create_user('aliheydar',
            'taxi_baku@mail.ru', 'nol_on_bir', is_driver=True)
        cls.today = timezone.now()
        make = Manufacturer.objects.create(
            make='Mercedes-Benz'
        )
        car = Car.objects.create(
            manufacturer=make,
            model="C Klass"
        )
        make2 = Manufacturer.objects.create(
            make='Lada'
        )
        car2 = Car.objects.create(
            manufacturer=make2,
            model="21011"
        )
        vehicle = Vehicle.objects.create(
            car_id='001',
            car_instance=car,
            registration_number='10-GJ-777',
        )
        vehicle.drivers.add(cls.user_driver)
        vehicle2 = Vehicle.objects.create(
            car_id='002',
            car_instance=car2,
            registration_number='85-AA-356',
        )
        vehicle2.drivers.add(cls.user_driver2)
        cls.travel = Travel.objects.create(
            traveller=cls.user,
            pickup='39 Zivarbey Ahmadbeyov Street, Baku, Azerbaijan',
            dropoff='Samad Vurghun, Baku, Azerbaijan',
            date_time=cls.today,
            notes='I will give you dostoyniy otvet',
            assigned_vehicle=vehicle,
        )
        cls.travel2 = Travel.objects.create(
            traveller=cls.user2,
            pickup='Ahmedli',
            dropoff='Zevin teref',
            date_time=cls.today,
            notes='6 manat verirem',
            assigned_vehicle=vehicle2,
        )

    def test_travel_form(self):
        """
        This tests the TravelForm
        """
        form_data = {
            'pickup': '28th May Street, Baku, Azerbaijan',
            'dropoff': 'Samad Vurghun, Baku, Azerbaijan',
            'no_of_passengers': 3,
            'pickup_data': '{"address": "a"}',
            'dropoff_data': '{"address": "b"}',
            'date_time': self.today,
            }
        form = TravelForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_travel_create(self):
        """
        This test is for creating a travel
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        response = self.client.post('/requests/new', {
            'pickup': '28th May Street, Baku, Azerbaijan',
            'dropoff': 'Samad Vurghun, Baku, Azerbaijan',
            'no_of_passengers': 3,
            'pickup_data': '{"address": "a"}',
            'dropoff_data': '{"address": "b"}',
            'date_time': self.today.date(),
            })
        self.assertRedirects(response, '/requests/3/')
        response = self.client.post('/requests/new', {
            'pickup': 'Prospekt',
            'dropoff': 'Savetski',
            'no_of_passengers': 3,
            'pickup_data': '{"address": "a"}',
            'dropoff_data': '{"address": "b"}',
            'date_time': self.today.date(),
            }, follow=True)
        self.assertTemplateUsed(response, 'travels/travel_detail.html')
        self.assertContains(response, 'Savetski')
        self.client.logout()

    def test_travels_list(self):
        """
        This test is for getting a list of travels
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        new_travel = Travel.objects.create(
            traveller=self.user,
            pickup='28th May Street, Baku, Azerbaijan',
            dropoff='56 Rustam Rustamov, Baku, Azerbaijan',
            date_time=self.today,
            no_of_passengers=3,
        )
        new_travel.save()
        response = self.client.get('/requests/')
        self.assertEqual(len(response.context['object_list']), 2)
        self.assertContains(response, '39')
        self.assertTemplateUsed(response, 'travels/travel_list.html')
        self.client.logout()

    def test_anonymous_travels_list(self):
        """
        This test is to check redirection if user not logged in
        """
        response = self.client.get('/requests/')
        self.assertRedirects(response, '/accounts/login/?next=/requests/')

    def test_travel_detail(self):
        """
        This test is for viewing a travel
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        response = self.client.get('/requests/{}/'.format(self.travel.id))
        self.assertContains(response, 'Pickup Location')
        self.assertContains(response, 'Destination')
        self.assertContains(response, 'Additional Notes')
        self.assertNotContains(response, 'what is dead may never die')
        self.assertTemplateUsed(response, 'travels/travel_detail.html')
        self.client.logout()

    def test_failed_travel_create(self):
        """
        This test is for raising an exception if error in travel form
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        response = self.client.post('/requests/new', {
            'pickup': '28th May Street, Baku, Azerbaijan',
            'dropoff': '',
            'pickup_data': '{"address": "a"}',
            'dropoff_data': '{"address": "b"}',
            'date_time': self.today.date(),
            'no_of_passengers': 3,
            })
        self.assertFormError(response, 'form', 'dropoff',
            ('This field is required.'))

    def test_travel_delete(self):
        """
        This test is for deleting a travel
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        response = self.client.post('/requests/new', {
            'pickup': '28th May Street, Baku, Azerbaijan',
            'dropoff': 'Samad Vurghun, Baku, Azerbaijan',
            'pickup_data': '{"address": "a"}',
            'dropoff_data': '{"address": "b"}',
            'date_time': self.today.date(),
            'no_of_passengers': 3,
            }, follow=True)
        self.assertRedirects(response, '/requests/5/')
        response = self.client.post(
            '/requests/delete/{}/'.format(self.travel.id),
            follow=True)
        self.assertRedirects(response, '/requests/')
        self.client.logout()

    def test_user_view_another_request(self):
        """
        Tests to see if user is able to see another user's request
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        response = self.client.get('/requests/{}/'.format(self.travel2.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_user_edit_another_request(self):
        """
        Tests to see if user is able to edit another user's request
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        response = self.client.get('/requests/edit/{}/'.format(self.travel2.id))
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/requests/edit/{}'.format(
                self.travel2.id), {
            'pickup': 'Prospekt',
            'dropoff': 'Savetski',
            'no_of_passengers': 3,
            'pickup_data': '{"address": "a"}',
            'dropoff_data': '{"address": "b"}',
            'date_time': self.today.date(),
            }, follow=True)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_user_delete_another_request(self):
        """
        Tests to see if user is able to delete another user's request
        """
        login = self.client.login(username='prez', password='onlyme')
        self.assertTrue(login)
        response = self.client.get('/requests/delete/{}/'.format(
            self.travel2.id), follow=True)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_driver_preview(self):
        """
        Tests to see if driver is able to preview requests list and detail
        """
        login = self.client.login(username='rusik', password='ceshka777')
        self.assertTrue(login)
        requests = self.client.get('/requests/vehicle_list/')
        self.assertEqual(len(requests.context['object_list']), 1)
        response = self.client.get('/requests/preview/{}/'.format(
            self.travel.id))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_driver_take_task_and_release(self):
        """
        Tests if driver can take a travel request assigned to a vehicle
        they operate and then release it
        """
        login = self.client.login(username='rusik', password='ceshka777')
        self.assertTrue(login)
        requests = self.client.get('/requests/vehicle_list/')
        self.assertEqual(len(requests.context['object_list']), 1)
        response = self.client.get('/requests/preview/{}/'.format(
            self.travel.id))
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/requests/driver_assign/{}/'.format(
            self.travel.id), follow=True)
        self.assertRedirects(response, '/requests/driver_detail/{}/'.format(
            self.travel.id))
        # Checks if vehicle_list is empty
        requests = self.client.get('/requests/vehicle_list/')
        self.assertEqual(len(requests.context['object_list']), 0)
        response = self.client.post('/requests/driver_release/{}/'.format(
            self.travel.id), follow=True)
        self.assertRedirects(response, '/requests/vehicle_list/')
        self.client.logout()

    # check if driver could see the details of a request w/o driver or with a different driver
    def test_driver_view_request_same_vehicle_not_assigned(self):
        """
        Tests if a driver could see a request which is for the vehicle
        but not yet assigned to anyone
        """
        login = self.client.login(username='rusik', password='ceshka777')
        self.assertTrue(login)
        requests = self.client.get('/requests/vehicle_list/')
        self.assertEqual(len(requests.context['object_list']), 1)
        response = self.client.get('/requests/driver_detail/{}/'.format(
            self.travel.id))
        self.assertEqual(response.status_code, 403)


    def test_driver_view_another_request(self):
        """
        Tests to see if driver is able to see another driver's request
        """
        login = self.client.login(username='rusik', password='ceshka777')
        self.assertTrue(login)
        response = self.client.get('/requests/driver_detail/{}/'.format(
            self.travel2.id))
        self.assertEqual(response.status_code, 403)
        self.client.logout()
