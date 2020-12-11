import cv2
import pytesseract
import numpy as np

custom_config = '-l eng -c tessedit_char_whitelist=" "aAeEiIoOuUhHkKlLmMnNpPwW0123456789., --oem 3 --psm 6'
def image_to_string(array):
    array = np.asarray(bytearray(array), dtype="uint8")
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # scan the image
    clean_image = cv2.fastNlMeansDenoising(gray_image) # remove noise on the image
    transcribed_text = pytesseract.image_to_string(image, config=custom_config) # OCR
    return transcribed_text
