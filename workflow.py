"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    if not 1 <= data['max_attempts'] <= 4 or not 1 <= data['threshold'] <= 5:
        raise ValueError('Invalid optimization limits')
    candidate = await agent.ask('generate', 'Create a concise explanation.', data['task'], 'A ResultMessage with is_error=False indicates SDK completion; validate the answer separately.')
    scores = []
    for attempt in range(data['max_attempts']):
        grade = await agent.ask('evaluate_' + str(attempt), 'Score accuracy from 1 to 5 and give actionable feedback.', candidate, {'score': 5, 'feedback': 'Completion and answer validity are distinguished.'})
        if not 1 <= grade['score'] <= 5:
            raise ValueError('Evaluator score is outside the rubric')
        scores.append(grade)
        if grade['score'] >= data['threshold'] or attempt + 1 == data['max_attempts']:
            break
        candidate = await agent.ask('optimize_' + str(attempt), 'Improve this candidate using the evaluator feedback.', {'candidate': candidate, 'grade': grade}, 'Check ResultMessage.is_error, then independently validate the returned answer.')
    return {'candidate': candidate, 'grades': scores, 'accepted': scores[-1]['score'] >= data['threshold']}
