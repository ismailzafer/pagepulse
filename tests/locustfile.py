from locust import HttpUser, task, between

class PDFUploadUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def upload_pdf(self):
        with open("sa.pdf", "rb") as f:
            files = {"file": ("sa.pdf", f, "application/pdf")}
            self.client.post("/upload", files=files)