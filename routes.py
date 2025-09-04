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
        html_content = markdown.markdown(markdown_content, extensions=['extra', 'toc'])
        
        # Add senior-friendly CSS classes to the HTML
        html_content = format_scam_content(html_content)
        
        return render_template('learn.html', scam_content=html_content)
        
    except Exception as e:
        logging.error(f"Error loading scam content: {str(e)}")
        return render_template('learn.html', 
                             scam_content="<p>Unable to load educational content. Please try again later.</p>")

def format_scam_content(html_content):
    """Add senior-friendly styling classes to the generated HTML"""
    import re
    
    # Find all h2 headers (scam titles) 
    h2_pattern = r'<h2>(.*?)</h2>'
    matches = re.findall(h2_pattern, html_content)
    
    # Style the main title first
    html_content = html_content.replace('<h1>', '<h1 class="display-4 fw-bold text-primary mb-3">')
    
    # Create index HTML after title
    if matches:
        index_html = '''
        <div class="scam-index bg-light p-4 rounded-3 mb-5">
            <h3 class="text-center mb-4"><i class="fas fa-list me-2"></i>Quick Navigation</h3>
            <div class="row">
        '''
        
        for i, match in enumerate(matches[:10]):
            clean_title = re.sub(r'<.*?>', '', match).strip()
            anchor_id = f"scam-{i+1}"
            
            index_html += f'''
                <div class="col-md-6 mb-2">
                    <a href="#{anchor_id}" class="btn btn-outline-primary btn-sm d-block text-start">
                        <i class="fas fa-chevron-right me-2"></i>{clean_title}
                    </a>
                </div>
            '''
        
        index_html += '</div></div>'
        
        # Insert index after the first paragraph 
        first_p_end = html_content.find('</p>')
        if first_p_end != -1:
            html_content = html_content[:first_p_end + 4] + index_html + html_content[first_p_end + 4:]
    
    # Transform each scam section
    for i, match in enumerate(matches[:10]):
        anchor_id = f"scam-{i+1}"
        old_h2 = f'<h2>{match}</h2>'
        new_h2 = f'''<div class="scam-section mb-5" id="{anchor_id}">
<h2 class="h3 fw-bold text-white mb-4 p-3 bg-primary rounded">
    <i class="fas fa-exclamation-triangle me-2"></i>{match}
</h2>'''
        html_content = html_content.replace(old_h2, new_h2)
    
    # Style subsections consistently
    html_content = re.sub(r'<p><strong>Summary:</strong>', 
        '<div class="section-content"><div class="mb-3"><h5 class="fw-bold text-primary mb-2"><i class="fas fa-info-circle me-2"></i>Summary</h5><p class="fs-5">', 
        html_content)
    
    html_content = re.sub(r'<p><strong>How it works:</strong>', 
        '</p></div><div class="mb-3"><h5 class="fw-bold text-primary mb-2"><i class="fas fa-cog me-2"></i>How it works</h5>', 
        html_content)
    
    html_content = re.sub(r'<p><strong>Red Flags:</strong>', 
        '</div><div class="mb-3"><h5 class="fw-bold text-primary mb-2"><i class="fas fa-flag me-2"></i>Red Flags</h5>', 
        html_content)
    
    html_content = re.sub(r'<p><strong>What to Do:</strong>', 
        '</div><div class="mb-3"><h5 class="fw-bold text-primary mb-2"><i class="fas fa-shield-alt me-2"></i>What to Do</h5>', 
        html_content)
    
    html_content = re.sub(r'<p><strong>Quick Script:</strong>', 
        '</div><div class="mb-3"><h5 class="fw-bold text-primary mb-2"><i class="fas fa-comment me-2"></i>Quick Script</h5><div class="alert alert-info">', 
        html_content)
    
    html_content = re.sub(r'<p><strong>Report &amp; Help:</strong>', 
        '</div></div><div class="mb-4"><h5 class="fw-bold text-primary mb-2"><i class="fas fa-phone me-2"></i>Report & Help</h5>', 
        html_content)
    
    # Close sections properly
    html_content = re.sub(r'<hr />', '</div></div></div><hr class="my-5" />', html_content)
    
    # Style links as buttons
    html_content = re.sub(r'<a href="([^"]+)">([^<]+)</a>', 
        r'<a href="\1" target="_blank" class="btn btn-sm btn-outline-primary me-2 mb-2"><i class="fas fa-external-link-alt me-1"></i>\2</a>', 
        html_content)
    
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
