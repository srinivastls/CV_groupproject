import cv2
import pytesseract


for i in range(10):
    
# Load the image containing the license plate
    image_path="images/Cars"+str(i)+".png"
    print(image_path)
    img = cv2.imread(image_path)
    
    # Convert the image to grayscale for character recognition
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use OpenCV's text detection to detect the license plate
    license_plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
    plates = license_plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in plates:
        # Draw a rectangle around the detected license plate
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Crop the license plate region
        plate = gray[y:y + h, x:x + w]

        # Use Tesseract for character recognition
        plate_text = pytesseract.image_to_string(plate)

        # Display the recognized license plate text
        print("License Plate Text:", plate_text)

    # Display the image with the detected license plate
    cv2.imshow("License Plate Detection", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
