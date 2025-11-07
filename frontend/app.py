import gradio as gr
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.components.ui_components import create_header, create_section_divider, clear_inputs

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def generate_code(query, language):
    """Generates code based on user input and language preference."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/generate-code",
            json={"query": query, "language": language}
        )
        response.raise_for_status()
        return response.json()["code"]
    except Exception as e:
        return f"Error: {str(e)}"

def generate_unit_tests(code, language):
    """Generates unit tests for the provided code."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/generate-tests",
            json={"code": code, "language": language}
        )
        response.raise_for_status()
        return response.json()["tests"]
    except Exception as e:
        return f"Error: {str(e)}"

def generate_documentation(code, language):
    """Generates documentation in the form of docstrings for classes and functions."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/generate-documentation",
            json={"code": code, "language": language}
        )
        response.raise_for_status()
        return response.json()["documentation"]
    except Exception as e:
        return f"Error: {str(e)}"

def copy_to_clipboard(code):
    """Copies the generated code to the clipboard."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/copy-to-clipboard",
            json={"code": code}
        )
        response.raise_for_status()
        return response.json()["message"]
    except Exception as e:
        return f"Error: {str(e)}"

def save_to_file(code, language):
    """Saves the generated code to a file with the correct extension."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/save-to-file",
            json={"code": code, "language": language}
        )
        response.raise_for_status()
        return response.json()["message"]
    except Exception as e:
        return f"Error: {str(e)}"

# Load custom CSS
def load_custom_css():
    """Load custom CSS from file."""
    try:
        with open("frontend/static/styles.css", "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# Create the enhanced Gradio interface
with gr.Blocks(
    css=load_custom_css(),
    title="🚀 Advanced AI Code Generator"
) as ui:
    
    # Spectacular header
    create_header()

    # Input section with enhanced layout
    with gr.Row():
        with gr.Column(scale=2):
            query = gr.Textbox(
                label="💭 Enter Code Requirements", 
                placeholder="Example: Create a REST API in Python with user authentication and JWT tokens...",
                lines=4
            )
        
        with gr.Column(scale=1):
            language = gr.Dropdown(
                ["python", "javascript", "java", "html", "c++", "go", "typescript", "php", "ruby", "swift"], 
                label="🔧 Select Programming Language", 
                value="python"
            )

    # Action buttons with enhanced styling
    create_section_divider()
    
    with gr.Row():
        generate_button = gr.Button("🚀 Generate Code", variant="primary", size="lg")
        test_button = gr.Button("🧪 Generate Unit Tests", variant="secondary")
        doc_button = gr.Button("📚 Generate Documentation", variant="secondary")
    
    with gr.Row():
        copy_button = gr.Button("📋 Copy Code", variant="secondary")
        save_button = gr.Button("💾 Save Code", variant="secondary")
        clear_button = gr.Button("🗑️ Clear All", variant="stop")

    # Output sections with better organization
    create_section_divider()
    
    gr.Markdown("### 📄 Generated Code")
    output = gr.Code(
        label="Generated Code", 
        language="python",
        lines=18
    )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🧪 Unit Tests")
            unit_test_output = gr.Code(
                label="Generated Unit Tests", 
                language="python",
                lines=15
            )
        
        with gr.Column():
            gr.Markdown("### 📚 Documentation")
            doc_output = gr.Code(
                label="Generated Documentation", 
                language="python",
                lines=15
            )
    
    create_section_divider()
    
    status = gr.Textbox(
        label="📊 Status", 
        interactive=False,
        lines=2
    )

    # Event handlers - preserving all original functionality
    generate_button.click(generate_code, inputs=[query, language], outputs=output)
    test_button.click(generate_unit_tests, inputs=[output, language], outputs=unit_test_output)
    doc_button.click(generate_documentation, inputs=[output, language], outputs=doc_output)
    copy_button.click(copy_to_clipboard, inputs=[output], outputs=status)
    save_button.click(save_to_file, inputs=[output, language], outputs=status)
    clear_button.click(clear_inputs, inputs=[], outputs=[query, language, output, unit_test_output, doc_output])

# Launch with enhanced settings
if __name__ == "__main__":
    ui.launch(
        server_name="0.0.0.0",
        server_port=7819,
        share=False,
        show_error=True,
        inbrowser=True
    )
