from typing import List
from pydantic import BaseModel
from pydantic import Field


class Module(BaseModel):
    type: str = Field(
        description="The type of module out of Teaching, Modelling, Scaffolding, Cowriting and Test"
    )
    task: str = Field(description="The task of the module; speaking or writing")
    topic: str = Field(description="The topic of the module")
    level: str = Field(description="The level of the module")


class Pedagogy(BaseModel):
    reasoning: str = Field(
        description="The reasoning behind choosing that pedagogical steps for learning"
    )
    steps: List[Module] = Field(description="The steps of the pedagogy")
