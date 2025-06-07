# main_cowriting.py
import getpass
import os
import itertools
from tqdm.asyncio import tqdm as asyncio_tqdm
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError
import asyncio
import csv
import json
from typing import Optional

from data_cowriting import ( # Assuming you've populated this with relevant dimensions
    TEACHER_PERSONAS_COWRITING, # Reuse or make specific
    ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL,
    STUDENT_AFFECTIVE_STATE_PROXY, # Could be adapted to "Current_Student_Affective_State"
    # New dimensions for co-writing:
    WRITING_TASK_CONTEXTS, # List of dicts: {"task_type": "Independent", "section": "Body Paragraph 1 - Topic Sentence"}
    STUDENT_WRITTEN_INPUT_CHUNKS, # List of example student text snippets
    STUDENT_ARTICULATED_THOUGHTS, # List of example student articulations (can include "None")
    COWRITING_LO_FOCUS_EXAMPLES, # List of optional LO focuses for the AI
)
from schema_cowriting import CoWritingStrategy, CoWritingIntervention, ReactUIActionHint # New Pydantic schema

load_dotenv()

CHECKPOINT_FILE_COWRITING = "checkpoint_cowriting.txt"
# ... (save_checkpoint, load_checkpoint functions - same as before, just use CHECKPOINT_FILE_COWRITING) ...
def save_checkpoint(completed_count: int, filename: str = CHECKPOINT_FILE_COWRITING):
    try:
        with open(filename, "w") as f: f.write(str(completed_count))
    except IOError as e: print(f"Warning: Could not write to checkpoint file '{filename}': {e}")

def load_checkpoint(filename: str = CHECKPOINT_FILE_COWRITING) -> int:
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                content = f.read().strip()
                if content: return int(content)
                else: print(f"Warning: Checkpoint file '{filename}' is empty."); return 0
        except ValueError: print(f"Warning: Checkpoint file '{filename}' invalid."); return 0
        except IOError as e: print(f"Warning: Could not read '{filename}': {e}."); return 0
    return 0


if "GOOGLE_API_KEY" not in os.environ: os.environ["GOOGLE_API_KEY"] = getpass.getpass("Google AI API key: ")
if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" in os.environ: os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.4, # Allow for more creative/varied co-writing interventions
    convert_system_message_to_human=True
)

async def validate_cowriting_json(content: str) -> CoWritingStrategy | None:
    try:
        if content.strip().startswith("```json"): content = content.strip()[7:-3].strip()
        elif content.strip().startswith("```"): content = content.strip()[3:-3].strip()
        return CoWritingStrategy.model_validate_json(content)
    except ValidationError as e_val:
        print(f"Pydantic validation failed for CoWritingStrategy: {e_val}")
        print(f"Problematic JSON content snippet: {content[:1000]}...")
        return None
    except json.JSONDecodeError as e_json:
        print(f"JSON Decode Error for CoWritingStrategy: {e_json}. Snippet: {content[:1000]}...")
        return None
    except Exception as e:
        print(f"Unexpected error during CoWritingStrategy validation: {e}. Snippet: {content[:1000]}...")
        return None

async def generate_cowriting_intervention_for_scenario(
    persona_dict: dict,
    writing_task_ctx: dict,
    lo_focus: Optional[str],
    student_written_chunk: str,
    student_articulation: Optional[str],
    comfort_level: str,
    affective_state: Optional[str] = "not specified", # Using "Initial Impression" as a proxy for affective state
) -> CoWritingStrategy | None:
    
    persona_name = persona_dict["name"]
    persona_description = persona_dict["description"]
    task_type_desc = writing_task_ctx["task_type"]
    essay_section_desc = writing_task_ctx["section"]

    prompt_template_str = """
    You are an expert TOEFL Writing Co-Pilot acting as the persona: {persona_name}.
    Your teaching philosophy is: {persona_description}

    A student with an English comfort level of '{comfort_level}' is currently perceived by you to be in an affective state of '{affective_state}'.
    They are working on the '{essay_section_desc}' section of a '{task_type_desc}' TOEFL writing task.
    Your current pedagogical focus (if any) for this interaction is: '{lo_focus_str}'.

    The student has just typed the following text chunk:
    --- STUDENT WRITTEN CHUNK ---
    {student_written_chunk}
    --- END STUDENT WRITTEN CHUNK ---

    The student also articulated their thought process by saying:
    --- STUDENT ARTICULATED THOUGHT ---
    {student_articulation_str}
    --- END STUDENT ARTICULATED THOUGHT ---

    Given this exact situation, provide your real-time co-writing assistance. 
    Detail your intervention plan as a single JSON object adhering to the `CoWritingStrategy` Pydantic schema.
    The `CoWritingStrategy` schema has a top-level `intervention_plan` field of type `CoWritingIntervention`.
    The `CoWritingIntervention` schema includes:
    - `immediate_assessment_of_input`: (string) Your quick diagnosis.
    - `decision_to_intervene`: (boolean) True to intervene now, False to wait.
    - `intervention_reasoning_if_waiting`: (string, optional) If waiting, why.
    - `intervention_type`: (string, optional) If intervening, e.g., 'SuggestRephrasing', 'CorrectGrammar', 'OfferVocab', 'AskSocraticQuestionAboutWriting', 'ProvideStructuralHint'.
    - `ai_spoken_or_suggested_text`: (string, optional) What you (AI) would say or the text of your suggestion/question.
    - `original_student_text_if_revision`: (string, optional) The specific student text segment being addressed if suggesting a revision.
    - `suggested_ai_revision_if_any`: (string, optional) Your suggested revised text for the student.
    - `associated_ui_action_hints`: (List[ReactUIActionHint], optional) Hints for UI actions. Each hint has `action_type_suggestion` (e.g., "SHOW_INLINE_SUGGESTION"), `target_student_text_segment` (optional), and `parameter_suggestions` (a dict, e.g., {{"suggestion_text": "new phrase", "reason": "clarity"}}).
    - `rationale_for_intervention_style`: (string) Why this intervention/phrasing, linking to persona and student state.
    - `anticipated_next_student_action_or_reply`: (string) What you expect next.
    
    The top-level `CoWritingStrategy` JSON should also include these input context fields for reference: `persona_name`, `learning_objective_focus`, `writing_task_context_section`, `student_written_input_chunk`, `student_articulated_thought`, `student_comfort_level`, `student_affective_state`.

    Example for `associated_ui_action_hints` within `intervention_plan`:
    `[{{"action_type_suggestion": "HIGHLIGHT_TEXT_RANGE", "target_student_text_segment": "their mistake", "parameter_suggestions": {{"style_class": "grammar_error"}}}}, {{"action_type_suggestion": "SHOW_TOOLTIP", "target_student_text_segment": "their mistake", "parameter_suggestions": {{"tooltip_text": "Consider subject-verb agreement here."}}}}]`

    Focus on providing a *single, immediate, actionable* intervention based on the student's last chunk of writing and articulated thought. Your response should be ONLY the valid JSON object.
    """
    
    prompt = PromptTemplate.from_template(prompt_template_str)
    
    full_prompt_formatted = prompt.format(
        persona_name=persona_name,
        persona_description=persona_description,
        comfort_level=comfort_level,
        affective_state=affective_state, # This comes from INITIAL_IMPRESSION_FOR_STUDENT
        essay_section_desc=essay_section_desc,
        task_type_desc=task_type_desc,
        lo_focus_str=lo_focus if lo_focus else "General writing assistance",
        student_written_chunk=student_written_chunk,
        student_articulation_str=student_articulation if student_articulation else "No articulated thought provided.",
    )

    # print(f"---- PROMPT for Co-Writing: {persona_name} / Chunk: {student_written_chunk[:50]}... ----")
    # print(full_prompt_formatted) # For debugging
    # print("---- END PROMPT ----")

    try:
        response = await llm.ainvoke(full_prompt_formatted)
        content = response.content
        
        if isinstance(content, str):
            # print(f"---- RAW LLM RESPONSE for Co-Writing: {persona_name} / Chunk: {student_written_chunk[:50]}... ----")
            # print(content) # For debugging
            # print("---- END RAW LLM RESPONSE ----")
            # The LLM is asked to return the CoWritingStrategy JSON directly
            validated_data = await validate_cowriting_json(content)
            return validated_data
        else:
            print(f"Unexpected LLM response type for co-writing: {type(content)}")
            return None
    except Exception as e:
        print(f"Error during LLM call or processing for co-writing ({persona_name} / Chunk: {student_written_chunk[:50]}...): {e}")
        return None

async def main_cowriting_generator():
    csv_file_path = "cowriting_cta_data.csv"
    header_list = [
        # Input Context Fields from CoWritingStrategy
        "Persona",
        "Learning_Objective_Focus",
        "Writing_Task_Context_Section",
        "Student_Written_Input_Chunk",
        "Student_Articulated_Thought",
        "Student_Comfort_Level",
        "Student_Affective_State",
        # Fields from CoWritingIntervention (within intervention_plan)
        "Immediate_Assessment_of_Input",
        "Decision_to_Intervene",
        "Intervention_Reasoning_if_Waiting",
        "Intervention_Type",
        "AI_Spoken_or_Suggested_Text",
        "Original_Student_Text_if_Revision",
        "Suggested_AI_Revision_if_Any",
        "Associated_UI_Action_Hints_JSON", # Store as JSON string
        "Rationale_for_Intervention_Style",
        "Anticipated_Next_Student_Action_or_Reply",
    ]

    file_exists = os.path.exists(csv_file_path)
    is_empty = False
    if file_exists: is_empty = os.path.getsize(csv_file_path) == 0
    needs_header = not file_exists or is_empty

    # --- Create Iteration Space ---
    # This will be large, so be selective for initial runs
    scenarios_to_process = []
    for persona_dict in TEACHER_PERSONAS_COWRITING:
        for task_ctx in WRITING_TASK_CONTEXTS: # Predefined list of task sections
            for lo_focus in COWRITING_LO_FOCUS_EXAMPLES + [None]: # Include a case for general assistance
                for written_chunk in STUDENT_WRITTEN_INPUT_CHUNKS: # Example chunks
                    for articulation in STUDENT_ARTICULATED_THOUGHTS + [None]: # Include no articulation
                        for comfort in ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL:
                            scenarios_to_process.append({
                                    "persona_dict": persona_dict,
                                    "task_ctx": task_ctx,
                                    "lo_focus": lo_focus,
                                    "written_chunk": written_chunk,
                                    "articulation": articulation,
                                    "comfort": comfort,
                                })
    
    total_combinations = len(scenarios_to_process)
    print(f"Total co-writing scenarios to generate: {total_combinations}")

    completed_from_checkpoint = load_checkpoint()
    if completed_from_checkpoint >= total_combinations:
        print("All co-writing scenarios already processed according to checkpoint.")
        return

    scenarios_this_run = scenarios_to_process[completed_from_checkpoint:]
    print(f"Processing {len(scenarios_this_run)} remaining co-writing scenarios, starting from index {completed_from_checkpoint}.")

    with open(csv_file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(header_list)

        for i, scenario in enumerate(asyncio_tqdm(scenarios_this_run, total=len(scenarios_this_run), desc="Generating Co-Writing Strategies")):
            current_overall_index = completed_from_checkpoint + i
            
            print(f"\nProcessing co-writing scenario {current_overall_index + 1}/{total_combinations}: "
                  f"Persona: {scenario['persona_dict']['name']}, Chunk: {scenario['written_chunk'][:30]}...")
            
            # await asyncio.sleep(3) # Adjust based on QPM for Gemini Pro

            res_strategy: CoWritingStrategy | None = await generate_cowriting_intervention_for_scenario(
                persona_dict=scenario["persona_dict"],
                writing_task_ctx=scenario["task_ctx"],
                lo_focus=scenario["lo_focus"],
                student_written_chunk=scenario["written_chunk"],
                student_articulation=scenario["articulation"],
                comfort_level=scenario["comfort"],
            )

            if res_strategy and res_strategy.intervention_plan:
                ip = res_strategy.intervention_plan # shortcut for intervention_plan
                writer.writerow([
                    res_strategy.persona_name,
                    res_strategy.learning_objective_focus,
                    res_strategy.writing_task_context_section,
                    res_strategy.student_written_input_chunk,
                    res_strategy.student_articulated_thought,
                    res_strategy.student_comfort_level,
                    res_strategy.student_affective_state,
                    ip.immediate_assessment_of_input,
                    ip.decision_to_intervene,
                    ip.intervention_reasoning_if_waiting,
                    ip.intervention_type,
                    ip.ai_spoken_or_suggested_text,
                    ip.original_student_text_if_revision,
                    ip.suggested_ai_revision_if_any,
                    json.dumps([hint.model_dump() for hint in ip.associated_ui_action_hints]) if ip.associated_ui_action_hints else None,
                    ip.rationale_for_intervention_style,
                    ip.anticipated_next_student_action_or_reply,
                ])
                print(f"Successfully generated and wrote co-writing strategy for scenario {current_overall_index + 1}.")
            else:
                print(f"Failed to generate or validate co-writing strategy for scenario {current_overall_index + 1}. Skipping.")
                # Write a FAILED row
                writer.writerow([
                    scenario["persona_dict"]["name"], scenario["lo_focus"], scenario["task_ctx"]["section"],
                    scenario["written_chunk"], scenario["articulation"], scenario["comfort"], scenario["affect"],
                    "FAILED_TO_GENERATE", False, None, None, None, None, None, None, None, None
                ])
            
            save_checkpoint(current_overall_index + 1)



if __name__ == "__main__":
    # Define these lists in data_cowriting.py or directly here for testing
    # Ensure they are populated with diverse examples
    WRITING_TASK_CONTEXTS = [
        {"task_type": "Independent Essay", "section": "Introduction - Thesis Statement"},
        {"task_type": "Independent Essay", "section": "Body Paragraph 1 - Topic Sentence"},
        {"task_type": "Independent Essay", "section": "Body Paragraph 1 - Evidence"},
        {"task_type": "Integrated Essay", "section": "Summarizing Reading Point 1"},
        {"task_type": "Integrated Essay", "section": "Connecting Listening to Reading Point 1"},
    ]
    STUDENT_WRITTEN_INPUT_CHUNKS = [
        "I think recycling is good.",
        "The reading passage states that the new university policy will save money.",
        "For example many people they like to use cars.",
        "Furthermore, the lecturer she disagree with this idea.",
        "In conclusion it is clear that solution must be finded."
    ]
    STUDENT_ARTICULATED_THOUGHTS = [
        "I'm trying to make my main argument here for the thesis.",
        "Is this word 'utilize' too formal here?",
        "I'm not sure how to connect this idea to the previous paragraph.",
        "I need to give an example now to support my point about pollution.",
        None # Represents no articulated thought
    ]
    COWRITING_LO_FOCUS_EXAMPLES = [
        "Crafting a clear and arguable thesis statement.",
        "Using varied and precise academic vocabulary.",
        "Ensuring subject-verb agreement.",
        "Creating smooth transitions between sentences.",
        None # Represents general co-writing assistance without a narrow LO focus
    ]
    asyncio.run(main_cowriting_generator())