'''This should test the configuration of SQLAlchemy'''

# Third Party modules
import pytest
from dotenv import dotenv_values

@pytest.mark.parametrize("dev_env_value", dotenv_values(".env").items())
def test_env_values(dev_env_value):
    assert dev_env_value[1] is not None and len(dev_env_value[1]) != 0
