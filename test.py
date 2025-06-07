"""
Test script for the language modelling 
"""

import os
import json
import asyncio
import random
import csv
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from main_modelling import generate_correction_example, save_to_csv
from data_modelling import TOPICS, PROFICIENCY_LEVELS, TASK_TYPES


async def test_generator():
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    if "GOOGLE_API_KEY" not in os.environ or not os.environ["GOOGLE_API_KEY"]:
        print("Please set GOOGLE_API_KEY in your .env file")
        return
    
    # Set Gemini API key
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
    
    # Initialize the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.2,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    # Pick random elements for the test
    topic = random.choice(TOPICS)
    proficiency_level = random.choice(PROFICIENCY_LEVELS)
    task_type = random.choice(TASK_TYPES)
    
    print(f"\nGenerating a language correction example with:")
    print(f"Topic: {topic}")
    print(f"Proficiency Level: {proficiency_level}")
    print(f"Task Type: {task_type}")
    print("\nGenerating response... (this may take a moment)\n")
    
    # Generate an example
    correction_example = await generate_correction_example(
        topic=topic,
        proficiency_level=proficiency_level,
        task_type=task_type,
        llm=llm
    )
    
    if correction_example:
        # Print the result in a readable format
        print("\n=== GENERATED EXAMPLE ===\n")
        print(f"TOPIC: {correction_example.topic}")
        print(f"PROFICIENCY LEVEL: {correction_example.proficiency_level}")
        print(f"TASK TYPE: {correction_example.task_type}")
        print(f"MISTAKE TYPES: {', '.join(correction_example.mistake_type)}")
        print("\n--- INCORRECT VERSION ---\n")
        print(correction_example.incorrect_version)
        print("\n--- THOUGHT PROCESS ---\n")
        print(correction_example.thought_process)
        print("\n--- CORRECT VERSION ---\n")
        print(correction_example.correct_version)
        
        # Convert to a dictionary for saving
        example_dict = correction_example.model_dump()
        
        # Save to JSON
        with open("test_example.json", "w") as f:
            json.dump(example_dict, f, indent=2)
        
        # Save to CSV
        save_to_csv([example_dict], "test_example.csv")
            
        print("\nExample saved to test_example.json and test_example.csv")
    else:
        print("Failed to generate an example. Check for errors in the console output.")


if __name__ == "__main__":
    asyncio.run(test_generator())
