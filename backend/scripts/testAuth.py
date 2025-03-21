import requests

url = "http://localhost:8004/auth/token"
data = {
    #"username": "drsmith@example.com",
    "username": "alice@example.com",
    "password": "password123"
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

response = requests.post(url, data=data, headers=headers)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
