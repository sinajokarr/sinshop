import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db 
def test_user_registration():
    client = APIClient()
    payload = {
        "phone_number": "09123456789",
        "password": "SuperSecretPassword123"
    }

    response = client.post('/api/account/register/', payload)

    assert response.status_code == 201
    
    assert User.objects.filter(phone_number="09123456789").exists() == True
    
