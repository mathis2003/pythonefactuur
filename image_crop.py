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
    def __init__(self, name, logo_coordinates, price_coordinates, vat_coordinates, excl_vat_coordinates):
        self.name = name
        self.logo_coordinates = logo_coordinates
        self.price_coordinates = price_coordinates
        self.vat_coordinates = vat_coordinates
        self.excl_vat_coordinates = excl_vat_coordinates

images = [
    TemplateData("template1.png", [60, 150, 60, 400], [460, 500, 250, 600], [450, 470, 400, 550], [430, 450, 400, 550]),
    TemplateData("template2.png", [30, 400, 100, 400], [1030, 1100, 900, 1200], [1000, 1050, 1030, 1250], [970, 1000, 1030, 1250]),
    TemplateData("template3.png", [30, 150, 500, 700], [700, 800, 500, 700], [670, 720, 600, 700], [640, 690, 600, 700]),
]

print("input factuur:")
factuur_image = cv2.imread(input())
#factuur_image = cv2.imread("factuur1.png")

#logo_pos = [430, 450, 400, 550]
#cv2.imshow("vat", factuur_image[logo_pos[0]:logo_pos[1], logo_pos[2]:logo_pos[3]])
#cv2.waitKey(0)
#cv2.destroyAllWindows()

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
price = re.sub(",",".", price)
print("amount incl vat = "+price)

vat_pos = images[closest_img].vat_coordinates
vat = pytesseract.image_to_string(factuur_image[vat_pos[0]:vat_pos[1], vat_pos[2]:vat_pos[3]])
vat = re.sub(r'[^0-9,]', '', vat)
vat = re.sub(",",".", vat)
print("vat = "+vat)

excl_vat_pos = images[closest_img].excl_vat_coordinates
excl_vat = pytesseract.image_to_string(factuur_image[excl_vat_pos[0]:excl_vat_pos[1], excl_vat_pos[2]:excl_vat_pos[3]])
excl_vat = re.sub(r'[^0-9,]', '', excl_vat)
excl_vat = re.sub(",",".", excl_vat)
print("amount excl vat = "+excl_vat)

if float(price) - float(vat) == float(excl_vat):
    print ("reconciliation = OK")
elif float(price) - float(vat) != float(excl_vat):
    print ("reconciliation not OK")
