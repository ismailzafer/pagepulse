from locust import HttpUser, task, between

class PagePulseUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_pdf(self):
        with open("sample.pdf", "rb") as f:
            files = {'file': ("sample.pdf", f, "application/pdf")}
            self.client.post("/upload/", files=files)

    @task
    def check_status(self):
        # Burada örnek bir file_id kullanılıyor, test için bir dosya yükleyip gerçek id ile deneyebilirsin
        file_id = "test-file-id"
        self.client.get(f"/status/{file_id}")