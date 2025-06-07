# data_scaffolding.py (or add to your existing data.py)

# --- Dimensions from your existing data.py (we'll reuse these) ---
QUESTION_ONE_ANSWERS = [
    "Great to meet you too! My main goal is to score at least 105 on the TOEFL. I'm especially focused on the speaking and writing sections since I need strong scores for my graduate school applications.",
    "Thanks! I'm mainly using this tutor to improve my speaking skills. I find it hard to organize my thoughts and speak clearly under the time limit, so I want to practice giving structured responses.",
    "Hi! I'm preparing for the TOEFL because I plan to apply to U.S. universities. My biggest goal is to strengthen my academic writing and listening skills so I can perform well in real classroom settings.",
]

QUESTION_TWO_ANSWERS = [
    "I feel fairly confident overall. I can understand lectures and academic texts pretty well, but I still want to polish my writing and make sure my speaking sounds more natural and fluent, especially under time pressure.",
    "I think I'm okay with reading and listening, but I struggle a bit with writing essays—especially organizing my ideas and using academic vocabulary. I'd like to improve that before test day.",
    "Honestly, I feel a bit nervous about the academic tasks. I sometimes get lost during lectures or have trouble expressing my ideas clearly in writing. I'm hoping this tutoring will help me feel more prepared and confident.",
]

QUESTION_THREE_ANSWERS = [
    "I'm honestly a bit nervous. It feels like a big challenge, especially because of the time limits and pressure. But I'm motivated to put in the work and improve—I just need some guidance and practice.",
    "I feel okay about it. I know I still have some weak spots, but I think with regular practice and some support, I can definitely reach my target score. I'm trying to stay positive.",
    "I actually feel pretty good about it! I've been studying for a while, so now I just want to fine-tune my performance and get used to the test format. I'm aiming to stay calm and focused on test day.",
]

ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL = [
    "Beginner",
    "Conversational",
    "Fluent",
    "Proficient",
    # "Near-Native", # Let's focus on levels where scaffolding is more distinct initially
    # "Native",
]

INITIAL_IMPRESSION = [ # How the AI teacher initially assesses student needs
    "Needs Foundational Support",
    "Needs Skill-Specific Drills",
    "Needs Confidence Building & Practice",
    "Needs Strategic Refinement for Test",
]

# We can use these for general context, but the struggle will be more specific
# SPEAKING_STRENGTHS = ["Clear Pronunciation", "Logical Organization", "Good Vocabulary Range"]
# FLUENCY = ["Developing", "Functional", "Natural & Effortless"]
# GRAMMAR = ["Basic Grammatical Control", "Moderate Grammatical Accuracy", "Advanced Grammatical Range & Precision"]
# VOCAB = ["Limited Lexical Resource", "Adequate Lexical Range", "Rich & Precise Lexical Use"]

# --- NEW DIMENSIONS FOR SCAFFOLDING ---

TEACHER_PERSONAS_SCAFFOLDING = [
    {
        "name": "The Structuralist",
        "description": "You are 'The Structuralist,' an English teacher who emphasizes organization, clarity, and logic in communication. Your teaching philosophy focuses on helping learners master structured templates for writing and speaking. You give direct, no-nonsense feedback and clearly point out logical or structural flaws. Use clear examples, step-by-step templates, and encourage outlining, paragraph structure, and logical transitions. Your goal is to help the learner develop rigorously organized responses in both written and spoken formats."
    },
    {
        "name": "The Encouraging Nurturer",
        "description": "You are 'The Encouraging Nurturer,' an English teacher who believes in building student confidence and creating a supportive learning environment. Your philosophy is that students learn best when they feel safe to make mistakes and are encouraged for their efforts. You provide gentle guidance, lots of positive reinforcement, and try to make learning relatable and less intimidating. You break down complex tasks into very small, achievable steps and celebrate every success."
    },
    # Add more personas if you wish
]

LEARNING_OBJECTIVES_OR_TASKS_TO_SCAFFOLD = [
    {"id": "S_Q1_Fluency", "description": "Speaking Fluently for TOEFL Speaking Question 1 (Independent Task - e.g., giving an opinion)"},
    {"id": "S_Q1_Structure", "description": "Structuring a Response for TOEFL Speaking Question 1 (e.g., Opinion + Reason 1 + Example 1 + Reason 2 + Example 2)"},
    {"id": "W_Ind_Thesis", "description": "Writing a Clear Thesis Statement for TOEFL Independent Essay"},
    {"id": "W_Ind_BodyPara_PEE", "description": "Developing a Body Paragraph (Point-Evidence-Explanation) for TOEFL Independent Essay"},
    {"id": "W_Int_ParaphraseRead", "description": "Paraphrasing a key point from the Reading Passage for TOEFL Integrated Writing"},
    {"id": "W_Int_SynthesizeListenRead", "description": "Synthesizing a point from the Listening Passage with a point from the Reading Passage for TOEFL Integrated Writing"},
    {"id": "G_SVA", "description": "Correctly using Subject-Verb Agreement in sentences"},
    {"id": "G_PastTense", "description": "Correctly using Simple Past Tense to describe past events"},
    {"id": "V_AcademicWords", "description": "Using appropriate Academic Vocabulary instead of informal words"},
]

SPECIFIC_STRUGGLE_POINTS_EXAMPLES = [ # Examples of where a student might get stuck for a given LO
    {"applies_to_lo_id": "W_Ind_Thesis", "struggle": "Student has written a topic but not an arguable thesis. They say 'I don't know what my main argument is.'"},
    {"applies_to_lo_id": "W_Ind_BodyPara_PEE", "struggle": "Student wrote a topic sentence for a body paragraph but is staring at a blank page, unsure how to provide evidence or explanation."},
    {"applies_to_lo_id": "S_Q1_Fluency", "struggle": "Student starts speaking but hesitates frequently after the first few words, using many filler words like 'um' and 'uh'."},
    {"applies_to_lo_id": "S_Q1_Structure", "struggle": "Student gives an opinion but then rambles without clearly distinct reasons or examples."},
    {"applies_to_lo_id": "G_SVA", "struggle": "Student consistently makes subject-verb agreement errors when the subject is 'he/she/it'."},
    {"applies_to_lo_id": "W_Int_ParaphraseRead", "struggle": "Student's attempt to paraphrase is too close to the original text from the reading passage."},
]

# You can expand this significantly. For generation, you might iterate through LOs and then
# pair them with a few representative struggle points, or even ask the LLM to imagine
# a typical struggle point for that LO and proficiency.