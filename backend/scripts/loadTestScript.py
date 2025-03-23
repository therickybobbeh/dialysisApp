from locust import HttpUser, task, between
import uuid

class PDManagementUser(HttpUser):
    wait_time = between(1, 3)  # Simulate user wait time between requests
    token = None

    def on_start(self):
        """Executed when a simulated user starts a test run."""
        self.register_user()
        self.token = self.login_user()

    def register_user(self):
        """Register a test user."""
        user_data = {
            "name": "LoadTest User",
            "email": f"loadtest_{uuid.uuid4()}@example.com",
            "password": "testpass",
            "role": "patient"
        }
        self.client.post("/auth/register", json=user_data)

    def login_user(self):
        """Log in as the test user and retrieve a JWT token."""
        login_data = {"email": "loadtest@example.com", "password": "testpass"}
        response = self.client.post("/auth/token", json=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None

    @task
    def submit_dialysis_session(self):
        """Simulate a patient submitting a dialysis session."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            session_data = {
                "pre_weight": 70.0,
                "post_weight": 68.5,
                "pre_bp": "120/80",
                "post_bp": "110/75",
                "effluent": 1.2
            }
            patient_id = str(uuid.uuid4())
            self.client.post(f"/patients/{patient_id}/dialysis-session", json=session_data, headers=headers)

    @task
    def view_dialysis_history(self):
        """Simulate a patient viewing their dialysis history."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            patient_id = str(uuid.uuid4())
            self.client.get(f"/patients/{patient_id}/dialysis-history", headers=headers)

    @task
    def provider_dashboard_access(self):
        """Simulate a provider accessing the dashboard."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/providers/dashboard", headers=headers)

# To run the test, use the command: locust -f locust_load_test.py --host=http://localhost:8000
