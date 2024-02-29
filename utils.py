import random
from gender_detection.gender_detection import predict_gender
import face_recognition
from age_estimation.age_estimation import predict_age


def set_seed():
    seed = random.randint(42,4294967295)
    return seed


def age_and_gender(image):
    boxes_face = face_recognition.face_locations(image)
    if len(boxes_face) == 1:
        x0,y1,x1,y0 = boxes_face[0]
        face_image = image[x0:x1,y0:y1]
        detected_gender = predict_gender(face_image)
        detected_age = predict_age(face_image)
        
        return detected_gender, detected_age[0]
    else:
        return 'Multiple faces', 'Multiple ages'
