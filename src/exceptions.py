"""Base project exceptions"""


class EqCompareError(BaseException):
    """Raises on attempt to compare object with
    another object, which don't have required attrs."""

    def __init__(self, obj_1: object, obj_2: object) -> None:
        self.cls1_name = obj_1.__class__.__name__
        self.cls2_name = obj_2.__class__.__name__

    def __str__(self) -> str:
        return f'{self.cls2_name} hasn\'t required fields'\
               f' to be compared with {self.cls1_name}'
