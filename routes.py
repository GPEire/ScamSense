from flask import render_template, request, jsonify, redirect, url_for, session
from app import app
from scam_analyzer import analyze_scam_indicators
import logging

@app.route('/')
def index():
    """Landing page with prominent scam check button"""
    return render_template('index.html')

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
