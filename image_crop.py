import cv2
import pytesseract
import re


def compare_images(im1, im2):
    # SIFT is no longer available in cv2 so using ORB
    orb = cv2.ORB_create()

    # detect keypoints and descriptors
    kp_a, desc_a = orb.detectAndCompute(im1, None)
    kp_b, desc_b = orb.detectAndCompute(im2, None)

    # define the bruteforce matcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # perform matches.
    matches = bf.match(desc_a, desc_b)
    # Look for similar regions with distance < 50. Goes from 0 to 100 so pick a number between.
    similar_regions = [i for i in matches if i.distance < 50]
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)

class TemplateData:
    def __init__(self, name, logo_coordinates, price_coordinates):
        self.name = name
        self.logo_coordinates = logo_coordinates
        self.price_coordinates = price_coordinates

images = [
    TemplateData("template1.png", [60, 150, 60, 400], [460, 500, 250, 600]),
    TemplateData("template2.png", [30, 400, 100, 400], [1030, 1100, 900, 1200]),
    TemplateData("template3.png", [30, 150, 500, 700], [700, 800, 500, 700]),
]

print("input factuur:")
factuur_image = cv2.imread(input())

closest_img = 0
current_similarity = 0

for i in range(len(images)):
    img = images[i]
    logo_pos = img.logo_coordinates
    cropped_image = factuur_image[logo_pos[0]:logo_pos[1], logo_pos[2]:logo_pos[3]]
    template_image = cv2.imread("templates/" + img.name)
    similarity = compare_images(cropped_image, template_image)
    if similarity > current_similarity:
        current_similarity = similarity
        closest_img = i

price_pos = images[closest_img].price_coordinates
price = pytesseract.image_to_string(factuur_image[price_pos[0]:price_pos[1], price_pos[2]:price_pos[3]])
price = re.sub(r'[^0-9,]', '', price)
print(price)
