from collections.abc import Sequence
from typing import Annotated, Generic, Literal, TypeVar

from fastapi import Depends, Query
from pydantic import BaseModel
from sqlalchemy import Select

T = TypeVar("T")


class PagingResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: Sequence[T]


class Paging(BaseModel, Generic[T]):
    page: int
    page_size: int
    sort: Literal["asc", "desc"]

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    @property
    def sort_order(self) -> int:
        return 1 if self.sort == "asc" else -1

    def apply(self, stmt: Select, sort_field) -> Select:
        return (
            stmt.order_by(
                sort_field.asc() if self.sort_order == 1 else sort_field.desc()
            )
            .offset(self.skip)
            .limit(self.limit)
        )


def get_paging(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort: Literal["asc", "desc"] = Query("desc"),
) -> Paging:
    return Paging(page=page, page_size=page_size, sort=sort)


PagingDep = Annotated[Paging, Depends(get_paging)]
