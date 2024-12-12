from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
import json


class CreateRobotTestCase(TestCase):

    def test_create_robot_success(self):
        url = reverse('create_robot')
        data = {
            "model": "XR100",
            "version": "1.0",
            "created": timezone.now().isoformat()
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.json())
        self.assertIn('id', response.json())
        self.assertEqual(
            response.json()['message'],
            'Robot created succesfully'
        )

    def test_create_robot_missing_fields(self):
        url = reverse('create_robot')

        data = {
            "version": "1.0",
            "created": timezone.now().isoformat()
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Missing required fields')

    def test_create_robot_invalid_date_format(self):
        url = reverse('create_robot')

        data = {
            "model": "XR100",
            "version": "1.0",
            "created": "invalid_date_format"
        }
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid date format')

    def test_create_robot_invalid_json(self):
        url = reverse('create_robot')

        data = "{model: XR100, version: 1.0, created: '2024-12-12T00:00:00'}"
        response = self.client.post(url, data=data, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid JSON format')

    def test_create_robot_database_error(self):
        url = reverse('create_robot')

        data = {
            "model": "XR100",
            "version": "1.0",
            "created": timezone.now().isoformat()
        }

        with patch('robots.models.Robot.objects.create', side_effect=DatabaseError("Database is down")):
            response = self.client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error'], "Database error: Database is down")

    def test_create_robot_invalid_method(self):
        url = reverse('create_robot')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json()['error'], "Only POST method is allowed")
