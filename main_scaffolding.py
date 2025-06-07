# main_scaffolding.py
import getpass
import os
import itertools
from tqdm.asyncio import tqdm as asyncio_tqdm
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate # Use from langchain_core
from langchain_google_genai import ChatGoogleGenerativeAI # Correct import
from pydantic import ValidationError
# from pydantic_ai_agent import Agent # Assuming this was for pydantic-ai, let's use direct Pydantic for now

# Import data from your new/augmented data file
from data_scaffolding import (
    QUESTION_ONE_ANSWERS,
    QUESTION_TWO_ANSWERS,
    QUESTION_THREE_ANSWERS,
    ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL,
    INITIAL_IMPRESSION,
    TEACHER_PERSONAS_SCAFFOLDING,
    LEARNING_OBJECTIVES_OR_TASKS_TO_SCAFFOLD,
    SPECIFIC_STRUGGLE_POINTS_EXAMPLES, # Use this for more targeted scenarios
)

# Import the new Pydantic schema
from schema_scaffolding import ScaffoldingStrategy
import asyncio
import csv
import json # For parsing potential JSON string from LLM

load_dotenv()

# --- Checkpoint handling (can reuse your existing functions) ---
CHECKPOINT_FILE_SCAFFOLDING = "checkpoint_scaffolding.txt"

def save_checkpoint(completed_count: int, filename: str = CHECKPOINT_FILE_SCAFFOLDING):
    try:
        with open(filename, "w") as f:
            f.write(str(completed_count))
    except IOError as e:
        print(f"Warning: Could not write to checkpoint file '{filename}': {e}")

def load_checkpoint(filename: str = CHECKPOINT_FILE_SCAFFOLDING) -> int:
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                content = f.read().strip()
                if content:
                    return int(content)
                else:
                    print(f"Warning: Checkpoint file '{filename}' is empty. Starting from scratch.")
                    return 0
        except ValueError:
            print(f"Warning: Checkpoint file '{filename}' content is invalid. Starting from scratch.")
            return 0
        except IOError as e:
            print(f"Warning: Could not read checkpoint file '{filename}': {e}. Starting from scratch.")
            return 0
    return 0
# --- End Checkpoint handling ---

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

# Ensure GEMINI_API_KEY is also set if ChatGoogleGenerativeAI prefers it
if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", # Consider 1.5 Flash for speed/cost or Pro for quality
    temperature=0.2, # Slightly higher for more varied scaffolding ideas, but still controlled
    # max_tokens=None, # Let it decide, but be mindful of cost
    # timeout=None,
    # max_retries=2, # Default is often sufficient
    convert_system_message_to_human=True # Good for Gemini
)

async def validate_scaffolding_json(content: str) -> ScaffoldingStrategy | None:
    """Validates and potentially corrects JSON content against ScaffoldingStrategy."""
    try:
        # LLMs sometimes wrap JSON in ```json ... ```
        if content.strip().startswith("```json"):
            content = content.strip()[7:-3].strip()
        elif content.strip().startswith("```"):
             content = content.strip()[3:-3].strip()

        return ScaffoldingStrategy.model_validate_json(content)
    except ValidationError as e_val:
        print(f"Initial Pydantic validation failed: {e_val}")
        # If direct validation fails, try to use an LLM to fix the JSON structure
        # This is an advanced step, for now, let's just log and return None
        # You could try a pydantic-ai agent here or a simpler "fix this JSON" prompt
        print(f"Could not validate JSON: {content[:500]}...") # Log snippet
        return None
    except json.JSONDecodeError as e_json:
        print(f"JSON Decode Error: {e_json}. Content snippet: {content[:500]}...")
        return None
    except Exception as e:
        print(f"Unexpected error during validation: {e}. Content snippet: {content[:500]}...")
        return None


async def generate_scaffolding_strategy(
    persona_dict: dict,
    learning_objective_dict: dict,
    student_q1_ans: str,
    student_q2_ans: str,
    student_q3_ans: str,
    comfort_level: str,
    initial_impression: str,
    struggle_point_desc: str,
) -> ScaffoldingStrategy | None:
    
    persona_name = persona_dict["name"]
    persona_description = persona_dict["description"]
    lo_description = learning_objective_dict["description"]

    prompt_template_str = """
    You are an expert TOEFL teacher acting as the persona: {persona_name}.
    Your teaching philosophy is: {persona_description}

    A student presents with the following profile and situation:
    *   Student's Stated Goal (Q1): "{student_q1_ans}"
    *   Student's Self-Assessed Confidence/Challenge Area (Q2): "{student_q2_ans}"
    *   Student's Current Attitude towards TOEFL (Q3): "{student_q3_ans}"
    *   Estimated Overall English Comfort Level: "{comfort_level}"
    *   Your Initial Pedagogical Impression/Focus for this Student: "{initial_impression}"
    *   Learning Objective/Task Being Attempted: "{lo_description}"
    *   Specific Point of Struggle: "{struggle_point_desc}"

    Given this complete scenario, please detail your scaffolding approach by providing a JSON object adhering to the following Pydantic schema:

    ```json
    {{
        "reasoning_for_scaffold_choice": "str (Your rationale for selecting this specific scaffold type given the student's situation and your persona.)",
        "scaffold_type_selected": "str (A descriptive name of the scaffold type, e.g., 'Detailed Paragraph Template', 'Targeted Guiding Questions', 'Step-by-Step Breakdown', 'Synonym List for Paraphrasing')",
        "scaffold_content_delivered": {{
            "type": "str (Type of content, e.g., 'template', 'sentence_starters', 'guiding_questions', 'hint', 'simplified_steps_list', 'vocabulary_list')",
            "name": "str (Optional descriptive name for the scaffold content, e.g., 'P-E-E Paragraph Template')",
            "content": {{}} // JSON object: For 'template', content could be {{"fields": [{{"label": "Topic:", "placeholder": "..."}}]}}. For 'sentence_starters', {{"starters": ["Firstly...", "Another reason is..."]}}. For 'guiding_questions', {{"questions": ["What is your main point here?", "How does this example support it?"]}}. For 'vocabulary_list', {{"category": "Transition Words", "words": [{{"word": "Furthermore", "usage": "To add another point"}}]}}
        }},
        "scaffold_delivery_script": "str (What you, as the AI teacher persona, would say when introducing/presenting this scaffold.)",
        "guidance_on_use_script": "str (Brief instructions or tips on how the student should use this scaffold effectively.)",
        "monitoring_and_immediate_followup": "str (How you monitor the student's use of the scaffold and what's your immediate next step if they still struggle with the scaffold OR if they use it well.)",
        "fading_strategy_next_step": "str (How this specific scaffold would be reduced or faded in a future, similar task to promote independence. Be specific.)",
        "affective_state_adaptation_notes": "str (How your persona's delivery, tone, or the scaffold itself is adapted due to the student's current attitude/confidence/comfort level as described in their Q2/Q3 answers and overall comfort level.)"
    }}
    ```

    Ensure the output is ONLY the valid JSON object, without any surrounding text or markdown formatting.
    For "scaffold_content_delivered.content", be creative and provide concrete, structured examples. For instance, if providing a 'template', structure it with fields a student could fill. If 'guiding_questions', list several distinct questions.
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
        struggle_point_desc=struggle_point_desc,
    )

    # print(f"---- PROMPT for {persona_name} / {lo_description[:30]}... / {struggle_point_desc[:30]}... ----")
    # print(full_prompt_formatted) # For debugging prompts
    # print("---- END PROMPT ----")

    try:
        response = await llm.ainvoke(full_prompt_formatted) # Use await for async call
        content = response.content
        
        if isinstance(content, str):
            # print(f"---- RAW LLM RESPONSE for {persona_name} / {lo_description[:30]}... ----")
            # print(content) # For debugging raw responses
            # print("---- END RAW LLM RESPONSE ----")
            validated_data = await validate_scaffolding_json(content)
            return validated_data
        else:
            print(f"Unexpected LLM response type: {type(content)}")
            return None
            
    except Exception as e:
        print(f"Error during LLM call or processing for {persona_name} / {lo_description[:30]}...: {e}")
        return None


async def main_scaffolding_generator():
    csv_file_path = "scaffolding_cta_data.csv"
    header_list = [
        "Persona",
        "Learning_Objective_Task",
        "Student_Goal_Context",
        "Student_Confidence_Context",
        "Student_Attitude_Context",
        "English_Comfort_Level",
        "Teacher_Initial_Impression",
        "Specific_Struggle_Point",
        # Columns from ScaffoldingStrategy Pydantic model
        "reasoning_for_scaffold_choice",
        "scaffold_type_selected",
        "scaffold_content_delivered_type", # from ScaffoldContentDetail
        "scaffold_content_delivered_name", # from ScaffoldContentDetail
        "scaffold_content_delivered_content_json", # JSON string of the content dict
        "scaffold_delivery_script",
        "guidance_on_use_script",
        "monitoring_and_immediate_followup",
        "fading_strategy_next_step",
        "affective_state_adaptation_notes",
    ]

    file_exists = os.path.exists(csv_file_path)
    is_empty = False
    if file_exists:
        is_empty = os.path.getsize(csv_file_path) == 0

    needs_header = not file_exists or is_empty

    # --- Create Iteration Space ---
    # We need to iterate through personas, LOs, student profiles, and struggle points.
    # For SPECIFIC_STRUGGLE_POINTS_EXAMPLES, they are tied to LOs.

    scenarios_to_process = []
    for persona_dict in TEACHER_PERSONAS_SCAFFOLDING:
        for lo_dict in LEARNING_OBJECTIVES_OR_TASKS_TO_SCAFFOLD:
            # Find relevant struggle points for this LO
            relevant_struggles = [sp["struggle"] for sp in SPECIFIC_STRUGGLE_POINTS_EXAMPLES if sp["applies_to_lo_id"] == lo_dict["id"]]
            if not relevant_struggles: # If no specific struggle, use a generic one or skip
                relevant_struggles = [f"Student is generally finding it hard to start or progress with '{lo_dict['description']}'."]

            for struggle_desc in relevant_struggles:
                for q1_ans in QUESTION_ONE_ANSWERS:
                    for q2_ans in QUESTION_TWO_ANSWERS:
                        for q3_ans in QUESTION_THREE_ANSWERS:
                            for comfort in ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL:
                                for impression in INITIAL_IMPRESSION:
                                    scenarios_to_process.append({
                                        "persona_dict": persona_dict,
                                        "lo_dict": lo_dict,
                                        "q1_ans": q1_ans,
                                        "q2_ans": q2_ans,
                                        "q3_ans": q3_ans,
                                        "comfort": comfort,
                                        "impression": impression,
                                        "struggle": struggle_desc,
                                    })
    
    total_combinations = len(scenarios_to_process)
    print(f"Total scaffolding scenarios to generate: {total_combinations}")

    completed_from_checkpoint = load_checkpoint()
    
    if completed_from_checkpoint >= total_combinations:
        print("All scaffolding scenarios already processed according to checkpoint.")
        return

    scenarios_this_run = scenarios_to_process[completed_from_checkpoint:]
    print(f"Processing {len(scenarios_this_run)} remaining scaffolding scenarios, starting from index {completed_from_checkpoint}.")

    with open(csv_file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(header_list)

        for i, scenario in enumerate(asyncio_tqdm(scenarios_this_run, total=len(scenarios_this_run), desc="Generating Scaffolding Strategies")):
            current_overall_index = completed_from_checkpoint + i
            
            print(f"\nProcessing scenario {current_overall_index + 1}/{total_combinations}: "
                  f"Persona: {scenario['persona_dict']['name']}, LO: {scenario['lo_dict']['description'][:30]}..., "
                  f"Struggle: {scenario['struggle'][:30]}...")

            # Basic rate limiting / retry mechanism can be added here if needed
            # For Gemini, be mindful of queries per minute (QPM) limits.
            # A small sleep can help if you hit limits frequently.
            # await asyncio.sleep(1) # Example: 1 QPS if needed

            res_strategy: ScaffoldingStrategy | None = await generate_scaffolding_strategy(
                persona_dict=scenario["persona_dict"],
                learning_objective_dict=scenario["lo_dict"],
                student_q1_ans=scenario["q1_ans"],
                student_q2_ans=scenario["q2_ans"],
                student_q3_ans=scenario["q3_ans"],
                comfort_level=scenario["comfort"],
                initial_impression=scenario["impression"],
                struggle_point_desc=scenario["struggle"],
            )

            if res_strategy:
                writer.writerow([
                    scenario["persona_dict"]["name"],
                    scenario["lo_dict"]["description"],
                    scenario["q1_ans"],
                    scenario["q2_ans"],
                    scenario["q3_ans"],
                    scenario["comfort"],
                    scenario["impression"],
                    scenario["struggle"],
                    res_strategy.reasoning_for_scaffold_choice,
                    res_strategy.scaffold_type_selected,
                    res_strategy.scaffold_content_delivered.type,
                    res_strategy.scaffold_content_delivered.name,
                    json.dumps(res_strategy.scaffold_content_delivered.content), # Store content as JSON string
                    res_strategy.scaffold_delivery_script,
                    res_strategy.guidance_on_use_script,
                    res_strategy.monitoring_and_immediate_followup,
                    res_strategy.fading_strategy_next_step,
                    res_strategy.affective_state_adaptation_notes,
                ])
                print(f"Successfully generated and wrote strategy for scenario {current_overall_index + 1}.")
            else:
                # Log the failure to a separate error file perhaps, or just print
                print(f"Failed to generate or validate strategy for scenario {current_overall_index + 1}. Skipping.")
                # Optionally write a row with N/A for strategy fields to keep row count aligned
                writer.writerow([
                    scenario["persona_dict"]["name"],
                    scenario["lo_dict"]["description"],
                    scenario["q1_ans"],
                    scenario["q2_ans"],
                    scenario["q3_ans"],
                    scenario["comfort"],
                    scenario["impression"],
                    scenario["struggle"],
                    "FAILED_TO_GENERATE", "", "", "", "", "", "", "", "", ""
                ])


            save_checkpoint(current_overall_index + 1)
            


if __name__ == "__main__":
    asyncio.run(main_scaffolding_generator())