import requests
import json
import pytest

url = 'https://api.matchbook.com/bpapi/rest/security/session'

# payload with user credentials
payload = {
    "username": 'QA_ITW3',
    "password": 'NQqaT2cMC0'
}
# customized payload for invalid login test
custom_payload = {
    "username": "admin",
    "password": "admin"
}
header = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'api-doc-test-client'
}
# creating a post request and storing session token in a variable for later use in the test cases
post_resp = requests.post(url, data=json.dumps(payload), headers=header)
session_tkn = post_resp.json()['session-token']
set_cookie_value = post_resp.headers["set-cookie"]


@pytest.mark.regression
def test_001_verify_login():
    # test to verify the login is successful or not
    assert post_resp.status_code == 200


@pytest.mark.regression
def test_002_user_id_match():
    # test to verify the user ID is correct
    user_id = post_resp.json()['user-id']
    assert user_id == 426553


@pytest.mark.regression
def test_003_get_account_info():
    # test to ensure if get account info API is returning the valid response
    custom_header = {'Accept': 'application/json', 'User-Agent': 'api-doc-test-client', 'session-token': session_tkn}
    get_resp = requests.get(url, headers=custom_header)
    assert get_resp.status_code == 200


# function for partitioning the string obtained from cookie parameter
def substring_after(s, delimx):
    return s.partition(delimx)[2]


@pytest.mark.regression
def test_004_check_cookie_expiry_time():
    # test to verify the cookie expiration max age is set to 6 hours
    y = substring_after(set_cookie_value, 'Max-Age=')
    split_str = y.split(";", 1)
    assert split_str.__getitem__(0) == '21600'


@pytest.mark.regression
def test_005_logout():
    # test to verify the logout works as expected
    custom_header = {'Accept': 'application/json', 'User-Agent': 'api-doc-test-client', 'session-token': session_tkn}
    del_resp = requests.delete(url, headers=custom_header)
    assert del_resp.status_code == 200


@pytest.mark.regression
def test_006_logout_clicked_the_second_time():
    # test to ensure when logout link is hit the second time it provides appropriate response
    custom_header = {'Accept': 'application/json', 'User-Agent': 'api-doc-test-client', 'session-token': session_tkn}
    del_resp = requests.delete(url, headers=custom_header)
    try:
        err_msg = del_resp.json()['errors'][0]['messages']
        assert err_msg[0] == 'Authentication Required'
        assert del_resp.status_code == 401
    except KeyError:
        print("key error occurred")


@pytest.mark.regression
def test_007_check_account_after_logout():
    # test to verify when get account details is called without login it gives the excepted response with
    # authorization failure
    custom_header = {'Accept': 'application/json', 'User-Agent': 'api-doc-test-client'}
    get_resp = requests.get("https://api.matchbook.com/edge/rest/account", headers=custom_header)
    err_msg = get_resp.json()['errors'][0]['messages']
    assert get_resp.status_code == 401
    assert err_msg[0] == 'You are not authorised to access this resource. Login to continue.'


@pytest.mark.regression
def test_008_invalid_credentials():
    # test to verify if the user inputs invalid credentials the login should failed with the expected response
    custom_post_resp = requests.post(url, data=json.dumps(custom_payload), headers=header)
    assert custom_post_resp.status_code == 400

# https://sherryhsu.medium.com/session-vs-token-based-authentication-11a6c5ac45e4

# https://www.geeksforgeeks.org/session-vs-token-based-authentication/#:~:text=The%20main%20difference%20is%20session,one%20the%20client%20stores%20them.
