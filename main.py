from checkboardGenerator import create_chessboard_image  # Import the CameraStream class from camera.py


def main():
    # Define the chessboard parameters
    board_size = (9, 6)  # Number of squares in each row and column
    square_size = 50  # Size of each square in pixels
    # Create and save the chessboard image
    create_chessboard_image('chessboard_image.jpg', board_size, square_size)

if __name__ == "__main__":
    main()
