# schema_cowriting.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# Re-using ReactUIAction from your main models.py if it's general enough,
# or define a specific one here if co-writing actions are very unique.
# For now, let's assume we can hint at the general ReactUIAction structure.
# from models import ReactUIAction # Assuming ReactUIAction is defined elsewhere

class ReactUIActionHint(BaseModel):
    action_type_suggestion: str # e.g., "HIGHLIGHT_TEXT_RANGE", "SHOW_INLINE_SUGGESTION", "DISPLAY_TOOLTIP"
    target_student_text_segment: Optional[str] = Field(None, description="The specific part of student's text this action applies to.")
    parameter_suggestions: Dict[str, Any] = Field(description="Suggestions for the 'parameters' field of ReactUIAction")

class CoWritingIntervention(BaseModel):
    immediate_assessment_of_input: str = Field(description="AI's quick diagnosis of the student's current written chunk and/or articulated thought.")
    decision_to_intervene: bool = Field(description="True if AI decides to intervene now, False if it decides to wait.")
    intervention_reasoning_if_waiting: Optional[str] = Field(None, description="If decided to wait, the persona's reasoning.")
    
    intervention_type: Optional[str] = Field(None, description="If intervening: e.g., 'SuggestRephrasing', 'CorrectGrammar', 'OfferVocab', 'AskSocraticQuestion', 'ProvideHint'.")
    ai_spoken_or_suggested_text: Optional[str] = Field(None, description="What the AI co-pilot would say or the exact text of its suggestion.")
    original_student_text_if_revision: Optional[str] = Field(None, description="The original student text segment being addressed.")
    suggested_ai_revision_if_any: Optional[str] = Field(None, description="AI's suggested revision for the student's text.")
    
    associated_ui_action_hints: Optional[List[ReactUIActionHint]] = Field(default_factory=list)
    
    rationale_for_intervention_style: str = Field(description="Why this specific intervention and phrasing was chosen, linking to persona and student state.")
    anticipated_next_student_action_or_reply: str = Field(description="What the AI expects the student to do/say next.")

class CoWritingStrategy(BaseModel):
    # Input context for which this strategy applies
    persona_name: str
    learning_objective_focus: Optional[str]
    writing_task_context_section: str
    student_written_input_chunk: str
    student_articulated_thought: Optional[str]
    student_comfort_level: str
    student_affective_state: str
    
    # The generated strategy
    intervention_plan: CoWritingIntervention

    class Config:
        title = "AI Co-Writing Intervention Strategy"