import gradio as gr

def create_header():
    """Create the main header component."""
    return gr.HTML("""
    <div class="main-header">
        <h1>🚀 AI Code Generator</h1>
        <p>Generate high-quality code, unit tests, and documentation with AI</p>
        <div class="subtitle">
            ✨ Powered by LLM • 🧪 Unit Tests • 📚 Documentation 
        </div>
    </div>
    """)

def create_section_divider():
    """Create a section divider."""
    return gr.HTML('<div class="section-divider"></div>')

def clear_inputs():
    """Clear all inputs and outputs."""
    return "", "python", "", "", ""
