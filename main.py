# main_modeling.py
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

from data_modeling import (
    QUESTION_ONE_ANSWERS,
    QUESTION_TWO_ANSWERS,
    QUESTION_THREE_ANSWERS,
    ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL,
    INITIAL_IMPRESSION_FOR_STUDENT,
    TEACHER_PERSONAS_MODELING,
    LEARNING_OBJECTIVE_BEING_MODELED,
    EXAMPLE_TOEFL_PROMPTS_FOR_MODELING, # You'll need to select appropriate prompts per LO
    STUDENT_STRUGGLE_CONTEXT_FOR_MODELING
)
from schema_modeling import ModelingStrategy # New Pydantic schema

load_dotenv()

# --- Checkpoint handling (can reuse your existing functions or make specific ones) ---
CHECKPOINT_FILE_MODELING = "checkpoint_modeling.txt"

def save_checkpoint(completed_count: int, filename: str = CHECKPOINT_FILE_MODELING):
    try:
        with open(filename, "w") as f:
            f.write(str(completed_count))
    except IOError as e:
        print(f"Warning: Could not write to checkpoint file '{filename}': {e}")

def load_checkpoint(filename: str = CHECKPOINT_FILE_MODELING) -> int:
    # ... (same load_checkpoint logic as before) ...
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                content = f.read().strip()
                if content: return int(content)
                else: print(f"Warning: Checkpoint file '{filename}' is empty."); return 0
        except ValueError: print(f"Warning: Checkpoint file '{filename}' invalid."); return 0
        except IOError as e: print(f"Warning: Could not read '{filename}': {e}."); return 0
    return 0
# --- End Checkpoint handling ---

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest", # Using Pro for potentially more complex generation
    temperature=0.3, # Slightly creative but still grounded for persona
    convert_system_message_to_human=True
)

async def validate_modeling_json(content: str) -> ModelingStrategy | None:
    """Validates and potentially corrects JSON content against ModelingStrategy."""
    try:
        if content.strip().startswith("```json"):
            content = content.strip()[7:-3].strip()
        elif content.strip().startswith("```"):
             content = content.strip()[3:-3].strip()
        return ModelingStrategy.model_validate_json(content)
    except ValidationError as e_val:
        print(f"Pydantic validation failed for ModelingStrategy: {e_val}")
        print(f"Problematic JSON content snippet: {content[:1000]}...")
        return None
    except json.JSONDecodeError as e_json:
        print(f"JSON Decode Error for ModelingStrategy: {e_json}. Content snippet: {content[:1000]}...")
        return None
    except Exception as e:
        print(f"Unexpected error during ModelingStrategy validation: {e}. Content: {content[:1000]}...")
        return None

async def generate_modeling_strategy_for_scenario(
    persona_dict: dict,
    lo_being_modeled_dict: dict,
    example_prompt_text: str, # The specific TOEFL prompt AI will model for
    student_q1_ans: str,
    student_q2_ans: str,
    student_q3_ans: str,
    comfort_level: str,
    initial_impression: str,
    struggle_context: str,
) -> ModelingStrategy | None:
    
    persona_name = persona_dict["name"]
    persona_description = persona_dict["description"]
    lo_description = lo_being_modeled_dict["description"]
    task_type = lo_being_modeled_dict["task_type"] # Speaking or Writing

    prompt_template_str = """
    You are an expert TOEFL teacher acting as the persona: {persona_name}.
    Your teaching philosophy is: {persona_description}

    A student presents with the following profile:
    *   Student's Stated Goal (Q1): "{student_q1_ans}"
    *   Student's Self-Assessed Confidence/Challenge Area (Q2): "{student_q2_ans}"
    *   Student's Current Attitude towards TOEFL (Q3): "{student_q3_ans}"
    *   Estimated Overall English Comfort Level: "{comfort_level}"
    *   Your Initial Pedagogical Impression/Focus for this Student: "{initial_impression}"
    *   Student's current area of struggle relevant to this modeling: "{struggle_context}"

    Your task is to design and script an AI Modeling session. The AI (you, as the persona) will demonstrate how to approach a {task_type} task, specifically modeling the Learning Objective: "{lo_description}".
    The specific TOEFL-style prompt the AI should model a response for is: "{example_prompt_text}"

    Please provide the following detailed plan for the modeling session as a single JSON object adhering to the `ModelingStrategy` Pydantic schema. 
    The schema includes:
    - `learning_objective_modeled`: (string) - restate "{lo_description}"
    - `persona_style_summary`: (string) - briefly how your persona influences this modeling.
    - `pre_modeling_setup_script`: (string, optional) - What you say to introduce the modeling.
    - `modeling_and_think_aloud_sequence`: (List[ModelSegment]) - This is critical. Provide a sequence of segments. Each segment is an object with `type` ('MODEL_TEXT' for what the AI writes/says, or 'THINK_ALOUD_TEXT' for its explanation) and `content` (the text). Also, optionally include `ui_action_hints` (e.g., for highlighting parts of `MODEL_TEXT`). Ensure this sequence is logical and clearly demonstrates the LO. For writing, show the essay being built chunk by chunk with interleaved think-alouds. For speaking, provide the model speech with interleaved think-alouds.
    - `post_modeling_summary_and_key_takeaways`: (string) - What you say after the demonstration.
    - `self_correction_demonstration`: (List[ModelSegment], optional) - If relevant for this LO and persona, show the AI making a small "mistake" then self-correcting with think-aloud.
    - `comprehension_check_or_reflection_prompt_for_student`: (string) - The question you ask the student after modeling.
    - `adaptation_for_student_profile_notes`: (string) - How this specific modeling session is adapted for the student's profile (comfort level, attitude, initial impression, struggle).

    Think step-by-step for the `modeling_and_think_aloud_sequence`. For example, if modeling a thesis statement:
    1. THINK_ALOUD_TEXT: "First, I need to understand the prompt and decide my main argument..."
    2. MODEL_TEXT: "[Drafts a thesis statement]"
    3. THINK_ALOUD_TEXT: "This thesis is good because it's arguable and addresses the prompt directly. I've also included my main supporting points..."
    
    Ensure your entire response is ONLY the valid JSON object, without any surrounding text or markdown.
    The `modeling_and_think_aloud_sequence` should be detailed and provide a realistic flow of how the AI would model the skill.
    """
    
    prompt = PromptTemplate.from_template(prompt_template_str)
    
    full_prompt_formatted = prompt.format(
        persona_name=persona_name,
        persona_description=persona_description,
        student_q1_ans=student_q1_ans,
        student_q2_ans=student_q2_ans,
        student_q3_ans=student_q3_ans,
        comfort_level=comfort_level,
        initial_impression=initial_impression,
        lo_description=lo_description,
        task_type=task_type,
        example_prompt_text=example_prompt_text,
        struggle_context=struggle_context,
    )

    # print(f"---- PROMPT for Modeling: {persona_name} / {lo_description[:30]}... ----")
    # print(full_prompt_formatted) # For debugging
    # print("---- END PROMPT ----")

    try:
        response = await llm.ainvoke(full_prompt_formatted)
        content = response.content
        
        if isinstance(content, str):
            # print(f"---- RAW LLM RESPONSE for Modeling: {persona_name} / {lo_description[:30]}... ----")
            # print(content) # For debugging
            # print("---- END RAW LLM RESPONSE ----")
            validated_data = await validate_modeling_json(content)
            return validated_data
        else:
            print(f"Unexpected LLM response type for modeling: {type(content)}")
            return None
            
    except Exception as e:
        print(f"Error during LLM call or processing for modeling ({persona_name} / {lo_description[:30]}...): {e}")
        # Consider logging the full_prompt_formatted here for easier debugging of failed prompts
        return None


async def main_modeling_generator():
    csv_file_path = "modeling_cta_data.csv"
    header_list = [
        "Persona",
        "Learning_Objective_Modeled",
        "Task_Type", # Speaking or Writing
        "Example_Prompt_Text",
        "Student_Goal_Context",
        "Student_Confidence_Context",
        "Student_Attitude_Context",
        "English_Comfort_Level",
        "Teacher_Initial_Impression",
        "Student_Struggle_Context",
        # Columns from ModelingStrategy Pydantic model
        "persona_style_summary",
        "pre_modeling_setup_script",
        "modeling_and_think_aloud_sequence_json", # Store as JSON string
        "post_modeling_summary_and_key_takeaways",
        "self_correction_demonstration_json", # Store as JSON string
        "comprehension_check_or_reflection_prompt_for_student",
        "adaptation_for_student_profile_notes",
    ]

    file_exists = os.path.exists(csv_file_path)
    is_empty = False
    if file_exists:
        is_empty = os.path.getsize(csv_file_path) == 0
    needs_header = not file_exists or is_empty

    scenarios_to_process = []
    # Iteration logic: For each Persona, LO, Student Profile combination, and a relevant prompt.
    # You'll need to smartly pair LOs with EXAMPLE_TOEFL_PROMPTS_FOR_MODELING
    for persona_dict in TEACHER_PERSONAS_MODELING:
        for lo_dict in LEARNING_OBJECTIVE_BEING_MODELED:
            # Select a relevant example prompt for this LO and task type
            # This logic needs to be smarter, e.g., filter prompts by task_type
            # For now, just picking the first one that matches task_type for simplicity
            relevant_prompts = [p for p in EXAMPLE_TOEFL_PROMPTS_FOR_MODELING if p["type"].startswith(lo_dict["task_type"])]
            if not relevant_prompts:
                print(f"Warning: No example prompt found for LO '{lo_dict['description']}' and task type '{lo_dict['task_type']}'. Skipping.")
                continue
            example_prompt = relevant_prompts[0] # Simple selection for now

            for struggle_ctx in STUDENT_STRUGGLE_CONTEXT_FOR_MODELING: # Could also make this more targeted to LO
                for q1_ans in QUESTION_ONE_ANSWERS:
                    for q2_ans in QUESTION_TWO_ANSWERS:
                        for q3_ans in QUESTION_THREE_ANSWERS:
                            for comfort in ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL:
                                for impression in INITIAL_IMPRESSION_FOR_STUDENT:
                                    scenarios_to_process.append({
                                        "persona_dict": persona_dict,
                                        "lo_dict": lo_dict,
                                        "example_prompt_text": example_prompt["prompt_text"],
                                        "q1_ans": q1_ans,
                                        "q2_ans": q2_ans,
                                        "q3_ans": q3_ans,
                                        "comfort": comfort,
                                        "impression": impression,
                                        "struggle": struggle_ctx,
                                    })
    
    total_combinations = len(scenarios_to_process)
    print(f"Total modeling scenarios to generate: {total_combinations}")

    completed_from_checkpoint = load_checkpoint()
    if completed_from_checkpoint >= total_combinations:
        print("All modeling scenarios already processed according to checkpoint.")
        return

    scenarios_this_run = scenarios_to_process[completed_from_checkpoint:]
    print(f"Processing {len(scenarios_this_run)} remaining modeling scenarios, starting from index {completed_from_checkpoint}.")

    with open(csv_file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(header_list)

        for i, scenario in enumerate(asyncio_tqdm(scenarios_this_run, total=len(scenarios_this_run), desc="Generating Modeling Strategies")):
            current_overall_index = completed_from_checkpoint + i
            
            print(f"\nProcessing modeling scenario {current_overall_index + 1}/{total_combinations}: "
                  f"Persona: {scenario['persona_dict']['name']}, LO: {scenario['lo_dict']['description'][:30]}...")
            
            # await asyncio.sleep(2) # Adjust sleep based on your QPM for Gemini Pro

            res_strategy: ModelingStrategy | None = await generate_modeling_strategy_for_scenario(
                persona_dict=scenario["persona_dict"],
                lo_being_modeled_dict=scenario["lo_dict"],
                example_prompt_text=scenario["example_prompt_text"],
                student_q1_ans=scenario["q1_ans"],
                student_q2_ans=scenario["q2_ans"],
                student_q3_ans=scenario["q3_ans"],
                comfort_level=scenario["comfort"],
                initial_impression=scenario["impression"],
                struggle_context=scenario["struggle"],
            )

            if res_strategy:
                writer.writerow([
                    scenario["persona_dict"]["name"],
                    res_strategy.learning_objective_modeled, # From LLM output to ensure consistency
                    scenario["lo_dict"]["task_type"],
                    scenario["example_prompt_text"],
                    scenario["q1_ans"],
                    scenario["q2_ans"],
                    scenario["q3_ans"],
                    scenario["comfort"],
                    scenario["impression"],
                    scenario["struggle"],
                    res_strategy.persona_style_summary,
                    res_strategy.pre_modeling_setup_script,
                    json.dumps([segment.model_dump() for segment in res_strategy.modeling_and_think_aloud_sequence]),
                    res_strategy.post_modeling_summary_and_key_takeaways,
                    json.dumps([segment.model_dump() for segment in res_strategy.self_correction_demonstration]) if res_strategy.self_correction_demonstration else None,
                    res_strategy.comprehension_check_or_reflection_prompt_for_student,
                    res_strategy.adaptation_for_student_profile_notes,
                ])
                print(f"Successfully generated and wrote modeling strategy for scenario {current_overall_index + 1}.")
            else:
                print(f"Failed to generate or validate modeling strategy for scenario {current_overall_index + 1}. Skipping.")
                writer.writerow([
                    scenario["persona_dict"]["name"],
                    scenario["lo_dict"]["description"], # Fallback to input LO
                    scenario["lo_dict"]["task_type"],
                    scenario["example_prompt_text"],
                    scenario["q1_ans"],
                    scenario["q2_ans"],
                    scenario["q3_ans"],
                    scenario["comfort"],
                    scenario["impression"],
                    scenario["struggle"],
                    "FAILED_TO_GENERATE", "", "", "", "", "", "" # Placeholder for failed strategy fields
                ])

            save_checkpoint(current_overall_index + 1)
            if (i > 0 and (i + 1) % 5 == 0) or total_combinations < 10 : # More frequent for Gemini Pro QPM
                 print(f"Pausing for 10s to respect API rate limits after {i+1} calls...")
                 await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main_modeling_generator())