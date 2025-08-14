# Flags
# Copy this section to flags.py to override defaults

START, NUM_LECS = 0, 100
MODEL = "gpt-4.1-mini"

GET_TRANSCRIPTS = True
GET_KEY_POINTS = True
GET_Q_AND_A = True

TRY_REUSE_NOTES = False
IS_BOOK = False

# End Flags

try:
    from flags import *
except ImportError:
    pass

def remove_unwanted_lines(text):

    # If chatgpt starts with a conversational message, Remove first and last line
    if not text.strip().startswith("#"):
        lines = text.split('\n')
        if len(lines) > 2:
            lines = lines[1:-1]
        text = '\n'.join(lines)

    # Remove lines that contain '# Study Note'
    lines = text.split('\n')
    lines = [line for line in lines if '# Study Note' not in line]
    text = '\n'.join(lines)

    return text

def clean(text):
    text = remove_unwanted_lines(text)
    if text.startswith('#'):
        text = '#' + text
    if text.startswith('## '):
        text = '#' + text
    return text.replace('\n---\n', '\n').replace('\n#', '\n##').replace('\n## ', '\n### ').strip()

system_prompt = """
You are ChatGPT, an advanced language model developed by OpenAI, based on the GPT-4 architecture. You are helpful, honest, and harmless. Your knowledge is current up to **June 2024**, and today's date is **July 6, 2025**.

**Your objectives are:**

- **Help the user effectively.** Provide useful, accurate, and relevant information. Prioritize clarity, precision, and completeness in your answers.
- **Be honest about your limitations.** If you don’t know something or your knowledge is outdated, say so clearly.
- **Follow user instructions.** Adjust your tone, style, and format to match what the user asks, unless it conflicts with  truthfulness.
- **Be natural and professional.** Write in a warm, respectful, and articulate tone. Avoid robotic or overly formal language unless requested.
- **Think step-by-step.** When solving problems, especially involving reasoning, calculations, or coding, break them down into logical steps.
- **Ground your answers.** When possible, cite sources, show reasoning, or explain how you arrived at your conclusions.
- **Avoid hallucination.** Don't make up facts. If uncertain, say so, or provide an informed guess clearly labeled as such.

**You are capable of:**

* Answering complex questions
* Writing and editing code
* Helping with writing, research, and analysis
* Supporting creative and technical tasks
* Parsing and generating images when requested
* Adapting tone and personality for different user needs

Always maintain a professional, clear, and helpful demeanor. You are here to assist, not to judge, speculate excessively, or take strong stances unless well-supported.
"""

guided_system_prompt = """
Avoid artificial or bloated language. Your tone should be natural, not grandiose.

Follow these key principles:

1. Use normal, unpretentious language.
- Do not use flowery or inflated phrasing.
- Avoid vague or empty adjectives like “innovative,” “captivating,” or “groundbreaking.”
- Write like a thoughtful person explaining something clearly, not a marketing bot.

2. Focus on substance.
- Every sentence must add value or information.
- Avoid filler and verbosity.
- Do not generate multiple paragraphs when one would do.

3. Stay accurate and honest.
- Never guess or invent facts. If uncertain, say so plainly.
- When needed, support your points with examples, but only if they are clear and helpful.
"""

user_prompt_1 = """
Create a detailed, introductory understandable study note based on the following lecture content, make sure it's well organized, ADD CONTENTT AND DETAIL, and is clear and detailed. Explain key concepts clearly and in words. Do not leave anything out that's in the lecture content. Structured liek a note, not just a list of points. Each section must have a clear, detailed IN WORD INTRODUCTION. Don't use overly academic tone.

Be VERY DETAILED in each of your explanations. Prefer clear, in-word explanations over brevity. Use emojis in main headings for clarity. Number main headings like ## 1. [Emoji] Heading. Use between 3 - 10 main headings as needed. Don't use too many sub headings.

lecture content:
"""

user_prompt_2 = """
Hence, create a complete comprehensive lecture that is well structured and clearly introduces and explains this whole topic. Do not include headings.

Your task is to narrate the lecture in natural language spoken paragraph form. Don't prefix of suffix it with anything, just the lecture. Make sure to maintain a relatable, intuitive, and introductory tone that encourages engagement and curiosity. Don't use overly flowery language. Don't include raw formulas or equations.
"""

user_prompt_3 = """
Hence, write 20 multiple choice questions that comprehensively cover this topic (each question having ONE OR MORE CORRECT answer). Don't mark answers. Make sure to cover all the key concepts and ideas in the lecture content. Each question should be clear and concise. Include TRICKY and DIFFICULT questions. Make sure the answer isn't obvious, and REQUIRE A CLEAR UNDERSTANDING of the content. No need to say like "according to the lecture", as it is implied. Use the following format.

### X. [Question]
A)
B)
C) 
D)
"""

user_prompt_4 = """
For each question, clearly state the correct choices, and clearly state why each choice is correct or incorrect. Make sure to carefully consider each statement, its relation to the question, and the context of the lecture. Keep explanations brief but specific. Use the following format exactly.

### X. [Question]
A) ✓/✗ [Short explanation]  
B) ✓/✗ [Short explanation]  
C) ✓/✗ [Short explanation]  
D) ✓/✗ [Short explanation]

**Correct:** P,Q
"""

user_prompt_5 = """
State all the KEY TESTABLE FACTS here, ignore all filler and common knowledge You may use emojis for clarity. Use this format for key facts.

### 1. [Emoji] [Fact-Topic]
- [fact1]
- [fact2]

### 2. [Emoji] [Fact-Topic]
- [fact1]
- [fact2]
- [fact3]

"""

if IS_BOOK:
    user_prompt_1 = user_prompt_1.replace("lecture", "book")
    # user_prompt_2 = user_prompt_2.replace("lecture", "book")
    user_prompt_3 = user_prompt_3.replace("lecture", "book")
    user_prompt_4 = user_prompt_4.replace("lecture", "book")
    user_prompt_5 = user_prompt_5.replace("lecture", "book")

model_costs = {
    "gpt-4.1":       [2.00, 0.50, 8.00],
    "gpt-4.1-mini":  [0.40, 0.10, 1.60],
    "gpt-4.1-nano":  [0.10, 0.03, 0.40],
    "gpt-4o":        [2.50, 1.25, 10.00],
    "gpt-4o-mini":   [0.15, 0.08, 0.60],
    "gpt-o4-mini":   [1.10, 0.28, 4.40],
}

def model_usage(usage, model):
    token_fields = ['prompt_tokens', 'cached_tokens', 'completion_tokens']

    # Extract token usage from nested and direct attributes
    flat_usage = {key: val for attr in usage.__dict__.values() if hasattr(attr, '__dict__')
        for key, val in attr.__dict__.items() if key in token_fields and val}
    flat_usage.update({key: val for key, val in usage.__dict__.items()
        if key in token_fields and not hasattr(val, '__dict__') and val})

    # Reorder according to token_fields
    token_usage = {key: flat_usage.get(key, 0) for key in token_fields}

    cost = 0
    if model in model_costs:
        prompt = token_usage['prompt_tokens']
        cached = token_usage['cached_tokens']
        completion = token_usage['completion_tokens']

        pricing = model_costs[model]
        costs = [
            (prompt - cached) * pricing[0],
            cached * pricing[1],
            completion * pricing[2],
        ]

        cost = sum(costs)/10**6
        print(f"- Cost: {cost:.4f}", end="  ")

    print(f"Usage: {token_usage}")

    return cost


import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_sections(md_text):
    sections = {}

    def unclean(text):
        if text.startswith("##"):
            text = text[1:]
        return text.replace('\n##', '\n#')

    def extract(key, pre, suf=r"(\n\n<br>|$)", apply_unclean=True):
        match = re.search(pre + r"(.*?)" + suf, md_text, re.DOTALL)
        if match:
            content = match.group(1).replace('<br>','').strip()
            sections[key] = unclean(content) if apply_unclean else content

    # Explicitly set the suffix to the start of the next section (or fallback) if needed.
    # extract("key_points", "### Key Points\n\n", r"(## Study Notes\n\n|\n\n<br>|$)")
    # Note: This may fail if the next section is missing.
    extract("title", "## ", r"\n\n", apply_unclean=False)
    extract("questions", "## Questions\n\n")
    extract("answers", "## Answers\n\n")
    extract("key_points", "### Key Points\n\n")
    extract("study_notes", "## Study Notes\n\n")

    return sections

def process_file(filepath):
    filename = os.path.basename(filepath)
    match = re.match(r"(\d+)", filename)
    if not match:
        return None

    id_num = int(match.group(1))

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            md_text = f.read()
        return id_num, extract_sections(md_text)
    except Exception:
        return None

def load_md_to_dict(folder="outputs"):
    if not os.path.exists(folder):
        return {}

    filepaths = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".md")]

    if not filepaths:
        return {}

    result_dict = {}

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, path) for path in filepaths]

        for future in as_completed(futures):
            result = future.result()
            if result:
                id_num, sections = result
                result_dict[id_num] = sections

    return result_dict
