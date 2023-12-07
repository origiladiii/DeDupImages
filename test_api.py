import requests
import json

# Constants
BASE_URL = "http://localhost:8000"
VALID_IMAGE_PATH = "/Users/origiladi/PycharmProjects/PolarisData/‏״IMG_3453״ - גדול.jpeg"  # Update this path to a valid image file
INVALID_IMAGE_PATH = "/Users/origiladi/PycharmProjects/PolarisData/‏״IM_3453״ - גדול.jpeg"  # Update this path to a non-existent file

def test_api():
    # Test /howto endpoint
    response = requests.get(f"{BASE_URL}/howto")
    print("/howto Response:", response.json())

    # Test /is_alive endpoint
    response = requests.get(f"{BASE_URL}/is_alive")
    print("/is_alive Response:", response.json())

    # Test valid input for /process endpoint
    valid_input = json.dumps({"image path": VALID_IMAGE_PATH})
    response = requests.post(f"{BASE_URL}/process", data=valid_input, headers={"Content-Type": "application/json"})
    print("/process with valid input Response:", response.json())

    # Test invalid input for /process endpoint (schema validation)
    invalid_input = json.dumps({"invalid key": "some value"})
    response = requests.post(f"{BASE_URL}/process", data=invalid_input, headers={"Content-Type": "application/json"})
    print("/process with invalid schema Response:", response.json())

    # Test invalid image path for /process endpoint
    invalid_path_input = json.dumps({"image path": INVALID_IMAGE_PATH})
    response = requests.post(f"{BASE_URL}/process", data=invalid_path_input, headers={"Content-Type": "application/json"})
    print("/process with invalid image path Response:", response.json())

    print("All tests completed.")

if __name__ == "__main__":
    test_api()
