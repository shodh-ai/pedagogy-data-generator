# schema_scaffolding.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ScaffoldContentDetail(BaseModel):
    type: str = Field(description="Type of content, e.g., 'template', 'sentence_starters', 'guiding_questions', 'hint', 'simplified_steps_list'")
    name: Optional[str] = Field(None, description="A descriptive name for the scaffold, e.g., 'P-E-E Paragraph Template'")
    # Using Dict[str, Any] for content allows flexibility for different scaffold types.
    # For 'template', content could be {"fields": [{"label": "Topic:", "placeholder": "..."}]}
    # For 'sentence_starters', content could be {"starters": ["Firstly...", "Another reason is..."]}
    # For 'guiding_questions', content could be {"questions": ["What is your main point here?", "How does this example support it?"]}
    content: Dict[str, Any] = Field(description="The actual scaffold content in a structured format (JSON-like).")

class ScaffoldingStrategy(BaseModel):
    reasoning_for_scaffold_choice: str = Field(description="Teacher's rationale for selecting this specific scaffold type given the student's situation.")
    scaffold_type_selected: str = Field(description="A descriptive name of the scaffold type (e.g., 'Detailed Paragraph Template', 'Targeted Guiding Questions', 'Step-by-Step Breakdown').")
    scaffold_content_delivered: ScaffoldContentDetail = Field(description="The actual scaffold content and its structure.")
    scaffold_delivery_script: str = Field(description="What the AI teacher persona would say when introducing/presenting this scaffold.")
    guidance_on_use_script: str = Field(description="Brief instructions or tips on how the student should use this scaffold.")
    monitoring_and_immediate_followup: str = Field(description="How the teacher monitors use and what's the immediate next step if student struggles with the scaffold or uses it well.")
    fading_strategy_next_step: str = Field(description="How this specific scaffold would be reduced or faded in a future, similar task to promote independence.")
    affective_state_adaptation_notes: str = Field(description="How the persona's delivery or support is modified due to the student's current affective state (e.g., frustration, nervousness).")

    class Config:
        title = "Scaffolding Strategy for AI Tutor"