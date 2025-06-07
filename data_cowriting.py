# data_cowriting.py

# --- Reused Dimensions from previous data files ---
TEACHER_PERSONAS_COWRITING = [
    {
        "name": "The Structuralist",
        "description": "You are 'The Structuralist,' an English teacher who emphasizes organization, clarity, and logic. When co-writing, you provide direct feedback on structure, thesis strength, topic sentences, transitions, and logical fallacies. You offer clear templates and expect adherence to academic writing conventions."
    },
    {
        "name": "The Encouraging Nurturer",
        "description": "You are 'The Encouraging Nurturer,' an English teacher focused on building student confidence. During co-writing, you praise effort, gently guide students towards better phrasing, focus on their ideas first, and offer suggestions in a supportive way. You aim to make the writing process less intimidating and encourage self-expression."
    },
    {
        "name": "The Interactive Explorer",
        "description": "You are 'The Interactive Explorer,' an English teacher who co-writes by posing questions, exploring alternatives with the student, and prompting them to justify their choices. You might offer several ways to phrase something and discuss the pros and cons of each. Your goal is to develop the student's critical thinking about their own writing."
    },
    {
        "name": "The Pragmatic Strategist",
        "description": "You are 'The Pragmatic Strategist,' an English teacher focused on TOEFL success. During co-writing, you prioritize task fulfillment, efficient argumentation, appropriate vocabulary for the test, and time management. You offer direct, actionable advice to maximize scoring potential."
    }
]

ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL = [
    "Beginner",
    "Conversational",
    "Fluent",
    "Proficient",
]

# Using INITIAL_IMPRESSION_FOR_STUDENT as a proxy for current student affective state during co-writing
# In a real system, this would be more dynamic based on ongoing interaction.
STUDENT_AFFECTIVE_STATE_PROXY = [
    "Focused and Receptive", # Was "Needs Foundational Support..."
    "Slightly Stuck but Trying",    # Was "Needs Skill-Specific Drills..."
    "Lacking Confidence / Anxious", # Was "Needs Confidence Building..."
    "Overconfident / Rushing",   # Was "Needs Strategic Refinement..."
    "Frustrated with this Section"
]

# --- NEW DIMENSIONS SPECIFIC TO CO-WRITING ---

# What part of the TOEFL writing task is the student currently working on?
WRITING_TASK_CONTEXTS = [
    {"task_type": "Independent Essay", "section": "Brainstorming ideas and outlining"},
    {"task_type": "Independent Essay", "section": "Crafting the Introduction and Thesis Statement"},
    {"task_type": "Independent Essay", "section": "Developing the First Body Paragraph (Topic Sentence)"},
    {"task_type": "Independent Essay", "section": "Developing the First Body Paragraph (Evidence/Examples)"},
    {"task_type": "Independent Essay", "section": "Developing the First Body Paragraph (Explanation/Link)"},
    {"task_type": "Independent Essay", "section": "Writing a Transition to the Second Body Paragraph"},
    {"task_type": "Independent Essay", "section": "Developing the Second Body Paragraph (Topic Sentence)"},
    {"task_type": "Independent Essay", "section": "Crafting the Conclusion"},
    
    {"task_type": "Integrated Essay", "section": "Summarizing the main point of the Reading Passage"},
    {"task_type": "Integrated Essay", "section": "Identifying the Lecturer's main counter-argument to the Reading"},
    {"task_type": "Integrated Essay", "section": "Paraphrasing a specific detail from the Reading"},
    {"task_type": "Integrated Essay", "section": "Paraphrasing a specific detail from the Listening"},
    {"task_type": "Integrated Essay", "section": "Synthesizing a point from Reading with a related point from Listening (Agreement)"},
    {"task_type": "Integrated Essay", "section": "Synthesizing a point from Reading with a contrasting point from Listening (Disagreement/Challenge)"},
    {"task_type": "Integrated Essay", "section": "Structuring the introduction for the Integrated Task"},
    {"task_type": "Integrated Essay", "section": "Writing a body paragraph that contrasts Reading and Listening points"},
]

# What is the AI's current pedagogical focus during this co-writing interaction? (Optional)
COWRITING_LO_FOCUS_EXAMPLES = [
    None, # General co-writing assistance
    "Ensuring a clear and arguable thesis statement.",
    "Developing well-supported body paragraphs with topic sentences.",
    "Using precise and academic vocabulary.",
    "Improving sentence variety and structure.",
    "Maintaining coherence and using effective transitions.",
    "Correctly paraphrasing source material (for Integrated tasks).",
    "Accurately synthesizing information from reading and listening (for Integrated tasks).",
    "Avoiding common grammatical errors (e.g., subject-verb agreement, tense consistency)."
]

# Examples of short text chunks the student might have just typed.
STUDENT_WRITTEN_INPUT_CHUNKS = [
    # Good starts
    "In my opinion, universities should focus more on practical skills.",
    "The reading passage explains that the new campus policy is intended to reduce traffic congestion.",
    "To begin with, one significant advantage of remote work is the increased flexibility it offers employees.",
    # Common errors/weaknesses
    "I think technology is very good.", # Vague
    "He go to school everyday make him smart.", # S-V agreement, run-on
    "The lecture talks about the problems. For example, pollution.", # Weak connection, needs more development
    "Reading say one thing, listening say other thing.", # Too informal, lacks detail for Integrated
    "Its important for students to study hard so they can get good job.", # its/it's, vague "good job"
    "Many peoples believe that social media have a bad affect on society.", # peoples, have/has, affect/effect
    "Because the internet provides vast amounts of information.", # Sentence fragment
    "The author of the article makes a point that recycling is beneficial for the environment this is true.", # Run-on, punctuation
    "The professor she say that the theory is not correct an example is...", # Pronoun redundancy, awkward phrasing
]

# Examples of what the student might say aloud while writing (their articulated thoughts).
STUDENT_ARTICULATED_THOUGHTS = [
    None, # Student is quiet, AI reacts only to text
    "Okay, so now I need to give my first reason for the thesis.",
    "Hmm, is 'tremendous' the right word here, or is it too strong?",
    "I'm trying to connect this example back to my main point for this paragraph.",
    "I'm not sure how to phrase the lecturer's disagreement with this reading point.",
    "I should probably add a transition word here to link these two sentences.",
    "I want to make sure this sounds academic enough.",
    "I'm stuck on how to start this conclusion.",
    "Does this sentence clearly support my topic sentence?",
    "I think I'll use a complex sentence here to show variety."
]

# Placeholder for consistency, though not directly used in the co-writing prompt in the same way as the pedagogical data prompt
# We use ESTIMATED_OVERALL_ENGLISH_COMFORT_LEVEL and STUDENT_AFFECTIVE_STATE_PROXY instead.
QUESTION_ONE_ANSWERS_CTX = QUESTION_ONE_ANSWERS 
QUESTION_TWO_ANSWERS_CTX = QUESTION_TWO_ANSWERS
QUESTION_THREE_ANSWERS_CTX = QUESTION_THREE_ANSWERS

# Example: You might want to pre-generate a few scenarios for each LO to ensure coverage
# For a full run, you'd iterate through all combinations as in your main_cowriting.py
# This is just to show the data structure.
# In main_cowriting.py, you will create these lists and iterate through them.