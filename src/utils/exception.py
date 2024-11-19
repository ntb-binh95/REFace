"""This file define custom exception for error in code"""

class NoFaceException(Exception):
    """Exception raised for errors with not face input.

    Attributes:
        image_name -- name of input image
    """

    def __init__(self, message="Input image should contain face"):
        self.message = message
        super().__init__(self.message)
