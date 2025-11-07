import pyperclip
import os

def copy_to_clipboard(code: str) -> str:
    """Copies the generated code to the clipboard."""
    pyperclip.copy(code)
    return "✅ Code copied to clipboard!"

def save_to_file(code: str, language: str) -> str:
    """Saves the generated code to a file with the correct extension."""
    extensions = {"python": "py", "javascript": "js", "html": "html", "java": "java", "c++": "cpp", "go": "go"}
    file_name = f"generated_code.{extensions.get(language, 'txt')}"

    with open(file_name, "w") as file:
        file.write(code)

    return f"✅ Code saved as {file_name}"
