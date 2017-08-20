import pytest
import finance

TEST_FILES = ["test_1.csv","test_2.csv"]
TEST_DATA_DIRECTORY = "test_data"
TEST_DIRECTORY = "test"

@pytest.fixture(scope="session")
def get_finance():
    return finance.Finance("test")