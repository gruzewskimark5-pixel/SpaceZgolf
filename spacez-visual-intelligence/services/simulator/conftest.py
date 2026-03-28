import sys
from unittest.mock import MagicMock

# Mock dependencies that might be missing in the test environment
mock_modules = [
    "nats", "nats.js", "nats.js.errors",
    "fastapi", "fastapi.responses", "fastapi.staticfiles",
    "uvicorn", "pydantic"
]

class MockBaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

for module_name in mock_modules:
    mock_module = MagicMock()
    if module_name == "pydantic":
        mock_module.BaseModel = MockBaseModel
    sys.modules[module_name] = mock_module
