from facelib import FaceDetector, AgeGenderEstimator


face_detector = FaceDetector()
age_gender_detector = AgeGenderEstimator()


def predict_gender_age(image):
    """
    Predicts the gender and age of a person in an image.

    Args:
        image (np.ndarray): The image containing the person.

    Returns:
        Tuple[str, str]: A tuple containing the predicted gender and age.

    Raises:
        ValueError: If the image does not have the correct dimensions.

    """
    # Check if the image has an alpha channel
    if image.shape[-1] == 4:  # Check if the last dimension is 4 (RGBA)
        # Drop the alpha channel
        image = image[:,:,:3]

    # converted_image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
    faces, _, _, _ = face_detector.detect_align(image)
    if len(faces) == 1:
        gender, ages = age_gender_detector.detect(faces)
        return gender, ages
    else:
        return 'Multiple faces', 'Multiple ages'
