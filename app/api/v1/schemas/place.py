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

class FilterFields(BaseModel):
    city: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.dict().items() if v is not None}

class QueryRequestWithFilters(QueryRequest):
    metadata_filter: Optional[FilterFields] = None
    distance_threshold: Optional[float] = 1.2

    def get_metadata_filter_dict(self) -> Optional[Dict[str, Any]]:
        if self.metadata_filter:
            return self.metadata_filter.to_dict()
        return None

class QueryResponseItem(BaseModel):
    data: Dict[str, Any]
    class Config:
        extra = 'allow'

class QueryResponse(BaseModel):
    results: List[QueryResponseItem]
