from pydantic import BaseModel, Field
class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class TagResponse(BaseModel):
    id: int
    name: str
    post_count: int = 0

class TagListResponse(BaseModel):
    total: int
    items: list[TagResponse]