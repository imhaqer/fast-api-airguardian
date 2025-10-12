import pytest
import httpx

class FakeResponse:
    def json(self):
        return [
            {
                "id": "drone-123",
                "owner_id": 1,
                "x": 300,
                "y": -180,
                "z": 26
            }
        ]
    def raise_for_status(self):
        pass

class FakeErrorResponse:
    def raise_for_status(self):
        raise httpx.HTTPStatusError(
            message="503 Server Error",
            request=None,
            response=None,
        )
    def json(self):
        return {}

class FakeInvalidResponse:
    def json(self):
        return [
            {
                "id": "drone-123",
                "owner_id": "INVALID",  # bad type (should be int)
                "x": 300,
                "y": -180,
                "z": 26
            }
        ]
    def raise_for_status(self):
        pass

@pytest.fixture
def fake_response():
    return FakeResponse()

@pytest.fixture
def fake_error_response():
    return FakeErrorResponse()

@pytest.fixture
def fake_invalid_response():
    return FakeInvalidResponse()
