import crud.server_crud as scrud
import crud.user_crud as ucrud
from datetime import datetime


def test_get_all_user():
    expected_results = [
        {
            'username': 'TestUser',
            'last_activity': 'None',
            'last_activity_loc': 'None',
            'last_activity_ts': datetime(1970, 1, 1, 0, 0),
            'date_added': datetime(2021, 3, 23, 5, 45, 12)

        },
        {
            'username': 'TestUser2',
            'last_activity': 'Texting',
            'last_activity_loc': '#general',
            'last_activity_ts': datetime(2020, 12, 5, 11, 30, 5),
            'date_added': datetime(2020, 4, 3, 2, 45),
        }
    ]
    user = ucrud.get_all_users()

    assert user == expected_results
