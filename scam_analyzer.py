import json
import os
from openai import OpenAI
import logging

# Using GPT-3.5 Turbo for scam analysis as requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def _default_response():
    return {
        'risk_level': 'unknown',
        'is_likely_scam': None,
        'confidence': 0,
        'explanation': "We were unable to analyze this message. When in doubt, it's best to be cautious.",
        'next_steps': [
            'Do not provide any personal information or money',
            'Contact the organization directly using official contact information',
            'Ask a trusted family member or friend for advice'
        ],
        'warning_signs': ['Unable to complete analysis - exercise caution']
    }


def analyze_scam_indicators(scam_data):
    """Analyze scam indicators using OpenAI GPT-3.5 Turbo"""
    if openai_client is None:
        logging.error("OpenAI API key not configured")
        return _default_response()

    try:
        # Build the prompt with user data
        prompt = build_analysis_prompt(scam_data)

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fraud prevention expert specializing in helping seniors identify scams. "
                    "Provide clear, simple analysis that older adults can easily understand. "
                    "Always be reassuring and avoid technical jargon. "
                    "Respond with JSON in this exact format: "
                    "{'risk_level': 'low'|'medium'|'high', 'is_likely_scam': true|false, "
                    "'confidence': number between 0 and 1, 'explanation': 'simple explanation', "
                    "'next_steps': ['step1', 'step2', 'step3'], 'warning_signs': ['sign1', 'sign2']}"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Lower temperature for more consistent analysis
        )

        result = json.loads(response.choices[0].message.content)

        # Validate and sanitize the response
        return validate_analysis_result(result)

    except Exception as e:
        logging.error(f"OpenAI analysis failed: {str(e)}")
        return _default_response()

def build_analysis_prompt(scam_data):
    """Build structured prompt for OpenAI analysis"""
    
    checklist_yes_responses = []
    for key, value in scam_data['checklist'].items():
        if value == 'yes':
            # Convert field names to readable format
            readable_name = key.replace('_', ' ').title()
            checklist_yes_responses.append(readable_name)
    
    prompt = f"""
Please analyze this communication for scam indicators from an Australian context:

Message Type: {scam_data['message_type'].replace('_', ' ').title()}
"""
    
    # Add message-type specific details
    if scam_data['message_type'] == 'phone_call':
        prompt += f"Automated Message: {scam_data['is_automated']}\n"
        if scam_data['sender_info']:
            prompt += f"Phone Number: {scam_data['sender_info']}\n"
    elif scam_data['message_type'] == 'email':
        if scam_data['sender_info']:
            prompt += f"Email Address: {scam_data['sender_info']}\n"
        if scam_data['email_subject']:
            prompt += f"Subject Line: {scam_data['email_subject']}\n"
    elif scam_data['message_type'] == 'text_message':
        if scam_data['sender_info']:
            prompt += f"Sender Number: {scam_data['sender_info']}\n"
        prompt += f"Contains Links: {scam_data.get('has_links', 'no')}\n"
    elif scam_data['message_type'] == 'letter':
        if scam_data['sender_info']:
            prompt += f"Return Address: {scam_data['sender_info']}\n"
        prompt += f"Appears Official: {scam_data.get('looks_official', 'yes')}\n"
    
    prompt += f"""
Organization Claimed: {scam_data['organization'] if scam_data['organization'] else 'Not specified'}
Main Request/Content: {scam_data['main_request']}

Scam Indicators Present: {', '.join(checklist_yes_responses) if checklist_yes_responses else 'None reported'}

Please provide a fraud risk assessment suitable for Australian seniors, considering local scam patterns and regulatory bodies.
Focus on practical advice and clear explanations. Consider Australian-specific organizations and scam types.
"""
    
    return prompt

def validate_analysis_result(result):
    """Validate and sanitize OpenAI response"""
    
    # Ensure all required fields exist with safe defaults
    validated = {
        'risk_level': result.get('risk_level', 'unknown'),
        'is_likely_scam': result.get('is_likely_scam', None),
        'confidence': max(0, min(1, result.get('confidence', 0))),
        'explanation': result.get('explanation', 'Analysis incomplete - exercise caution'),
        'next_steps': result.get('next_steps', [
            'Do not provide personal information',
            'Verify through official channels',
            'Consult with trusted contacts'
        ]),
        'warning_signs': result.get('warning_signs', ['Analysis incomplete'])
    }
    
    # Validate risk_level
    if validated['risk_level'] not in ['low', 'medium', 'high', 'unknown']:
        validated['risk_level'] = 'unknown'
    
    # Ensure lists are actually lists
    if not isinstance(validated['next_steps'], list):
        validated['next_steps'] = ['Contact official sources to verify']
    
    if not isinstance(validated['warning_signs'], list):
        validated['warning_signs'] = ['Unable to identify specific warning signs']
    
    return validated
