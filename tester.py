import requests

# Server URL
url = 'http://localhost:5000/answer'

# Path to the test WAV audio file
audio_file_path = 'audio01.wav'

# Make sure you replace 'path_to_test_audio.wav' with the actual path to your test WAV audio file.

try:
    # Read the audio file
    with open(audio_file_path, 'rb') as audio_file:
        files = {'file': audio_file}
        
        # Send the POST request to the server
        response = requests.post(url, files=files)
        
        # Print the response status code
        print(f"Status Code: {response.status_code}")
        
        # Print the response text to debug
        print(f"Response Text: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except ValueError as e:
    print(f"JSON decoding failed: {e}")
