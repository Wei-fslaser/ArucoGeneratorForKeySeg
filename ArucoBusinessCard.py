import matplotlib.pyplot as plt
import cv2
from cv2 import aruco
import numpy as np
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from io import BytesIO
import tempfile

# Create a blank white image of size 3.5"x2" (300 DPI)
width = 3.5 * 300
height = 2 * 300
image = np.ones((int(height), int(width), 3), dtype=np.uint8) * 255

# Define the size and ID of the ArUco tag
aruco_size = 0.5 * 300  # 1" converted to pixels (300 DPI)
aruco_id = 42

# Create an ArUco dictionary
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# Generate the ArUco marker image
marker_image = np.zeros((int(aruco_size), int(aruco_size)), dtype=np.uint8)
marker_image = aruco.generateImageMarker(aruco_dict, aruco_id, int(aruco_size), marker_image, 1)

# Place the marker image in the upper left corner of the main image
margin = 25
image[margin:margin+int(aruco_size), margin:margin+int(aruco_size)] = cv2.cvtColor(marker_image, cv2.COLOR_GRAY2RGB)

# Draw a cross and a circle for placing key head and key blade in the middle of the image

center_x = int(width / 2)
center_y = int(height / 2)
cross_size = int(0.25 / 2.54 * 300)  # 0.5 cm converted to pixels (300 DPI)
cross_thickness = 2
circle_diameter = cross_size
color = (0, 0, 0)  # Black color (BGR format)

# Calculate the x-coordinates for circle and cross
circle_x = center_x - 150
cross_x = center_x + 150

# Draw the cross
cv2.line(image, (cross_x - cross_size // 2, center_y), (cross_x + cross_size // 2, center_y),
         color, cross_thickness)
cv2.line(image, (cross_x, center_y - cross_size // 2), (cross_x, center_y + cross_size // 2),
         color, cross_thickness)

# Draw the circle
circle_radius = circle_diameter // 2
cv2.circle(image, (circle_x, center_y), circle_radius, color, cross_thickness)

# Add text labels on top and below the image
text1 = "Put the key head on the circle and the key blade on the cross"
text2 = "Please take the picture from upright position for better result"
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.8
text_thickness = 1
text1_size, _ = cv2.getTextSize(text1, font, font_scale, text_thickness)
text2_size, _ = cv2.getTextSize(text2, font, font_scale, text_thickness)
text1_x = int((width - text1_size[0]) / 2)
text1_y = height - margin - 30  # Place the first text just on the bottom
text2_x = int((width - text2_size[0]) / 2)
text2_y = height - margin  # Place the second text below the first line

cv2.putText(image, text1, (text1_x, text1_y), font, font_scale, color, text_thickness, cv2.LINE_AA)
cv2.putText(image, text2, (text2_x, text2_y), font, font_scale, color, text_thickness, cv2.LINE_AA)

# Load the PNG image
png_image = cv2.imread("FSLlogo.png", cv2.IMREAD_UNCHANGED)

# Resize the PNG image to fit the desired size
png_height, png_width = png_image.shape[:2]
desired_width = int(0.2 * width)  # Adjust the size as needed
scale_factor = desired_width / png_width
resized_png = cv2.resize(png_image, (desired_width, int(png_height * scale_factor)))

# Define the position for the top right corner
top_right_x = int(width - margin - desired_width)
top_right_y = margin

# Blend the PNG image onto the main image
image[top_right_y:top_right_y + resized_png.shape[0], top_right_x:top_right_x + resized_png.shape[1]] = resized_png


# Display the image using matplotlib
plt.imshow(image)
plt.axis('off')
plt.show()

# Save the image as a temporary file
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
    tempFilename = temp.name
    cv2.imwrite(tempFilename, image)

# Convert image to PDF using ReportLab
buffer = BytesIO()
card_width = width
card_height = height
c = canvas.Canvas(buffer, pagesize=landscape((card_width, card_height)))
c.drawImage(tempFilename, 0, 0, card_width, card_height)
c.showPage()
c.save()

# Save the PDF
outputFilename = "aruco_business_card.pdf"
with open(outputFilename, "wb") as pdfFile:
    pdfFile.write(buffer.getvalue())

print("Image saved as", outputFilename)

# Delete the temporary image file
temp.close()
