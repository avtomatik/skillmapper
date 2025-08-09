from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ItemsResponse(BaseModel, Generic[T]):
    items: list[T]
