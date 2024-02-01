import cv2
import face_recognition
import json

# This file can be used for detecting individual people.
# I am using it for tasks, but can also be used for other
# things like a clock-in-out system.

json_data_path = "./public/data/data.json"

# Open and read json file containing data for each person
with open(json_data_path, "r") as file:
    data = json.load(file)

# Load pre-set names for each person
known_names = list(data["people"].keys())

# Load pre-set face encodings for each person
known_face_encodings = []
for name in known_names:
    known_image = face_recognition.load_image_file(f"./public/data/images/{name}.jpg")  # Use individual images for each person
    known_face_encoding = face_recognition.face_encodings(known_image)[0]
    known_face_encodings.append(known_face_encoding)

def compare_faces(frame):
    # Find all face locations in the frame
    face_locations = face_recognition.face_locations(frame)

    # Convert the frame from BGR to RGB (OpenCV uses BGR by default)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Find face encodings for all faces in the frame
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    name = "Unknown"  # Default name if no match is found

    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the face with pre-set face encodings
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)

        # If a match is found, use the corresponding pre-set name
        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

        # Uncomment to show a rectangle and label on the frame when displaying
        # cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # font = cv2.FONT_HERSHEY_DUPLEX
        # cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    return (frame, name)

def main():
    # Open the default camera (camera index 0)
    cap = cv2.VideoCapture(0)
    name = "Unknown"

    while name == "Unknown":
        # Read a frame from the camera
        ret, frame = cap.read()

        # Perform face recognition and update the frame
        recognition_data = compare_faces(frame)
        updated_frame = recognition_data[0]
        name = recognition_data[1]

        # Uncomment to display the updated frame
        # cv2.imshow("Face Recognition", updated_frame)

        # Check for key press and break the loop if 'q' is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # Release the camera and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()
    print(name, flush=True)

main()