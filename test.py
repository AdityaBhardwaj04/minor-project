from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle


def login(username):
    video = cv2.VideoCapture(0)
    faceDetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

    with open('data/names.pkl', 'rb') as f:
        LABELS = pickle.load(f)

    with open('data/faces_data.pkl', 'rb') as f:
        FACES = pickle.load(f)

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)

    output = []

    while True:
        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cropImage = frame[y:y + h, x:x + w, :]
            resizedImage = cv2.resize(cropImage, (50, 50)).flatten().reshape(1, -1)
            output = knn.predict(resizedImage)
            cv2.putText(frame, str(output[0]), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
        cv2.imshow("Sign Up", frame)
        k = cv2.waitKey(1)
        if k == ord('q') or output[0] == username:
            break

    video.release()
    cv2.destroyAllWindows()

    if username in output:
        return True
