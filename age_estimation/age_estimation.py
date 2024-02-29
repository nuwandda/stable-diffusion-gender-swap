from facelib import FaceDetector, AgeGenderEstimator
import cv2


face_detector = FaceDetector()
age_gender_detector = AgeGenderEstimator()


def predict_age(image):
    faces, _, _, _ = face_detector.detect_align(image)
    _, ages = age_gender_detector.detect(faces)
    
    return ages


def main():
    image = cv2.imread('/Users/bdonmez/Documents/Personal/Projeler/Wowoo/test_images/i17.jpg')
    ages = predict_age(image)
    print(ages)


if __name__ == '__main__':
    main()