import cv2
import numpy as np

def create_chessboard_image(filename, board_size, square_size):
    """
    Create a chessboard image and save it to a file.

    :param filename: The path to save the chessboard image.
    :param board_size: Tuple (width, height) specifying the number of squares in the chessboard.
    :param square_size: Size of each square in pixels.
    """
    # Calculate the size of the chessboard image
    width = board_size[0] * square_size
    height = board_size[1] * square_size

    # Create a black image
    chessboard = np.zeros((height, width), dtype=np.uint8)

    # Draw the white squares
    for y in range(board_size[1]):
        for x in range(board_size[0]):
            if (x + y) % 2 == 0:
                top_left = (x * square_size, y * square_size)
                bottom_right = ((x + 1) * square_size, (y + 1) * square_size)
                cv2.rectangle(chessboard, top_left, bottom_right, (255, 255, 255), -1)

    # Save the image
    cv2.imwrite(filename, chessboard)

    # Optionally, display the chessboard image
    cv2.imshow('Chessboard', chessboard)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__checkerboardGenerator__":
    # Define the chessboard parameters
    board_size = (9, 6)  # Number of squares in each row and column
    square_size = 50  # Size of each square in pixels
    # Create and save the chessboard image
    create_chessboard_image('chessboard_image.jpg', board_size, square_size)