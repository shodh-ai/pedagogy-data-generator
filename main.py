import getpass
import os
import itertools
from tqdm.asyncio import tqdm as asyncio_tqdm
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError
from pydantic_ai import Agent
from data import (
    QUESTION_ONE_ANSWERS,
    QUESTION_TWO_ANSWERS,
    QUESTION_THREE_ANSWERS,
    ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL,
    INITIAL_IMPRESSION,
    SPEAKING_STRENGTHS,
    FLUENCY,
    GRAMMAR,
    VOCAB,
)

CHECKPOINT_FILE = "checkpoint.txt"


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
                    print(
                        f"Warning: Checkpoint file '{CHECKPOINT_FILE}' is empty. Starting from scratch."
                    )
                    return 0
        except ValueError:
            print(
                f"Warning: Checkpoint file '{CHECKPOINT_FILE}' content is invalid. Starting from scratch."
            )
            return 0
        except IOError as e:
            print(
                f"Warning: Could not read checkpoint file '{CHECKPOINT_FILE}': {e}. Starting from scratch."
            )
            return 0
    return 0


from schema import Pedagogy
import asyncio
import csv
import json

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


async def data_validation(content: str) -> Pedagogy | None:
    try:
        return Pedagogy.model_validate_json(content)
    except ValidationError:
        try:
            agent = Agent(
                "gemini-2.0-flash",
                result_type=Pedagogy,
                retries=5,
            )
            res = await agent.run(content)
            res = res.output
            return res
        except ValidationError as e:
            print("Got output but cannot convert it to object. Error: ", e)
            return None
        except Exception as e:
            print("Got output but cannot convert it to object. Error: ", e)
            return None


async def get_feedback(
    answer_one_index: int,
    answer_two_index: int,
    answer_three_index: int,
    estimated_overall_english_comfort_level_index: int,
    initial_impression_index: int,
    speaking_strengths_index: int,
    fluency_index: int,
    grammar_index: int,
    vocab_index: int,
) -> Pedagogy | None:
    answer_one = QUESTION_ONE_ANSWERS[answer_one_index]
    answer_two = QUESTION_TWO_ANSWERS[answer_two_index]
    answer_three = QUESTION_THREE_ANSWERS[answer_three_index]
    estimated_overall_english_comfort_level = ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL[
        estimated_overall_english_comfort_level_index
    ]
    initial_impression = INITIAL_IMPRESSION[initial_impression_index]
    speaking_strengths = SPEAKING_STRENGTHS[speaking_strengths_index]
    fluency = FLUENCY[fluency_index]
    grammar = GRAMMAR[grammar_index]
    vocab = VOCAB[vocab_index]

    prompt_template = PromptTemplate(
        input_variables=[
            "answer_one",
            "answer_two",
            "answer_three",
            "estimated_level",
            "initial_impression",
            "speaking_strengths",
            "fluency",
            "grammar",
            "vocab",
        ],
        template="""
        You have to design a pedagogy for teaching a student the learning objectives:
        
        ## Learning Objectives

        Speaking:
            Fluency & Pronunciation: Speak clearly and naturally with consistent pacing, proper intonation, and accurate pronunciation.
            Grammar & Vocabulary: Use a variety of sentence structures and precise vocabulary accurately.

        Writing:
            Structure & Style: Construct well-organized paragraphs and essays with varied sentence types, maintaining a formal academic tone.
            Mechanics: Type with sufficient speed and accuracy for timed essays.

        Listening:
            Comprehension: Identify main ideas, supporting details, speaker purpose, and attitude in both academic lectures and campus conversations.
            Note-Taking: Develop and use a systematic note-taking method to capture key information and structure.

        Reading:
            Comprehension: Quickly identify main ideas, locate specific details, and understand paragraph structure using skimming and scanning.
            Analysis: Answer questions about factual information, inferences, vocabulary in context, author's purpose, and sentence paraphrasing.

        Grammar & Vocabulary:
            Grammar: Master sentence structure (avoiding fragments/run-ons), verb tenses, passive voice, conditionals, clauses, and correct punctuation.
            Vocabulary: Understand and use high-frequency academic words, recognize different word forms, and infer meaning from context.

        General Test Strategies
            Time Management: Pace yourself effectively through all sections and make strategic decisions on difficult questions.
            Summarization: For integrated tasks, identify and accurately summarize the most important points from the source material.
            Synthesis: Clearly connect and explain the relationship between ideas from reading and listening passages.
        
        The student was asked the fllowing questions and he gave the respective answers:
        Q1. What’s your main goal for using this tutor? For example, are you aiming for a specific score, focusing on improving speaking, writing, or something else?
        Ans. {answer_one}
        Q2. How do you generally feel about your current English skills when it comes to academic tasks like those on the TOEFL?
        Ans. {answer_two}
        Q3. And how are you feeling about tackling the TOEFL exam itself right now?
        Ans. {answer_three}

        Also a simple proficiency test was taken which gave the following parameters:
        Estimated Overall English Comfort Level: {estimated_overall_english_comfort_level}
        Initial Impression: {initial_impression}
        Speaking Strengths: {speaking_strengths}
        Fluency: {fluency}
        Grammar: {grammar}
        Vocabulary: {vocab}

        In order to design the Pedagogy you have the following at your disposal:
        - Teaching: Teach Student any topic out of Learning Objective. It will be a lecture only and there will be no hands-on here.
        - Modelling: Here the teacher will perform the task and the student can observer and learn.
        - Scaffolding: Here the teacher will do some part of the task and rest will be done by the student
        - Cowriting: Here the teacher will observe and the student will perform all the tasks. The teacher will act as a guide for the student. It's a writing specific task.
        - Test: Here the student will perform the task and the teacher will provide feedback at the end

        Each of these tasks can be done for both Speaking and Writing (except cowriting). And the Pedagogy should cover all learning objectives.

        ## Output Format
        The output is a strict json of the format:
        {{
            "reasoning": "The overall reasoning behind the pedagogy. Why did you choose the order you did? Why not any other order? Is the response personalised for the student, etc."
            "steps": [
                {{
                    "type": "Module type out of Teaching, Modelling, Scaffolding, Cowriting and Test",
                    "task": "speaking or writing",
                    "topic": "If teaching which topic out of learning objective. If any other the topic the student will be expected to write or speak upon. Try to make it varied topics so the student doesn't feel comfort or discomfort.",
                    "level": "Level of the task: Basic, Intermediate, Advanced",
                }},
            ]
        }}
        
        ## Expected Output
        A pure JSON following the structure defined without any explanation or markdown.
        Output:
    """,
    )
    full_prompt = prompt_template.format(
        answer_one=answer_one,
        answer_two=answer_two,
        answer_three=answer_three,
        estimated_overall_english_comfort_level=estimated_overall_english_comfort_level,
        initial_impression=initial_impression,
        speaking_strengths=speaking_strengths,
        fluency=fluency,
        grammar=grammar,
        vocab=vocab,
    )

    response = llm.invoke(full_prompt)
    content = response.content
    try:
        if content is None:
            return None
        elif isinstance(content, list):
            first_item = content[0] if content else None
            if isinstance(first_item, str):
                res = await data_validation(first_item)
                return res
            elif isinstance(first_item, dict):
                visualization_json = Pedagogy(**first_item)
                return visualization_json
            else:
                print("Invalid output format")
                return None
        elif isinstance(content, str):
            res = await data_validation(content)
            return res
        else:
            print("Got output but cannot convert it to object")
            return None
    except (json.JSONDecodeError, ValidationError) as e:
        print("Got output but cannot convert it to json")
        return None


async def main():

    csv_file_path = "data.csv"
    header_list = [
        "Answer One",
        "Answer Two",
        "Answer Three",
        "Estimated Overall English Comfort Level",
        "Initial Impression",
        "Speaking Strengths",
        "Fluency",
        "Grammar",
        "Vocabulary",
        "Pedagogy",
    ]

    file_exists = os.path.exists(csv_file_path)
    is_empty = False
    if file_exists:
        try:
            is_empty = os.path.getsize(csv_file_path) == 0
        except OSError:
            pass

    needs_header = not file_exists or is_empty

    with open(csv_file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(header_list)

        possible_combinations = (
            len(QUESTION_ONE_ANSWERS)
            * len(QUESTION_TWO_ANSWERS)
            * len(QUESTION_THREE_ANSWERS)
            * len(ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL)
            * len(INITIAL_IMPRESSION)
            * len(SPEAKING_STRENGTHS)
            * len(FLUENCY)
            * len(GRAMMAR)
            * len(VOCAB)
        )

        completed_from_checkpoint = load_checkpoint()
        completed_combinations_overall = completed_from_checkpoint

        all_answer_lists = [
            list(range(len(QUESTION_ONE_ANSWERS))),
            list(range(len(QUESTION_TWO_ANSWERS))),
            list(range(len(QUESTION_THREE_ANSWERS))),
            list(range(len(ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL))),
            list(range(len(INITIAL_IMPRESSION))),
            list(range(len(SPEAKING_STRENGTHS))),
            list(range(len(FLUENCY))),
            list(range(len(GRAMMAR))),
            list(range(len(VOCAB))),
        ]

        index_combinations_full = list(itertools.product(*all_answer_lists))

        if completed_from_checkpoint > 0:
            print(
                f"Resuming from {completed_from_checkpoint} previously completed combinations out of {possible_combinations} total."
            )

        combinations_to_process_this_run = index_combinations_full[
            completed_from_checkpoint:
        ]

        if not combinations_to_process_this_run:
            print(
                f"All {possible_combinations} combinations have already been processed according to the checkpoint."
            )
            return

        print(
            f"Processing {len(combinations_to_process_this_run)} remaining combinations."
        )

        async for indices in asyncio_tqdm(
            combinations_to_process_this_run,
            total=possible_combinations,
            initial=completed_from_checkpoint,
            desc="Generating Feedback",
        ):
            i, j, k, l, m, n, o, p, q = indices
            res = await get_feedback(i, j, k, l, m, n, o, p, q)
            if res is not None:
                writer.writerow(
                    [
                        QUESTION_ONE_ANSWERS[i],
                        QUESTION_TWO_ANSWERS[j],
                        QUESTION_THREE_ANSWERS[k],
                        ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL[l],
                        INITIAL_IMPRESSION[m],
                        SPEAKING_STRENGTHS[n],
                        FLUENCY[o],
                        GRAMMAR[p],
                        VOCAB[q],
                        res.model_dump(),
                    ]
                )
                completed_combinations_overall += 1
                save_checkpoint(completed_combinations_overall)


if __name__ == "__main__":
    asyncio.run(main())
