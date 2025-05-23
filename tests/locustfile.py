from locust import HttpUser, task, between, events
import time

class PDFUploadAndTrackUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def upload_and_track(self):
        with open("sa.pdf", "rb") as f:
            files = {"file": ("sa.pdf", f, "application/pdf")}
            response = self.client.post("/upload", files=files)
            if response.status_code != 200:
                return
            file_id = response.json().get("file_id")
            if not file_id:
                return

            start = time.time()
            status = ""
            while status != "completed":
                status_response = self.client.get(f"/status/{file_id}")
                if status_response.status_code != 200:
                    break
                status = status_response.json().get("status")
                if status == "completed":
                    break
                time.sleep(1)
            end = time.time()
            total_time = end - start

            # Custom metric: record end-to-end processing time
            events.request.fire(
                request_type="PROCESS",
                name="end_to_end_processing",
                response_time=total_time * 1000,  # ms
                response_length=0,
                exception=None
            )