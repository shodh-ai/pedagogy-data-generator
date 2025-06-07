"""
Data collections for the language correction generator.
Contains topics, proficiency levels, and types of mistakes.
"""

# Writing/speaking topics covering various domains
TOPICS = [
    # Academic topics
    "The importance of higher education in today's society",
    "Should students be required to learn a foreign language?",
    "The impact of technology on modern education",
    "The benefits and drawbacks of online learning",
    "Are standardized tests an effective measure of student ability?",
    
    # Social issues
    "The influence of social media on interpersonal relationships",
    "Environmental conservation: individual responsibility or government policy?",
    "The challenges of cultural integration in multicultural societies",
    "The role of public transportation in reducing carbon emissions",
    "Should healthcare be free for all citizens?",
    
    # Personal/reflective topics
    "Describe a significant challenge you've overcome in your life",
    "The role of travel in personal development",
    "How has technology changed the way we communicate?",
    "The importance of maintaining traditions in modern society",
    "What qualities make someone a good leader?",
    
    # Professional topics
    "The future of remote work after the pandemic",
    "The importance of work-life balance",
    "How technology is changing the job market",
    "The value of diversity in the workplace",
    "Ethical considerations in business decision-making"
]

# Proficiency levels corresponding to CEFR standards
PROFICIENCY_LEVELS = [
    "A1 - Beginner",
    "A2 - Elementary", 
    "B1 - Intermediate",
    "B2 - Upper Intermediate",
    "C1 - Advanced",
    "C2 - Proficiency"
]

# Types of language mistakes organized by category
GRAMMAR_MISTAKES = [
    "Subject-verb agreement",
    "Verb tense inconsistency",
    "Article usage (a/an/the)",
    "Preposition errors",
    "Plural/singular noun confusion",
    "Conditional clause structure",
    "Modal verb usage",
    "Passive voice construction",
    "Relative clause formation",
    "Gerund/infinitive confusion"
]

VOCABULARY_MISTAKES = [
    "Word choice errors",
    "Collocation issues",
    "False friends (words similar to native language)",
    "Register mismatch (formal vs. informal)",
    "Idiom misuse",
    "Phrasal verb errors",
    "Academic vocabulary misuse",
    "Redundancy",
    "Vague language",
    "Connotation confusion"
]

STRUCTURE_MISTAKES = [
    "Paragraph organization",
    "Topic sentence missing/unclear",
    "Coherence issues between sentences",
    "Lack of transitions",
    "Redundant information",
    "Insufficient examples/evidence",
    "Introduction/conclusion problems",
    "Argument development",
    "Thesis statement issues",
    "Logical fallacies"
]

SPEAKING_SPECIFIC_MISTAKES = [
    "Pronunciation errors",
    "Intonation issues",
    "Stress patterns",
    "Rhythm problems",
    "Hesitation/fillers (um, ah)",
    "Incomplete sentences",
    "False starts",
    "Run-on sentences in speech",
    "Word stress errors",
    "Connected speech issues"
]

WRITING_SPECIFIC_MISTAKES = [
    "Punctuation errors",
    "Capitalization issues",
    "Formatting problems",
    "Run-on sentences",
    "Sentence fragments",
    "Paragraph breaks",
    "Citation/reference errors",
    "Spelling mistakes",
    "Wordiness",
    "Academic style issues"
]

# Task types
TASK_TYPES = ["speaking", "writing"]

# Combine mistake types for easy access
ALL_MISTAKE_TYPES = GRAMMAR_MISTAKES + VOCABULARY_MISTAKES + STRUCTURE_MISTAKES + SPEAKING_SPECIFIC_MISTAKES + WRITING_SPECIFIC_MISTAKES
