import requests

password = "mysecretpassword"
requests.post("http://example.com/api", data={"user": "admin", "password": password})
