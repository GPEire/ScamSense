# Scam Checker Application

## Overview

The Scam Checker is a web application designed to help seniors and caregivers identify potential scams in communications they receive. The application uses a guided questionnaire approach to collect information about suspicious messages (emails, phone calls, texts, or letters) and leverages OpenAI's GPT-5 model to provide intelligent analysis and recommendations. The interface is specifically designed with accessibility and senior-friendly features, including large fonts, high contrast colors, and simple navigation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating engine
- **UI Framework**: Bootstrap 5 for responsive design and accessibility features
- **Design Philosophy**: Senior-friendly interface with large fonts (18px+ base), high contrast colors, and simplified navigation
- **Accessibility**: WCAG-compliant features including skip links, screen reader support, and keyboard navigation
- **Progressive Enhancement**: JavaScript enhances the experience but the core functionality works without it

### Backend Architecture
- **Web Framework**: Flask (Python) with modular route organization
- **Session Management**: Flask sessions for temporary data storage during questionnaire flow
- **Error Handling**: Comprehensive logging and graceful fallbacks for API failures
- **Security**: Environment-based configuration with secure session keys

### Data Flow Architecture
- **Stateless Design**: No persistent user data storage - all analysis is session-based
- **Multi-step Form**: Progressive questionnaire with conditional logic (e.g., automated message detection for phone calls)
- **Structured Analysis**: Form data is converted to structured prompts for AI analysis
- **Response Validation**: AI responses are validated and sanitized before presentation

### AI Integration Architecture
- **Model**: OpenAI GPT-5 with specialized system prompts for fraud detection
- **Prompt Engineering**: Structured prompts that combine user input with fraud detection expertise
- **Response Format**: JSON-structured responses with risk levels, explanations, and actionable next steps
- **Fallback Strategy**: Safe default responses when AI analysis fails

## External Dependencies

### AI Services
- **OpenAI GPT-5 API**: Primary intelligence for scam analysis and risk assessment
- **Configuration**: API key managed through environment variables

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and accessibility components
- **Font Awesome 6**: Icon library for visual indicators and improved UX

### Python Packages
- **Flask**: Web framework for routing and templating
- **OpenAI Python Client**: Official SDK for GPT-5 integration
- **Standard Library**: logging, json, os for core functionality

### Development Dependencies
- **Environment Variables**: SESSION_SECRET, OPENAI_API_KEY for configuration management
- **Debug Logging**: Comprehensive logging setup for development and troubleshooting