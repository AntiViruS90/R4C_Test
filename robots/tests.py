from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
import json

import io
from openpyxl import Workbook
from robots.models import Robot


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


def load_workbook_from_response(response):
    """Вспомогательная функция для загрузки книги из ответа"""
    return Workbook(io.BytesIO(response.content))


def check_workbook_headers(ws):
    """Вспомогательная функция для проверки заголовков в листе"""
    assert ws.cell(row=1, column=1).value == 'Модель'
    assert ws.cell(row=1, column=2).value == 'Версия'
    assert ws.cell(row=1, column=3).value == 'Количество за неделю'


def check_data_rows(ws, expected_data):
    """Вспомогательная функция для проверки данных в строках листа"""
    for row, (model, version, count) in enumerate(expected_data, start=2):
        assert ws.cell(row=row, column=1).value == model
        assert ws.cell(row=row, column=2).value == version
        assert ws.cell(row=row, column=3).value == count


def test_generate_robot_summary_no_robots(self):
    url = reverse('generate_robot_summary')
    with patch('robots.models.Robot.objects.filter') as mock_filter:
        mock_filter.return_value = Robot.objects.none()
        response = self.client.get(url)

    assert response.status_code == 200
    wb = load_workbook_from_response(response)
    assert len(wb.sheetnames) == 0


def test_generate_robot_summary_single_model(self):
    url = reverse('generate_robot_summary')
    Robot.objects.create(model='XR200', version='1.0', created=timezone.now())
    Robot.objects.create(model='XR200', version='1.1', created=timezone.now())
    response = self.client.get(url)

    assert response.status_code == 200
    wb = load_workbook_from_response(response)
    assert len(wb.sheetnames) == 1
    assert wb.sheetnames[0] == 'XR200'

    ws = wb.active
    check_workbook_headers(ws)
    check_data_rows(ws, [('XR200', '1.0', 1), ('XR200', '1.1', 1)])


def test_generate_robot_summary_multiple_models(self):
    url = reverse('generate_robot_summary')
    Robot.objects.create(model='XR200', version='1.0', created=timezone.now())
    Robot.objects.create(model='XR300', version='1.0', created=timezone.now())
    response = self.client.get(url)

    assert response.status_code == 200
    wb = load_workbook_from_response(response)
    assert len(wb.sheetnames) == 2
    assert 'XR200' in wb.sheetnames
    assert 'XR300' in wb.sheetnames

    ws1, ws2 = wb['XR200'], wb['XR300']
    check_workbook_headers(ws1)
    check_workbook_headers(ws2)

    check_data_rows(ws1, [('XR200', '1.0', 1)])
    check_data_rows(ws2, [('XR300', '1.0', 1)])


def test_generate_robot_summary_column_width(self):
    url = reverse('generate_robot_summary')
    Robot.objects.create(model='XR200', version='1.0', created=timezone.now())
    Robot.objects.create(model='XR200', version='1.1.1', created=timezone.now())
    Robot.objects.create(model='XR300', version='1.0.0.0', created=timezone.now())
    response = self.client.get(url)

    assert response.status_code == 200
    wb = load_workbook_from_response(response)
    ws = wb['XR200']

    assert ws.column_dimensions['A'].width == 7  # Longest in column 1: 'XR200' (5 characters)
    assert ws.column_dimensions['B'].width == 7  # Longest in column 2: '1.1.1' (5 characters)
    assert ws.column_dimensions['C'].width == 3  # Longest in column 3: '1' (1 character)


def test_generate_robot_summary_multiple_versions_single_model(self):
    url = reverse('generate_robot_summary')
    Robot.objects.create(model='XR200', version='1.0', created=timezone.now())
    Robot.objects.create(model='XR200', version='1.1', created=timezone.now())
    Robot.objects.create(model='XR200', version='2.0', created=timezone.now())
    response = self.client.get(url)

    assert response.status_code == 200
    wb = load_workbook_from_response(response)
    assert len(wb.sheetnames) == 1
    assert wb.sheetnames[0] == 'XR200'

    ws = wb.active
    check_workbook_headers(ws)
    check_data_rows(ws, [('XR200', '1.0', 1), ('XR200', '1.1', 1), ('XR200', '2.0', 1)])


def test_generate_robot_summary_exception_handling(self):
    url = reverse('generate_robot_summary')
    with patch('openpyxl.Workbook.save', side_effect=Exception("Workbook error")):
        response = self.client.get(url)

    assert response.status_code == 500
    assert response.json()['error'] == 'Unexpected error: Workbook error'