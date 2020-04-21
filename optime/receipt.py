"""
Calls Google-Vision API & Parses receipt images.
"""
from instance import config
from google.cloud import vision
import pyap

client = vision.ImageAnnotatorClient()

def parse_receipt(image_file_path):
    """
    image_file_path: (path)
    """
    # read in image
    with open(image_file_path, 'rb') as image_file:
        content = image_file.read()

    # create image object
    image = vision.types.Image(content=content)

    # obtain response
    response = client.text_detection(image=image)
    texts = response.text_annotations

    receipt_contents = []
    receipt_string = texts[0].description

    # create array of text
    for text in texts[1:]:
        receipt_contents.append(f'{text.description}')

    address = pyap.parse(receipt_string, country='US')
    # print(receipt_string)
    # print(receipt_contents)
    # print(address)

# Testing
# parse_receipt('/Users/shubhamkumar/Desktop/sample-receipt.jpg')
