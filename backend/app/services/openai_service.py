import os
import time
import asyncio
from typing import Dict, List, Any, Optional
from openai import OpenAI, RateLimitError
from fastapi import HTTPException

from ..config import (
    config, system_prompt, guided_system_prompt, user_prompt_1, user_prompt_2, 
    user_prompt_3, user_prompt_4, user_prompt_5, clean, model_usage
)
from ..utils.temp_utils import save_temp_markdown

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.total_cost = 0.0

    async def generate(self, messages: List[Dict[str, str]], model: str = None, max_retries: int = 120) -> tuple[str, float]:
        """Generate text using OpenAI API with retry logic"""
        if model is None:
            model = config.MODEL
            
        retries = 0
        while retries <= max_retries:
            try:
                start = time.time()
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=10000,
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

                self.total_cost += cost
                return completion.choices[0].message.content, cost

            except RateLimitError as e:
                retries += 1
                if retries <= max_retries:
                    print(f"Rate limit hit - waiting 10s (retry {retries}/{max_retries})")
                    await asyncio.sleep(10)
                else:
                    raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    async def process_lecture(self, lecture: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single lecture and generate study materials"""
        lecture_id = lecture['index']
        title = lecture['title']
        content = lecture['content']

        print(f"Processing {lecture_id}: {title}")

        lec_prompt_1 = user_prompt_1 + title + "\n\n" + content

        # Step 1: Generate study notes
        study_notes, cost1 = await self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": lec_prompt_1}
        ], model='gpt-4o-mini')

        results = {
            "index": lecture_id,
            "title": title,
            "study_notes": clean(study_notes),
            "cost": cost1
        }

        # Step 2: Generate additional content based on flags
        tasks = []

        if config.GET_TRANSCRIPTS:
            tasks.append(self._generate_transcript(lec_prompt_1, study_notes))

        if config.GET_Q_AND_A:
            tasks.append(self._generate_questions_and_answers(lec_prompt_1, study_notes))

        if config.GET_KEY_POINTS:
            tasks.append(self._generate_key_points(lec_prompt_1, study_notes))

        # Execute tasks concurrently
        if tasks:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(task_results):
                if isinstance(result, Exception):
                    print(f"Task {i} failed: {result}")
                    continue
                    
                if isinstance(result, dict):
                    results.update(result)

        # Generate markdown content and save to temp directory
        markdown_content = self._generate_markdown_content(results)
        filename = f"lecture_{lecture_id:02d}_{title.replace(' ', '_').replace('/', '_')}.md"
        markdown_path = save_temp_markdown(markdown_content, filename)
        print(f"Lecture {lecture_id} markdown saved to: {markdown_path}")
        
        # Add the markdown file path to results
        results["markdown_file"] = str(markdown_path)

        return results

    def _generate_markdown_content(self, results: Dict[str, Any]) -> str:
        """Generate markdown content from processed lecture results"""
        content = []
        
        # Title and header
        content.append(f"# Lecture {results['index']}: {results['title']}\n")
        
        # Study notes
        content.append("## Study Notes\n")
        content.append(f"{results['study_notes']}\n")
        
        # Add transcript if available
        if 'transcript' in results:
            content.append("## Lecture Transcript\n")
            content.append(f"{results['transcript']}\n")
        
        # Add key points if available
        if 'key_points' in results:
            content.append("## Key Points\n")
            content.append(f"{results['key_points']}\n")
        
        # Add Q&A if available
        if 'questions' in results and 'answers' in results:
            content.append("## Questions and Answers\n")
            content.append("### Questions\n")
            content.append(f"{results['questions']}\n")
            content.append("### Answers\n")
            content.append(f"{results['answers']}\n")
        
        # Add cost information
        total_cost = results.get('cost', 0)
        if 'transcript_cost' in results:
            total_cost += results['transcript_cost']
        if 'qa_cost' in results:
            total_cost += results['qa_cost']
        if 'key_points_cost' in results:
            total_cost += results['key_points_cost']
            
        content.append(f"\n---\n*Processing cost: ${total_cost:.4f}*\n")
        
        return "\n".join(content)

    async def _generate_transcript(self, lec_prompt_1: str, study_notes: str) -> Dict[str, Any]:
        """Generate lecture transcript"""
        transcript, cost = await self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": lec_prompt_1},
            {"role": "assistant", "content": study_notes},
            {"role": "user", "content": user_prompt_2 + '\n\n' + guided_system_prompt}
        ])
        
        return {
            "transcript": transcript,
            "transcript_cost": cost
        }

    async def _generate_questions_and_answers(self, lec_prompt_1: str, study_notes: str) -> Dict[str, Any]:
        """Generate questions and answers"""
        # Generate questions
        questions, cost1 = await self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": lec_prompt_1},
            {"role": "assistant", "content": study_notes},
            {"role": "user", "content": user_prompt_3}
        ])
        
        # Generate answers
        answers, cost2 = await self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": lec_prompt_1},
            {"role": "assistant", "content": study_notes},
            {"role": "user", "content": user_prompt_3},
            {"role": "assistant", "content": questions},
            {"role": "user", "content": user_prompt_4}
        ])

        return {
            "questions": clean(questions),
            "answers": clean(answers),
            "qa_cost": cost1 + cost2
        }

    async def _generate_key_points(self, lec_prompt_1: str, study_notes: str) -> Dict[str, Any]:
        """Generate key points"""
        key_points, cost = await self.generate([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": lec_prompt_1},
            {"role": "assistant", "content": study_notes},
            {"role": "user", "content": user_prompt_5}
        ], model='gpt-4o-mini')

        return {
            "key_points": clean(key_points),
            "key_points_cost": cost
        }

    async def process_multiple_lectures(self, lectures: List[Dict[str, Any]], 
                                      max_concurrent: int = 3) -> List[Dict[str, Any]]:
        """Process multiple lectures with concurrency control"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_semaphore(lecture):
            async with semaphore:
                return await self.process_lecture(lecture)
        
        # Filter lectures based on config
        filtered_lectures = []
        for lecture in lectures:
            lecture_id = lecture['index']
            if config.START <= lecture_id < config.START + config.NUM_LECS:
                filtered_lectures.append(lecture)
        
        if not filtered_lectures:
            return []

        results = await asyncio.gather(
            *[process_with_semaphore(lecture) for lecture in filtered_lectures],
            return_exceptions=True
        )

        # Filter out exceptions and return successful results
        successful_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Lecture processing failed: {result}")
                continue
            successful_results.append(result)

        return successful_results
