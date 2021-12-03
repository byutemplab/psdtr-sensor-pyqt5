import cv2

# Show the edges of the image


def ShowEdges(img):
    """
    Show the edges of the image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Blur the image
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Find edges
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    # Show the image
    cv2.imshow('img', edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Find boundaries on an image using opencv


def FindBoundaries(img):
    """
    Find the boundaries of the grains in an image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Blur the image
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    # Find edges
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    # Find contours
    contours, hierarchy = cv2.findContours(
        edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # Find the bounding box of the contours
    boundingBoxes = []
    for contour in contours:
        boundingBoxes.append(cv2.boundingRect(contour))
    return boundingBoxes

# Show the boundaries on an image using opencv


def ShowBoundaries(img, boundingBoxes):
    """
    Show the boundaries of the grains in an image
    """
    # Copy the image
    imgCopy = img.copy()
    # Draw the bounding boxes
    for boundingBox in boundingBoxes:
        cv2.rectangle(imgCopy, (boundingBox[0], boundingBox[1]), (
            boundingBox[0] + boundingBox[2], boundingBox[1] + boundingBox[3]), (0, 255, 0), 2)
    # Show the image
    cv2.imshow('img', imgCopy)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Import the image


def ImportImage(path):
    """
    Import an image
    """
    return cv2.imread(path)


img = ImportImage("samples/aluminum-raw.jpg")
ShowEdges(img)
