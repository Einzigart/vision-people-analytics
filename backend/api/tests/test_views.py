import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_api_overview():
    client = APIClient()
    url = reverse('api-overview')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_cors_headers():
    client = APIClient()
    url = reverse('api-overview')
    origin = 'http://localhost:3000'
    response = client.get(url, HTTP_ORIGIN=origin)
    assert response.status_code == 200
    assert response['Access-Control-Allow-Origin'] == origin
