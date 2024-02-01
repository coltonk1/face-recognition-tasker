import subprocess
import time
import uuid as u
import cv2
import json
import face_recognition
import sys

json_file_path = "public/data/data.json"

# Takes a picture
def take_picture(user_uuid):
    # Open a connection to the default camera (usually the built-in webcam)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    time.sleep(5)

    # Read frames multiple times to allow the camera to adjust
    num_frames_to_read = 5  # Adjust the number of frames as needed
    for _ in range(num_frames_to_read):
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            cap.release()
            return

    # Release the camera
    cap.release()

    # Save the captured frame as an image file
    cv2.imwrite(f"public/data/images/{user_uuid}.jpg", frame)

    try:
        known_image = face_recognition.load_image_file(f"public/data/images/{user_uuid}.jpg")
        face_recognition.face_encodings(known_image)[0]
    except IndexError:
        print(f"No face encoding found for the image. Trying again.")
        take_picture(user_uuid)
        return

# Gets the json data
def get_json_data():
    try:
        with open(json_file_path, "r") as json_file:
            existing_data = json.load(json_file)
            return existing_data
    except FileNotFoundError:
        return None

# Updates whichever parameters are not None in the json file.
def update_json(user_uuid, name=None, tasks=None, status=None, active=None):
    json_data = get_json_data()

    if json_data is None:
        return
    
    user_uuid = str(user_uuid)

    # Retrieve the user or create a new entry with default values
    user_entry = json_data["people"].setdefault(user_uuid, {"name": "Unknown", "tasks": [], "status": 0, "active": 1})
    # Update user attributes if non-None values are provided
    user_entry['name'] = name if name is not None else user_entry['name']
    user_entry['tasks'] = tasks if tasks is not None else user_entry['tasks']
    user_entry['status'] = status if status is not None else user_entry['status']
    user_entry['active'] = active if active is not None else user_entry['active']

    with open(json_file_path, "w") as json_file:
        json.dump(json_data, json_file, indent=2)
    
    # print("Updated user")

# Adds a task
def add_task(user_uuid, task):
    json_data = get_json_data()
    tasks = json_data["people"][user_uuid]['tasks']
    tasks.append(task)
    update_json(user_uuid, None, tasks)

# Removes a task
def remove_task(user_uuid, index):
    json_data = get_json_data()
    tasks = json_data["people"][user_uuid]['tasks']
    if(len(tasks) >= index):
        return
    tasks.pop(index)
    update_json(user_uuid, None, tasks)

# Creates a new user
def create_new_user(user_uuid, name=None, tasks=None, status=None, active=None):
    take_picture(user_uuid)
    update_json(user_uuid, name, tasks, status, active)
    print(user_uuid)

# Uses the other script to detect a person. Returns the uuid.
def detect_face():
    script_path = './python/detect-face.py'

    # Use subprocess to call the second script
    process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Wait for a maximum of 30 seconds for the subprocess to finish
    timeout_seconds = 30
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        # Check if the process has terminated
        return_code = process.poll()
        
        if return_code is not None:
            # The process has terminated
            # print(f"Subprocess exited with return code: {return_code}")
            break

        # Sleep for a short duration before checking again
        time.sleep(1)

    # If the loop completes without breaking, the timeout has been reached
    if time.time() - start_time >= timeout_seconds:
        print("Timeout reached. Terminating the subprocess.")
        process.terminate()

    # Capture the output of the subprocess
    output, error = process.communicate()

    print("{\"output\":\"" + output[:-1])
    # print("Error: " + error)

    json_data = get_json_data()
    print( "\",\"name\":\"" + json_data["people"][output[:-1]]['name'] + "\"}")

    # Output should be the uuid unless there is none

    # Optionally, wait for the subprocess to finish (cleanly) and get the final return code
    final_return_code = process.wait()
    # print(f"Subprocess exited with return code: {final_return_code}")

    return output[:-1]

def switch_arguments():
    match sys.argv[1]:
        case '-new_user':
            create_new_user(u.uuid4(), sys.argv[2])
            return
        case '-get_uuid':
            detect_face()
            return
        case '-update_json':
            print(sys.argv[2])
        case '-add_task':
            uuid = sys.argv[2]
            new_task = sys.argv[3]
            add_task(uuid, new_task)
        case '-remove_task':
            uuid = sys.argv[2]
            index = sys.argv[3]
            remove_task(uuid, index)
def main():
    switch_arguments()

main()

# Functions:
# Creates a new user with an image and initializes in json.
#   create_new_user(u.uuid4(), "Colton Karaffa")
# Gets the uuid of the person in the camera.
#   uuid = detect_face()
# Updates the json, removes all tasks, adds one task.
#   update_json(uuid, None, ["Do some task"])
# Keeps all tasks and adds another.
#   add_task(uuid, "Bro..")
# Removes a task in the array, keeps all others.
#   remove_task(uuid, 1)