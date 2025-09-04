from flask import render_template, request, jsonify, redirect, url_for, session
from app import app
from scam_analyzer import analyze_scam_indicators
import logging
import markdown
import os

@app.route('/')
def index():
    """Landing page with prominent scam check button"""
    return render_template('index.html')

@app.route('/learn')
def learn():
    """Educational content about common scams"""
    try:
        # Read the markdown content
        content_path = os.path.join('content', 'top_10_scams.md')
        with open(content_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML with senior-friendly styling
        html_content = markdown.markdown(markdown_content, extensions=['extra'])
        
        # Add senior-friendly CSS classes to the HTML
        html_content = format_scam_content(html_content)
        
        return render_template('learn.html', scam_content=html_content)
        
    except Exception as e:
        logging.error(f"Error loading scam content: {str(e)}")
        return render_template('learn.html', 
                             scam_content="<p>Unable to load educational content. Please try again later.</p>")

def format_scam_content(html_content):
    """Add senior-friendly styling classes to the generated HTML"""
    # Add classes for better styling
    html_content = html_content.replace('<h1>', '<h1 class="display-4 fw-bold text-primary mb-4">')
    html_content = html_content.replace('<h2>', '<h2 class="h3 fw-bold text-dark mt-5 mb-3 border-bottom border-2 border-primary pb-2">')
    html_content = html_content.replace('<p><strong>Summary:</strong>', '<div class="alert alert-info"><p class="mb-0 fs-5"><strong>Summary:</strong>')
    html_content = html_content.replace('<p><strong>How it works:</strong>', '</div><div class="mt-3 mb-3"><h4 class="text-danger mb-2">How it works:</h4><ul class="list-group list-group-flush">')
    html_content = html_content.replace('<p><strong>Red Flags:</strong>', '</ul></div><div class="mt-3 mb-3"><h4 class="text-warning mb-2">Red Flags:</h4><ul class="list-group list-group-flush">')
    html_content = html_content.replace('<p><strong>What to Do:</strong>', '</ul></div><div class="mt-3 mb-3"><h4 class="text-success mb-2">What to Do:</h4><ul class="list-group list-group-flush">')
    html_content = html_content.replace('<p><strong>Quick Script:</strong>', '</ul></div><div class="alert alert-primary mt-3"><h5>Quick Script:</h5>')
    html_content = html_content.replace('<p><strong>Report &amp; Help:</strong>', '</div><div class="alert alert-secondary mt-3"><h5>Report & Help:</h5>')
    html_content = html_content.replace('<p><strong>Prevention Tips</strong>', '<div class="alert alert-success mt-5 p-4"><h3 class="text-center mb-4">Prevention Tips</h3>')
    
    return html_content

@app.route('/questionnaire')
def questionnaire():
    """Multi-step questionnaire form"""
    # Clear any existing session data when starting new questionnaire
    session.clear()
    return render_template('questionnaire.html')

@app.route('/submit_questionnaire', methods=['POST'])
def submit_questionnaire():
    """Process questionnaire submission and analyze with OpenAI"""
    try:
        # Get form data
        message_type = request.form.get('message_type')
        is_automated = request.form.get('is_automated', 'no')
        sender_info = request.form.get('sender_info', '')
        organization = request.form.get('organization', '')
        main_request = request.form.get('main_request', '')
        
        # Get message-type specific data
        email_subject = request.form.get('email_subject', '')
        has_links = request.form.get('has_links', 'no')
        looks_official = request.form.get('looks_official', 'yes')
        
        # Get checklist responses (with no defaults - user must answer)
        checklist_data = {}
        checklist_fields = [
            'asks_for_money',
            'asks_for_personal_info',
            'urgent_action_required',
            'threatens_consequences',
            'offers_unexpected_prize',
            'requests_immediate_payment',
            'sender_unknown',
            'poor_grammar_spelling',
            'suspicious_links',
            'requests_secrecy'
        ]
        
        for field in checklist_fields:
            value = request.form.get(field)
            checklist_data[field] = value if value else 'no'  # Default to 'no' only if nothing selected
        
        # Validate required fields
        if not message_type or not main_request:
            return render_template('questionnaire.html', 
                                 error="Please fill in all required fields.")
        
        # Prepare data for analysis
        scam_data = {
            'message_type': message_type,
            'is_automated': is_automated,
            'sender_info': sender_info,
            'organization': organization,
            'main_request': main_request,
            'email_subject': email_subject,
            'has_links': has_links,
            'looks_official': looks_official,
            'checklist': checklist_data
        }
        
        # Analyze with OpenAI
        analysis_result = analyze_scam_indicators(scam_data)
        
        # Store results in session for results page
        session['analysis_result'] = analysis_result
        session['scam_data'] = scam_data
        
        return redirect(url_for('results'))
        
    except Exception as e:
        logging.error(f"Error processing questionnaire: {str(e)}")
        return render_template('questionnaire.html', 
                             error="Unable to analyze your submission. Please try again or be cautious about the message.")

@app.route('/results')
def results():
    """Display analysis results"""
    analysis_result = session.get('analysis_result')
    scam_data = session.get('scam_data')
    
    if not analysis_result:
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                         analysis=analysis_result, 
                         data=scam_data)

@app.route('/start_over')
def start_over():
    """Clear session and start over"""
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return render_template('index.html', 
                         error="Something went wrong. Please try again."), 500
