#!/usr/bin/env python3

import asyncio
import os
import tempfile
from datetime import datetime
from io import BytesIO

import gradio as gr
from docx import Document
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

# This now assumes you have a 'src' directory with a 'workflow.py' file
# containing the real StartupWorkflow class.
from src.workflow import StartupWorkflow

# Load environment variables from .env file
load_dotenv()

class ReportGenerator:
    """Handles the generation of all report formats (text, PDF, Word)."""

    def __init__(self, result):
        self.result = result
        self.startup_idea = result.startup_idea
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_all_reports(self):
        """Generate all report formats and return them as a dictionary."""
        report_text = self._generate_text_report()
        return {
            "text": report_text,
            "pdf": self._generate_pdf_report(report_text),
            "word": self._generate_word_report(report_text),
        }

    def _generate_text_report(self):
        """Generate a formatted plain text report."""
        report_lines = [
            f"STARTUP IDEA ANALYSIS REPORT",
            f"Generated: {self.timestamp}",
            "=" * 80,
            f"💡 STARTUP IDEA: {self.startup_idea.name}",
            f"Description: {self.startup_idea.description or 'N/A'}",
            "\n--- MARKET ANALYSIS ---\n",
            self._format_market_analysis_text(),
            "\n--- COMPETITOR ANALYSIS ---\n",
            self._format_competitors_text(),
            "\n--- VIABILITY ASSESSMENT ---\n",
            self._format_viability_assessment_text(),
            "\n--- FINAL RECOMMENDATIONS ---\n",
            self.result.final_analysis or "N/A",
            "\n--- KEY TAKEAWAYS ---\n",
            "\n".join(f"- {rec}" for rec in self.result.recommendations) if self.result.recommendations else "N/A",
            "\n" + "=" * 80,
        ]
        return "\n".join(report_lines)

    def _format_market_analysis_text(self):
        market = self.startup_idea.market_analysis
        if not market:
            return "No market analysis available."
        return (
            f"Market Size: {market.market_size or 'Unknown'}\n"
            f"Growth Rate: {market.growth_rate or 'Unknown'}\n"
            f"Target Audience: {', '.join(market.target_audience) if market.target_audience else 'N/A'}\n"
            f"Market Trends: {', '.join(market.market_trends) if market.market_trends else 'N/A'}\n"
            f"Barriers to Entry: {', '.join(market.barriers_to_entry) if market.barriers_to_entry else 'N/A'}"
        )

    def _format_competitors_text(self):
        if not self.startup_idea.competitors:
            return "No competitors found."
        
        competitor_details = []
        for i, comp in enumerate(self.startup_idea.competitors[:5], 1):
            details = (
                f"{i}. {comp.name}\n"
                f"   - Website: {comp.website}\n"
                f"   - Business Model: {comp.business_model or 'Unknown'}\n"
                f"   - Key Features: {', '.join(comp.key_features[:3]) if comp.key_features else 'N/A'}"
            )
            competitor_details.append(details)
        return "\n".join(competitor_details)

    def _format_viability_assessment_text(self):
        analysis = self.startup_idea.startup_analysis
        if not analysis:
            return "No viability assessment available."
        return (
            f"Viability Score: {analysis.viability_score or 'N/A'}/10\n"
            f"Market Opportunity: {analysis.market_opportunity or 'N/A'}\n"
            f"Competitive Advantages: {', '.join(analysis.competitive_advantage) if analysis.competitive_advantage else 'N/A'}\n"
            f"Potential Challenges: {', '.join(analysis.potential_challenges) if analysis.potential_challenges else 'N/A'}"
        )

    def _generate_pdf_report(self, report_text):
        """Generate a PDF report from the text content."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(line.replace(' ', '&nbsp;'), styles['Normal']) for line in report_text.split('\n')]
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _generate_word_report(self, report_text):
        """Generate a Word document from the text content."""
        document = Document()
        for paragraph in report_text.split('\n'):
            document.add_paragraph(paragraph)
        buffer = BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer

def validate_environment():
    """Validate that all required environment variables are set."""
    required = ['GOOGLE_API_KEY', 'SERP_API_KEY']
    missing = [var for var in required if not os.getenv(var)]
    return missing

def format_html_section(title, content, icon=""):
    """Helper function to create a styled HTML section with a dark theme."""
    return f"""
    <div style="background-color: #2D3748; color: #E2E8F0; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #4A5568;">
        <h4 style="color: #FFFFFF;">{icon} {title}</h4>
        {content}
    </div>
    """

def format_viability_score(score):
    """Format the viability score with color coding for a dark theme."""
    if score >= 7:
        style = "background-color: #2F855A; color: #F0FFF4; border-color: #38A169;"
    elif score >= 4:
        style = "background-color: #B7791F; color: #FFFAF0; border-color: #D69E2E;"
    else:
        style = "background-color: #C53030; color: #FFF5F5; border-color: #E53E3E;"
    
    return f"""
    <div style="{style} font-size: 2rem; font-weight: bold; text-align: center; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; border: 2px solid;">
        Viability Score: {score}/10
    </div>
    """

def format_results_to_html(result):
    """Convert the analysis result into a single HTML string for display."""
    startup = result.startup_idea
    
    # Main Idea Section
    idea_html = f"""
    <div style="background-color: #2C5282; color: #EBF8FF; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 5px solid #63B3ED;">
        <h3 style="color: #FFFFFF;">💡 Startup Idea: {startup.name}</h3>
        <p>{startup.description or 'N/A'}</p>
    </div>
    """

    # Market Analysis Section
    market = startup.market_analysis
    market_content = "<p>No market analysis available.</p>"
    if market:
        market_content = f"""
        <p><strong>Market Size:</strong> {market.market_size or 'Unknown'}</p>
        <p><strong>Growth Rate:</strong> {market.growth_rate or 'Unknown'}</p>
        <h5 style="color: #FFFFFF;">🎯 Target Audience</h5>
        <ul style="list-style-type: square;">{''.join(f'<li>{a}</li>' for a in market.target_audience)}</ul>
        """
    market_html = format_html_section("Market Analysis", market_content, "📊")
    
    # Competitors Section
    competitors_content = "<p>No competitors found.</p>"
    if startup.competitors:
        competitors_content = "".join(
            f"""
            <div style="border-bottom: 1px solid #4A5568; padding-bottom: 10px; margin-bottom: 10px;">
                <strong>{i}. {comp.name}</strong>
                <p>Website: <a href="{comp.website}" target="_blank" style="color: #63B3ED;">{comp.website}</a></p>
                <p>Key Features: {', '.join(comp.key_features[:3]) if comp.key_features else 'N/A'}</p>
            </div>
            """ for i, comp in enumerate(startup.competitors[:5], 1)
        )
    competitors_html = format_html_section("Competitor Analysis", competitors_content, "🏢")

    # Viability Assessment Section
    analysis = startup.startup_analysis
    viability_content = "<p>No viability assessment available.</p>"
    if analysis:
        viability_content = f"""
        {format_viability_score(analysis.viability_score or 0)}
        <p><strong>Market Opportunity:</strong> {analysis.market_opportunity or 'N/A'}</p>
        <p><strong>Competitive Advantages:</strong> {', '.join(analysis.competitive_advantage) if analysis.competitive_advantage else 'N/A'}</p>
        """
    viability_html = format_html_section("Viability Assessment", viability_content, "🎯")

    # Final Recommendations Section
    recommendations_html = format_html_section(
        "Final Recommendations & Key Takeaways",
        f"<p>{result.final_analysis.replace(chr(10), '<br>')}</p>"
        f"<ul style='list-style-type: square;'>{''.join(f'<li>{rec}</li>' for rec in result.recommendations)}</ul>" if result.recommendations else "",
        "📋"
    )

    return idea_html + market_html + competitors_html + viability_html + recommendations_html

async def analyze_startup_idea(startup_idea_str, progress=gr.Progress()):
    """Main async function to analyze startup idea and return formatted results."""
    if not startup_idea_str.strip():
        # Return updates for each output component to clear them
        no_input_error = "❌ Please enter a startup idea to analyze."
        return no_input_error, gr.update(value=None, visible=False), gr.update(value=None, visible=False), gr.update(value=None, visible=False)

    missing_vars = validate_environment()
    if missing_vars:
        error_msg = f"❌ Missing required environment variables: {', '.join(missing_vars)}. Please check your .env file."
        return error_msg, gr.update(value=None, visible=False), gr.update(value=None, visible=False), gr.update(value=None, visible=False)

    progress(0, desc="Starting analysis...")
    try:
        workflow = StartupWorkflow()
        progress(0.3, desc="Running market and competitor analysis...")
        result = await workflow.run(startup_idea_str.strip())

        if not result or not result.startup_idea:
            error_msg = "❌ Analysis failed. The workflow did not return a valid result. Please try again."
            return error_msg, gr.update(value=None, visible=False), gr.update(value=None, visible=False), gr.update(value=None, visible=False)

        progress(0.7, desc="Generating reports...")
        
        results_html = format_results_to_html(result)
        report_generator = ReportGenerator(result)
        reports = report_generator.generate_all_reports()

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as tmp:
            tmp.write(reports["text"])
            txt_path = tmp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(reports["pdf"].getvalue())
            pdf_path = tmp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(reports["word"].getvalue())
            word_path = tmp.name
        
        progress(1, desc="Done!")

        return (
            results_html,
            gr.update(value=txt_path, visible=True),
            gr.update(value=pdf_path, visible=True),
            gr.update(value=word_path, visible=True),
        )

    except Exception as e:
        error_msg = f"❌ An unexpected error occurred: {e}"
        return error_msg, gr.update(value=None, visible=False), gr.update(value=None, visible=False), gr.update(value=None, visible=False)

def create_interface():
    """Create and configure the Gradio interface."""
    with gr.Blocks(theme=gr.themes.Default(primary_hue="blue"), title="Startup Idea Analyzer") as demo:
        gr.Markdown("# 🚀 Startup Idea Analyzer")
        gr.Markdown("AI-powered market research and competitor analysis for your next big idea.")
        
        with gr.Row():
            with gr.Column(scale=2):
                startup_idea_input = gr.Textbox(
                    label="💡 Describe your startup idea:",
                    placeholder="e.g., A subscription box for eco-friendly pet toys",
                    lines=4,
                )
                analyze_btn = gr.Button("🚀 Analyze Idea", variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Configuration Status")
                missing_vars = validate_environment()
                if missing_vars:
                    gr.Markdown(f"❌ **Missing:** {', '.join(missing_vars)}")
                else:
                    gr.Markdown("✅ **Environment configured**")
                
                gr.Markdown("### ℹ️ About")
                gr.Markdown(
                    "This tool provides a comprehensive analysis of startup ideas, "
                    "covering market size, competition, and viability."
                )
        
        results_html = gr.HTML(label="📊 Analysis Results")
        
        with gr.Row():
            txt_download = gr.File(label="📥 Download .txt", visible=False)
            pdf_download = gr.File(label="📄 Download .pdf", visible=False)
            word_download = gr.File(label="📑 Download .docx", visible=False)

        analyze_btn.click(
            fn=analyze_startup_idea,
            inputs=[startup_idea_input],
            outputs=[results_html, txt_download, pdf_download, word_download],
        )
    
    return demo

if __name__ == "__main__":
    app = create_interface()
    app.launch(dark=True)
