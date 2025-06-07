# data_modeling.py

# --- Dimensions from your existing data.py / data_scaffolding.py (reuse as needed) ---
# We'll need student profile context to tailor the modeling's complexity and think-aloud.
QUESTION_ONE_ANSWERS = [
    "My main goal is to score 105+ for grad school, focusing on speaking and writing.",
    "I need to improve my speaking organization and clarity under time pressure.",
    "I want to strengthen academic writing and listening for university readiness.",
]

QUESTION_TWO_ANSWERS = [
    "I'm fairly confident, but want to polish writing and make speaking more natural under pressure.",
    "Reading/listening are okay, but I struggle with essay organization and academic vocab.",
    "A bit nervous about academic tasks; sometimes get lost or can't express ideas clearly.",
]

QUESTION_THREE_ANSWERS = [
    "Nervous, feels like a big challenge, but motivated to work and improve with guidance.",
    "Okay, some weak spots, but positive I can reach my target with practice.",
    "Pretty good! Been studying, now want to fine-tune and get used to the test format.",
]

ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL = [
    "Beginner",        # AI Model might be very simple, think-aloud very explicit
    "Conversational",  # AI Model can be slightly more complex
    "Fluent",          # AI Model can use more natural language, think-aloud more nuanced
    "Proficient",      # AI Model can showcase advanced techniques
]

INITIAL_IMPRESSION_FOR_STUDENT = [ # Teacher's initial take on what student needs generally
    "Needs Foundational Support in this Skill Area",
    "Needs to See Clear Application of Strategies",
    "Needs Refinement of Existing Skills",
]

# --- NEW DIMENSIONS SPECIFIC TO MODELING ---

TEACHER_PERSONAS_MODELING = [
    {
        "name": "The Structuralist",
        "description": "You are 'The Structuralist,' an English teacher who emphasizes organization, clarity, and logic. When modeling, you break down the task into clear steps, explicitly state the templates or structures you are using, and explain the logical connections between ideas. Your think-aloud is very methodical."
    },
    {
        "name": "The Nurturer",
        "description": "You are 'The Nurturer,' an English teacher focused on building confidence. When modeling, you demonstrate a positive approach, normalize making small adjustments, and your think-aloud might include encouraging self-talk or how you overcome slight uncertainties. You emphasize clarity and effective communication over perfection."
    },
    {
        "name": "The Interactive Explorer", # New persona example
        "description": "You are 'The Interactive Explorer,' an English teacher who models by thinking through options and making choices aloud. You might present a couple of ways to phrase something and explain why you picked one. Your think-aloud is more of a live problem-solving process."
    }
]

# What specific skill/concept is the AI modeling within a larger task?
LEARNING_OBJECTIVE_BEING_MODELED = [
    # Speaking Modeling Examples
    {"id": "S_Q1_Model_PREP", "task_type": "Speaking", "description": "Modeling a Speaking Q1 response using the PREP structure (Point, Reason, Example, Point)"},
    {"id": "S_Q2_Model_Synth", "task_type": "Speaking", "description": "Modeling how to synthesize reading and listening points for Speaking Q2"},
    {"id": "S_Model_FluencyTechnique", "task_type": "Speaking", "description": "Modeling a fluency technique (e.g., chunking, strategic pausing) during a speaking response"},
    {"id": "S_Model_PronunciationFocus", "task_type": "Speaking", "description": "Modeling a speaking response while consciously focusing on and correctly articulating a specific challenging phoneme"},

    # Writing Modeling Examples
    {"id": "W_Ind_Model_Thesis", "task_type": "Writing", "description": "Modeling the process of crafting a strong thesis statement for an Independent Essay"},
    {"id": "W_Ind_Model_BodyPara_PEE", "task_type": "Writing", "description": "Modeling writing a coherent body paragraph (Point-Evidence-Explanation) for an Independent Essay"},
    {"id": "W_Ind_Model_Transitions", "task_type": "Writing", "description": "Modeling the use of effective transition words/phrases between paragraphs in an Independent Essay"},
    {"id": "W_Int_Model_Paraphrase", "task_type": "Writing", "description": "Modeling how to effectively paraphrase a segment from a reading passage for an Integrated Essay"},
    {"id": "W_Int_Model_Synthesis", "task_type": "Writing", "description": "Modeling how to synthesize information from the reading and listening passages in an Integrated Essay, showing clear connections"},
    {"id": "W_Model_SelfCorrection", "task_type": "Writing", "description": "Modeling the process of writing a sentence, then 'realizing' a small error (e.g., grammar, word choice) and self-correcting with explanation"},
]

# Example TOEFL Prompts (You'll need a bank of these, relevant to the LO being modeled)
# For simplicity, we'll just use a placeholder here, but in reality, you'd select a relevant prompt.
EXAMPLE_TOEFL_PROMPTS_FOR_MODELING = [
    {"id": "IndEssay_CityLife", "type": "Independent Writing", "prompt_text": "Do you agree or disagree with the following statement? Living in a big city is better than living in a small town. Use specific reasons and examples to support your answer."},
    {"id": "SpkQ1_FavoriteBook", "type": "Speaking Q1", "prompt_text": "Describe your favorite book and explain why you like it so much."},
    {"id": "IntWrite_ReadingListeningArt", "type": "Integrated Writing", "reading_summary": "The reading passage discusses the historical significance of Renaissance art, focusing on its realism.", "listening_summary": "The lecturer challenges the reading's view, arguing that Renaissance art often idealized subjects rather than depicting pure realism, citing examples of portraiture."}
]

# What is the student generally struggling with that warrants this modeling session?
STUDENT_STRUGGLE_CONTEXT_FOR_MODELING = [
    "Student has difficulty starting tasks.",
    "Student's responses often lack clear structure.",
    "Student struggles to connect ideas coherently.",
    "Student finds it hard to apply [specific concept] in practice.",
    "Student has asked for an example of how to do [specific skill].",
    "Student is proficient but needs to see a high-scoring example for refinement."
]