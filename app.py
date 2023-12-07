from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest
import random
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from datetime import datetime
import json
from PIL import Image
import numpy as np
import imagehash
import cv2

# Initialize metrics
last_processed_time = None
last_message_time = None
total_processing_time = 0
total_processed_requests = 0
max_processing_time = 0
last_error_request = None
last_successful_request = None


# Define the schema for input validation
input_schema = {
    "image path": "string"
}

app = Flask(__name__)

# This function should handle initializations that should only happen upon starting the service
def do_init():
    # Initialization logic here
    pass

def compute_phash(image, hash_size=8):
    return str(imagehash.phash(image, hash_size))

def get_histogram_vector(image):
    img_array = np.array(image)
    if len(img_array.shape) == 2:  # Check if the image is grayscale
        hist = cv2.calcHist([img_array], [0], None, [256], [0, 256])
    else:
        hist = cv2.calcHist([img_array], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    # Normalize and flatten the histogram to create a 1D vector
    hist_norm = cv2.normalize(hist, hist).flatten()
    return hist_norm.tolist()

def do_process(data):
    try:
        # The data is already a dictionary, so directly get the file path
        file_path = data.get("image path")

        # Open the image
        with Image.open(file_path) as img:
            # Compute normalized histogram vector and pHash
            histogram_vector = get_histogram_vector(img)
            phash = compute_phash(img)

            # Construct JSON response
            response = {
                "histogram_vector": histogram_vector,
                "phash": phash
            }
            return json.dumps(response)
    except Exception as e:
        return json.dumps({"error": str(e)})

@app.route('/howto', methods=['GET'])
def how_to():
    # Documentation for using the /process endpoint
    usage_instructions = {
        "description": "To use the /process endpoint, send a JSON POST request with a first_name and last_name. Here's an example:",
        "curl_example": "curl -X POST -H 'Content-Type: application/json' -d '{\"image path\":\"/home/nehoray/Downloads/0\"}' http://localhost:8000/process",
        "expected_response": "{\"histogram_vector\":\"<histogram vector value>\", \"phash\": <phash value>}"
    }
    return jsonify(usage_instructions)

@app.route('/process', methods=['POST'])
def process_request():
    global last_processed_time, last_message_time, total_processing_time, total_processed_requests, max_processing_time, last_error_request, last_successful_request

    last_message_time = datetime.utcnow()

    try:
        input_data = request.get_json()

        if input_data is None:
            raise BadRequest("Input is not valid JSON.")

        validate(instance=input_data, schema=input_schema)

        start_time = datetime.utcnow()
        response_data = do_process(input_data)
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds

        # Update metrics for successful processing
        last_successful_request = input_data
        last_processed_time = start_time
        total_processing_time += processing_time
        total_processed_requests += 1
        max_processing_time = max(max_processing_time, processing_time)

        return jsonify(response_data), 200

    except ValidationError as e:
        # Return an error if the input JSON is invalid according to the schema
        last_error_request = request.data.decode() 
        return jsonify({"error": "Schema validation failed.", "message": str(e)}), 400
    except BadRequest as e:
        # Return an error if the input data is not valid JSON
        last_error_request = request.data.decode() 
        return jsonify({"error": "Invalid JSON format.", "message": str(e)}), 400
    except Exception as e:
        # Update metrics for errors
        last_error_request = request.data.decode()  # store raw request data
        return jsonify({"error": "An error occurred.", "message": str(e)}), 500

@app.route('/is_alive', methods=['GET'])
def is_alive():
    # Check resources and return status
    resource_ok = True  # Replace with actual resource check logic
    if not resource_ok:
        return jsonify({"alive": False}), 503

    # Calculate metrics
    current_time = datetime.utcnow()
    millis_since_last_processed = ((current_time - last_processed_time).total_seconds() * 1000 if last_processed_time else None)
    average_processing_time = (total_processing_time / total_processed_requests if total_processed_requests else None)

    status = {
        "alive": True,
        "last_processed_time": last_processed_time.isoformat() if last_processed_time else None,
        "last_message_time": last_message_time.isoformat() if last_message_time else None,
        "millis_since_last_processed": millis_since_last_processed,
        "average_processing_time": average_processing_time,
        "max_processing_time": max_processing_time,
        "last_error_request": last_error_request,
        "last_successful_request": last_successful_request
    }
    
    return jsonify(status)


if __name__ == '__main__':
    do_init()  # Initialize the service
    app.run(host='0.0.0.0', port=8000)  # Start the Flask application
