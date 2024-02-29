import random
from gender_age_estimation.gender_age_estimation import predict_gender_age


def set_seed():
    seed = random.randint(42,4294967295)
    return seed


def age_and_gender(image):
    detected_gender, detected_age = predict_gender_age(image)
    return detected_gender[0], detected_age[0]
