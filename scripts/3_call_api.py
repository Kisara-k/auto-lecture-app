import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

from config import system_prompt, guided_system_prompt, user_prompt_1, user_prompt_2, user_prompt_3, user_prompt_4, user_prompt_5, clean, model_usage, load_md_to_dict
from config import MODEL, START, NUM_LECS, GET_TRANSCRIPTS, GET_KEY_POINTS, GET_Q_AND_A, TRY_REUSE_NOTES

load_dotenv()
openai_key = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=openai_key)

total_cost = 0.0
cost_lock = threading.Lock()

def generate(messages, model=MODEL, max_retries=120):
    retries = 0
    while retries <= max_retries:
        try:
            start = time.time()
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,  # Adjust for more creative or deterministic output
                max_tokens=10000,  # Increase this if responses are getting cut off
                top_p=0.3,
                frequency_penalty=0,
                presence_penalty=0
            )

            elapsed = time.time() - start
            print(f"Completion took {elapsed:.2f} seconds")
            
            try:
                cost = model_usage(completion.usage, model)
            except Exception as e:
                print(f"Error getting model usage: {e}")
                cost = 0

            with cost_lock:
                global total_cost
                total_cost += cost

            return completion.choices[0].message.content, completion

        except RateLimitError as e:
            retries += 1
            if retries <= max_retries:
                print(f"Rate limit hit - waiting {10}s (retry {retries}/{max_retries})")
                time.sleep(10)
            else:
                raise

import json

with open('Lectures.json', 'r', encoding='utf-8') as f:
    lectures = json.load(f)

lectures_sorted = sorted(lectures, key=lambda x: x['index'])
start_index = lectures_sorted[0]['index']
for offset, lecture in enumerate(lectures_sorted):
    lecture['index'] = start_index + offset

os.makedirs("outputs", exist_ok=True)

def load_data(name):
    data_path = os.path.join("outputs", f"{name}.json")
    data_dict = {}

    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            data_dict = {item["index"]: {k: item[k] for k in ["title", "content"]}
                for item in existing_data}

    return data_dict, data_path, threading.Lock()

transcripts, transcripts_path, transcripts_lock = load_data("Transcripts")

history = load_md_to_dict()

def process_lecture(lecture):
    id = lecture['index']
    title = lecture['title']
    content = lecture['content']

    if not (START <= id < START + NUM_LECS):
        return

    print(f"Processing {id}: {title}")

    lec_prompt_1 = user_prompt_1 + title + "\n\n" + content

    # Step 1
    
    text_1 = None
    if TRY_REUSE_NOTES:
        text_1 = history.get(id, {}).get("study_notes")
    
    if text_1 is None:
        text_1, _ = generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": lec_prompt_1}
            ], model='gpt-4.1-mini')

    # Step 2

    results = {}
    results_lock = threading.Lock()

    def add_to_results(key, history_key):
        item = history.get(id, {}).get(history_key)
        if item is not None:
            with results_lock:
                results[key] = item

    def step_2a():

        if GET_TRANSCRIPTS:
        
            text_2, _ = generate([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": lec_prompt_1},
                {"role": "assistant", "content": text_1},
                {"role": "user", "content": user_prompt_2  + '\n\n' + guided_system_prompt},])

            with transcripts_lock:
                transcripts[id] = {"title": title, "content": text_2}

    def step_2b():
        
        if GET_Q_AND_A:
        
            text_3, _ = generate([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": lec_prompt_1},
                {"role": "assistant", "content": text_1},
                {"role": "user", "content": user_prompt_3},])
            
            results["text_3"] = text_3
            
            text_4, _ = generate([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": lec_prompt_1},
                {"role": "assistant", "content": text_1},
                {"role": "user", "content": user_prompt_3},
                {"role": "assistant", "content": text_3},
                {"role": "user", "content": user_prompt_4},])

            results["text_4"] = text_4
        
        else:
        
            add_to_results("text_3", "questions")
            add_to_results("text_4", "answers")
    
    def step_2c():
        
        if GET_KEY_POINTS:
        
            text_5, _ = generate([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": lec_prompt_1},
                {"role": "assistant", "content": text_1},
                {"role": "user", "content": user_prompt_5},
                ], model='gpt-4.1-mini')
            
            results["text_5"] = text_5
        
        else:

            add_to_results("text_5", "key_points")

    threads = [
        threading.Thread(target=step_2a),
        threading.Thread(target=step_2b),
        threading.Thread(target=step_2c),
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    filepath = os.path.join("outputs", f"{id:02d} {re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', title)}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        def clean_title(title):
            return re.sub(r'^0*(\d+)\s+', lambda m: (m.group(1) if m.group(1) != "0" else "0") + ' ', title, count=1)
        SEP = "\n\n\n\n<br>\n\n"
        f.write("## " + clean_title(title) + "\n\n")
        f.write("[Key Points](#key-points)\n\n")
        f.write("[Study Notes](#study-notes)\n\n")
        # f.write("[Questions](#questions)\n\n")
        if "text_3" in results:
            f.write("## " + "Questions" + "\n\n")
            f.write(clean(results["text_3"]))
        if "text_4" in results:
            f.write(SEP + "## " + "Answers" + "\n\n")
            f.write(clean(results["text_4"]))
        if "text_5" in results:
            f.write(SEP + "## " + "Key Points" + "\n\n")
            f.write(clean(results["text_5"]))
        f.write(SEP + "## " + "Study Notes" + "\n\n")
        f.write(clean(text_1))
    
    print(f"Saved {id}: {title}")


with ThreadPoolExecutor() as executor:
    executor.map(process_lecture, lectures)

# Save Output JSONs

def save_data(data_dict, file_path):
    if not data_dict:
        return
    data_list = [
        {"index": id, "title": data["title"], "content": data["content"]}
        for id, data in sorted(data_dict.items())
    ]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)

save_data(transcripts, transcripts_path)

print("\nLecture Processing Complete'")
print(f"Total API Cost: {total_cost:.4f}")
