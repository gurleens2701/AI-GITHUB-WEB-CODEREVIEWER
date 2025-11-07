
import openai

import os
from backend.services.openai_client import client
from backend.config.settings import settings




def generate_code(query, language):
    prompt = f"""
    Generate ONLY the executable {language} code for: {query}
    
    CRITICAL RULES:
    - Return ONLY code that can be directly executed
    - NO explanations before or after the code
    - NO notes, warnings, or suggestions
    - NO markdown code blocks (```)
    - NO "Please note" or similar phrases
    - Just pure, clean, executable code
    """

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": "You return ONLY executable code. Never add explanations, notes, or markdown formatting."},
            {"role": "user", "content": prompt}
        ],
        temperature=settings.temperature
    )
    code = response.choices[0].message.content.strip()

    # Remove markdown code blocks if present
    if "```" in code:
        # Find the actual code between markdown blocks
        lines = code.split('\n')
        code_lines = []
        inside_code_block = False
        
        for line in lines:
            if line.strip().startswith("```"):
                inside_code_block = not inside_code_block
                continue
            if inside_code_block or not any(phrase in line.lower() for phrase in [
                "please note", "note that", "this code", "you should", "for this code",
                "make sure", "remember", "important", "also", "additionally"
            ]):
                code_lines.append(line)
        
        code = '\n'.join(code_lines).strip()
    
    # Remove common explanatory endings
    explanatory_phrases = [
        "Please note",
        "Note that",
        "This code",
        "You should",
        "For this code to work",
        "Make sure",
        "Remember",
        "Important:",
        "Also,",
        "Additionally,"
    ]
    
    lines = code.split('\n')
    clean_lines = []
    
    for line in lines:
        # Stop adding lines if we hit explanatory text
        if any(phrase in line for phrase in explanatory_phrases):
            break
        clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()


def generate_unit_tests(code: str, language: str) -> str:
    """Generates unit tests for the provided code."""
    prompt = f"""
    Given the following {language} code:
    {code}
    Generate unit tests using the best testing framework for {language}.
    Ensure tests cover edge cases and include assertions.
    """

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[{"role": "system", "content": "You generate high-quality unit tests for developers."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def generate_documentation(code: str, language: str) -> str:
    """Generates documentation in the form of docstrings for classes and functions."""
    prompt = f"""
    Given the following {language} code:
    {code}
    Add detailed docstrings for all functions and classes. Ensure:
    - Parameters and return values are well-documented.
    - Docstrings follow standard conventions (e.g., Google style for Python).
    """

    response = client.chat.completions.create(
        model=settings.model_name,
        messages=[{"role": "system", "content": "You generate high-quality documentation for developers."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


    