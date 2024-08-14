# Generated by ariadne-codegen on 2024-08-13 19:15
# Source: queries.graphql

from typing import List
from typing import Optional
from uuid import UUID

from .base_model import BaseModel


class FacetsQuery(BaseModel):
    facets: "FacetsQueryFacets"


class FacetsQueryFacets(BaseModel):
    objects: List["FacetsQueryFacetsObjects"]


class FacetsQueryFacetsObjects(BaseModel):
    current: Optional["FacetsQueryFacetsObjectsCurrent"]


class FacetsQueryFacetsObjectsCurrent(BaseModel):
    uuid: UUID
    user_key: str


FacetsQuery.update_forward_refs()
FacetsQueryFacets.update_forward_refs()
FacetsQueryFacetsObjects.update_forward_refs()
FacetsQueryFacetsObjectsCurrent.update_forward_refs()
