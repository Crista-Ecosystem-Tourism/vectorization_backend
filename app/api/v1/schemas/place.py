from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Extra

class Place(BaseModel):
    id: str
    name: str
    subcategories: Optional[List[str]]
    description: Optional[str]
    address: Optional[str]
    rating: Optional[float]
    numberOfReviews: Optional[int]

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QueryResponseItem(BaseModel):
    data: Dict[str, Any]
    class Config:
        extra = Extra.allow

class QueryResponse(BaseModel):
    results: List[QueryResponseItem]
