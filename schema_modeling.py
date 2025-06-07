# schema_modeling.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union

class ModelSegment(BaseModel):
    type: str = Field(description="Either 'MODEL_TEXT' (what AI writes/says) or 'THINK_ALOUD_TEXT' (AI's explanation/metacognition)")
    content: str = Field(description="The actual text for the model or the think-aloud.")
    ui_action_hints: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Optional hints for UI actions e.g., {'action_type': 'HIGHLIGHT_MODEL_TEXT', 'parameters': {'start':0, 'end':10, 'style':'emphasis'}}")

class ModelingStrategy(BaseModel):
    learning_objective_modeled: str = Field(description="The specific LO being demonstrated.")
    persona_style_summary: str = Field(description="Brief summary of how the persona's style influenced this modeling approach.")
    
    pre_modeling_setup_script: Optional[str] = Field(None, description="What the AI persona says to introduce the modeling session and what it will demonstrate.")
    
    # This is the core: a sequence of the AI "doing" and "thinking aloud"
    modeling_and_think_aloud_sequence: List[ModelSegment] = Field(description="An ordered list of model text/speech segments interleaved with think-aloud explanations.")
    
    post_modeling_summary_and_key_takeaways: str = Field(description="What the AI persona says after the demonstration to summarize key learning points from the model.")
    
    # Example of how the persona might model self-correction
    self_correction_demonstration: Optional[List[ModelSegment]] = Field(default_factory=list, description="Optional sequence showing AI making a 'mistake' then self-correcting with think-aloud.")

    comprehension_check_or_reflection_prompt_for_student: str = Field(description="What question the AI asks the student after modeling to encourage reflection or Q&A.")
    
    adaptation_for_student_profile_notes: str = Field(description="How this modeling (e.g., complexity, pace, think-aloud detail) was adapted for the student's proficiency, initial impression, or affective state.")

    class Config:
        title = "AI Modeling Strategy for TOEFL Tutor"