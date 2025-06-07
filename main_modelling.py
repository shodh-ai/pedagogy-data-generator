"""
Creates synthetic data with incorrect language samples, thought processes, and corrected versions.
"""

import os
import json
import csv
import getpass
import asyncio
import random
import itertools
from datetime import datetime
from tqdm.asyncio import tqdm as asyncio_tqdm
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError
from pydantic_ai import Agent

from schema_modelling import CorrectionExample
from data_modelling import (
    TOPICS,
    PROFICIENCY_LEVELS,
    GRAMMAR_MISTAKES,
    VOCABULARY_MISTAKES,
    STRUCTURE_MISTAKES,
    SPEAKING_SPECIFIC_MISTAKES, 
    WRITING_SPECIFIC_MISTAKES,
    TASK_TYPES
)

CHECKPOINT_FILE = "checkpoint.txt"
OUTPUT_JSON_FILE = "correction_examples.json"
OUTPUT_CSV_FILE = "correction_examples.csv"
BATCH_SIZE = 10


def save_checkpoint(completed_count: int):
    """Saves the number of completed combinations to the checkpoint file."""
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(str(completed_count))
    except IOError as e:
        print(f"Warning: Could not write to checkpoint file '{CHECKPOINT_FILE}': {e}")


def load_checkpoint() -> int:
    """Loads the number of completed combinations from the checkpoint file."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return int(content)
                else:
                    print(f"Warning: Checkpoint file '{CHECKPOINT_FILE}' is empty. Starting from scratch.")
                    return 0
        except ValueError:
            print(f"Warning: Checkpoint file '{CHECKPOINT_FILE}' content is invalid. Starting from scratch.")
            return 0
        except IOError as e:
            print(f"Warning: Could not read checkpoint file '{CHECKPOINT_FILE}': {e}. Starting from scratch.")
            return 0
    return 0


def save_to_csv(dataset, csv_filename):
    """Save the dataset to a CSV file.
    
    Args:
        dataset: List of dictionaries containing correction examples
        csv_filename: Name of the CSV file to save to
    """
    if not dataset:
        print("No data to save to CSV.")
        return
        
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Get all fields from the first example
            fieldnames = list(dataset[0].keys())
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for example in dataset:
                # Process the example data to make it CSV-friendly
                row = {}
                for key, value in example.items():
                    if key == 'mistake_type' and isinstance(value, list):
                        # Convert list to pipe-separated string
                        row[key] = '|'.join(value)
                    elif isinstance(value, str):
                        # Replace newlines with space to keep CSV format clean
                        row[key] = value.replace('\n', ' ').replace('\r', '')
                    else:
                        row[key] = value
                writer.writerow(row)
                
        print(f"Successfully wrote {len(dataset)} examples to {csv_filename}")
    except Exception as e:
        print(f"Error writing to CSV: {e}")


def select_mistake_types(task_type: str):
    """Select relevant mistake types based on the task type (speaking or writing)."""
    common_mistakes = GRAMMAR_MISTAKES + VOCABULARY_MISTAKES + STRUCTURE_MISTAKES
    
    if task_type == "speaking":
        return common_mistakes + SPEAKING_SPECIFIC_MISTAKES
    else:
        return common_mistakes + WRITING_SPECIFIC_MISTAKES


async def data_validation(content: str) -> CorrectionExample | None:
    """Validate and parse the AI output into our CorrectionExample schema."""
    try:
        return CorrectionExample.model_validate_json(content)
    except ValidationError:
        try:
            agent = Agent(
                "gemini-2.0-flash",
                result_type=CorrectionExample,
                retries=5,
            )
            res = await agent.run(content)
            return res.output
        except ValidationError as e:
            print("Got output but cannot convert it to object. Error: ", e)
            return None
        except Exception as e:
            print("Got output but cannot convert it to object. Error: ", e)
            return None


async def generate_correction_example(
    topic: str,
    proficiency_level: str,
    task_type: str,
    llm
) -> CorrectionExample | None:
    """Generate a correction example using the LLM."""
    all_mistake_types = select_mistake_types(task_type)
    num_mistakes = random.randint(1, min(3, len(all_mistake_types)))
    selected_mistake_types = random.sample(all_mistake_types, num_mistakes)
    
    prompt_template = PromptTemplate(
        input_variables=["topic", "proficiency_level", "task_type", "mistake_types"],
        template="""
        You are an expert language instructor who specializes in identifying and correcting language errors. 
        Create a realistic example of a language learning situation with the following components:

        Topic to {task_type} about: {topic}
        Student's proficiency level: {proficiency_level}
        Types of mistakes to include: {mistake_types}

        1. First, create a realistic {task_type} sample containing the specified mistakes that a student at this level might make. 
           The mistakes should be natural and realistic for the proficiency level, not exaggerated.

        2. Next, provide a detailed thought process analyzing the mistakes, explaining why they are incorrect 
           and how they impact comprehension or clarity.

        3. Finally, provide a fully corrected version that maintains the same meaning and intent but fixes all errors.

        Return your response in this exact JSON format:
        {{
            "topic": "{topic}",
            "proficiency_level": "{proficiency_level}",
            "mistake_type": {mistake_types},
            "incorrect_version": "The incorrect {task_type} sample with realistic errors",
            "thought_process": "Your detailed analysis of the errors, including grammatical explanations, alternative word choices, etc.",
            "correct_version": "The fully corrected version of the {task_type} sample",
            "task_type": "{task_type}"
        }}
        
        IMPORTANT: Make sure both versions are of similar length and cover the same content - the correct version should be a direct correction of the incorrect one, not a different text.
        """
    )
    
    prompt = prompt_template.format(
        topic=topic,
        proficiency_level=proficiency_level,
        task_type=task_type,
        mistake_types=str(selected_mistake_types)
    )
    
    try:
        response = await llm.ainvoke(prompt)
        content = response.content
        
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_content = content[json_start:json_end]
            return await data_validation(json_content)
        else:
            print("No JSON found in response")
            return None
            
    except Exception as e:
        print(f"Error generating correction example: {e}")
        return None


async def main():
    load_dotenv()
    
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    combinations = list(itertools.product(TOPICS, PROFICIENCY_LEVELS, TASK_TYPES))
    total_combinations = len(combinations)
    print(f"Total number of combinations: {total_combinations}")
    
    completed_count = load_checkpoint()
    print(f"Starting from combination {completed_count + 1} of {total_combinations}")
    
    dataset = []
    if os.path.exists(OUTPUT_JSON_FILE):
        try:
            with open(OUTPUT_JSON_FILE, "r") as f:
                existing_data = json.load(f)
                dataset = existing_data.get("examples", [])
                print(f"Loaded {len(dataset)} existing examples")
        except Exception as e:
            print(f"Error loading existing data: {e}")
    
    batch_counter = 0
    for i, (topic, proficiency_level, task_type) in enumerate(combinations[completed_count:], start=completed_count):
        try:
            print(f"Processing combination {i + 1}/{total_combinations}: {topic[:30]}... ({proficiency_level}, {task_type})")
            
            correction_example = await generate_correction_example(
                topic=topic,
                proficiency_level=proficiency_level,
                task_type=task_type,
                llm=llm
            )
            
            if correction_example:
                dataset.append(correction_example.model_dump())
                batch_counter += 1
                
                if batch_counter >= BATCH_SIZE:
                    save_checkpoint(i + 1)
                    
                    # Save to JSON
                    with open(OUTPUT_JSON_FILE, "w") as f:
                        json.dump({"examples": dataset, "metadata": {
                            "last_updated": datetime.now().isoformat(),
                            "total_examples": len(dataset)
                        }}, f, indent=2)
                    
                    # Save to CSV
                    save_to_csv(dataset, OUTPUT_CSV_FILE)
                    
                    print(f"Saved checkpoint at combination {i + 1} and wrote {len(dataset)} examples to {OUTPUT_JSON_FILE} and {OUTPUT_CSV_FILE}")
                    batch_counter = 0
                    
        except Exception as e:
            print(f"Error processing combination: {e}")
    
    save_checkpoint(total_combinations)
    
    # Save final JSON output
    with open(OUTPUT_JSON_FILE, "w") as f:
        json.dump({"examples": dataset, "metadata": {
            "last_updated": datetime.now().isoformat(),
            "total_examples": len(dataset),
            "completion": "full"
        }}, f, indent=2)
    
    # Save final CSV output
    save_to_csv(dataset, OUTPUT_CSV_FILE)
    
    print(f"Generation complete! {len(dataset)} examples written to {OUTPUT_JSON_FILE} and {OUTPUT_CSV_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
