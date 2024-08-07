from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import SlidingToken
from .models import Video, TimeStamp
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from .models import ChangeRequest
User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser12',
            'email': 'testemail1@example.com',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.token = str(SlidingToken.for_user(self.user))

    def test_create_user(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser123',
            'email': 'testemail12@example.com',
            'password': 'testpassword123'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='testuser123').exists())

    def test_get_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(reverse('user'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)

    def test_update_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        new_data = {'email': 'newemail@example.com'}
        response = self.client.post(reverse('user_update'), new_data, format='json')
        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')

    @patch('aromastream.views.send_confirm_code')  
    def test_update_password(self, mock_send_confirm_code):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        password_data = {'password': 'newpassword123'}

        response = self.client.post(reverse('password_reset'), password_data, format='json')
        self.assertEqual(response.status_code, 204)

        change_request = ChangeRequest.objects.filter(user=self.user, field='password').exists()
        self.assertTrue(change_request)

        mock_send_confirm_code.assert_called_once()

    def test_update_password_confirmation(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        new_password = 'newpassword123'
        self.client.post(reverse('password_reset'), {'password': new_password}, format='json')

        confirmation_code = ChangeRequest.objects.get(user=self.user, field='password').confirm_code

        response = self.client.post(reverse('password_reset_confirm'), {'confirm_code': confirmation_code}, format='json')
        self.assertEqual(response.status_code, 204)

        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': new_password
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        



class TimeStampTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser2', password='testpassword')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.token = str(SlidingToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.video = Video.objects.create(title='test video', description='test description', views=0)
        self.timestamp_data = {'video': self.video.id, 'aroma': 'A', 'moment': '12:34:56'}

        self.user.is_staff = True

        
    def test_create_timestamp(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(reverse('timestamp_create'), self.timestamp_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(TimeStamp.objects.filter(video=self.video, aroma='A', moment='12:34:56').exists())

    def test_get_timestamps(self):
        TimeStamp.objects.create(video=self.video, aroma='A', moment='12:34:56')
        response = self.client.get(reverse('timestamp_list', args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['aroma'], 'A')
        self.assertEqual(response.data['results'][0]['moment'], '12:34:56')


class VideoTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser3', password='testpassword')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.token = str(SlidingToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.video_data = {
            'title': 'test video',
            'description': 'test description',
            'file': SimpleUploadedFile('test.mp4', b'file_content', content_type='video/mp4')
        }
        self.video = Video.objects.create(title='test video', description='test description', views=0)

        
        
    def test_create_video(self):
        response = self.client.post(reverse('videos'), self.video_data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Video.objects.filter(title='test video').exists())

    def test_get_videos(self):
        response = self.client.get(reverse('videos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'test video')

    def test_get_video_detail(self):
        response = self.client.get(reverse('video_detail', args=[self.video.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], self.video.title)
        self.assertEqual(response.data['description'], self.video.description)

class SearchVideoTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = str(SlidingToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.video = Video.objects.create(title='searchable video', description='searchable description', views=0)

    def test_search_videos(self):
        response = self.client.get(reverse('search_video'), {'query': 'searchable'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'searchable video')

    def test_search_videos_no_results(self):
        response = self.client.get(reverse('search_video'), {'query': 'nonexistent'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

