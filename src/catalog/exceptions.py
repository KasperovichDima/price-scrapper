"""Catalog exceptions."""
from fastapi import HTTPException, status


wrong_model_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Not a valid model.",
)
