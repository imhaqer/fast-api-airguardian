from src.fast_api_airguardian.task import is_in_nfz
from src.fast_api_airguardian.main import app
from src.fast_api_airguardian.main import get_drones
from httpx import AsyncClient
from fastapi.testclient import TestClient
import httpx
import pytest

client = TestClient(app)

@pytest.mark.parametrize("position_x, position_y, expected", [
    (110, 100, True),
    (0,0, True),
    (-1001, 200, False),
    (1000,1000, False),
    (999, 999, False),
    (200, 999, False),
    (25355345, 8999999, False),
    (-656, -15, True),
    (1000, 0.1, False),
    (0, 1000, True),
    (1000, 1, False)
])

def test_is_in_nfz(position_x, position_y, expected):
    assert is_in_nfz(position_x, position_y) == expected


# @pytest.mark.asyncio no need for async 
def test_get_drones(mocker, fake_response, fake_data):
    mocker.patch("src.fast_api_airguardian.main.httpx.AsyncClient.get",
                return_value=fake_response)
    response = client.get("/drones") # sync call
    assert response.status_code == 200
    assert response.json() == fake_response.json() #compare


def test_get_drone_fail(mocker, fake_error_response):
    mocker.patch("src.fast_api_airguardian.main.httpx.AsyncClient.get",
                return_value=fake_error_response)
    response = client.get("/drones") # sync call
    assert response.status_code == 503
    assert response.json() == {"detail": "Drone data unavailable"}


def test_invalid_drone(mocker, fake_invalid_response):
    mocker.patch("src.fast_api_airguardian.main.httpx.AsyncClient.get",
                return_value=fake_invalid_response)
    response = client.get("/drones") # sync call
    assert response.status_code == 500
    assert response.json() == {"detail": "Invalid drone data received"}