from pydantic import BaseModel, Field
from typing import List, Optional


class CorrectionExample(BaseModel):
    """Represents a single language correction example."""
    topic: str = Field(description="The topic the student was asked to write/speak about")
    proficiency_level: str = Field(description="The simulated proficiency level of the student")
    mistake_type: List[str] = Field(description="Types of mistakes made (grammar, vocabulary, structure, etc.)")
    incorrect_version: str = Field(description="The version with mistakes")
    thought_process: str = Field(description="The reasoning and identification of errors")
    correct_version: str = Field(description="The corrected version")
    task_type: str = Field(description="Whether this is a speaking or writing task")


class CorrectionDataset(BaseModel):
    """Represents a collection of language correction examples."""
    examples: List[CorrectionExample] = Field(description="List of correction examples")
    metadata: dict = Field(description="Additional information about the dataset")
