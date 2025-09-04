# Product Requirements Document (PRD) – Scam Checker Form Page

## Objective
Create an easy-to-use web form that helps seniors and caregivers determine if a message or communication they received might be a scam. The form uses a guided questionnaire, with backend analysis powered by an LLM. This feature is part of a website. 

---

## User Flow
1. **Landing Page**
   - Prominent button: *“Check if this is a scam.”*
   - Clear, supportive language reassuring users their data is safe.

2. **Form Introduction**
   - Short, friendly explanation of purpose.
   - Accessibility-first design: large text, high contrast.

3. **Questionnaire Steps**
   - **Step 1:** Select type of message (Email, Phone call, Text, etc.).
   - **Step 1a:** if phone call: was it an automated message? 
   - **Step 2:** Enter basic details (sender, organization, or main request).
   - **Step 3:** Yes/No checklist (e.g., *“Does it ask for money?”*, *“Does it ask for personal details?”*).

4. **Submission**
   - “Check for Scams” button sends inputs to backend.
   - Backend formats inputs into structured prompt for the LLM.

5. **Results Page**
   - Clear verdict: “This looks suspicious” or “No major red flags.”
   - Next steps: Report guidance, trusted contacts, escalation advice.
   - Simple reassurance: “We’ve checked this for you. Stay safe.”

---

## Design Considerations
- **User Persona**
  - Older generations (Boomer and above)
- **Accessibility**
  - Large fonts, high contrast, simplified navigation.
  - Voice support and read-aloud options.
- **Clarity**
  - No jargon; plain English explanations.
- **Reassurance**
  - Emphasize data privacy.
  - Include disclaimers: educational tool, not foolproof.

---

## Technical Specifications

### Frontend
- **Stack:** HTML, CSS, JavaScript.
- **Features:**  
  - Accessible form with large buttons and text.  
  - Simple navigation between steps.  
  - Client-side validation for required fields.

### Backend
- **Stack:** Python (Flask).  
- **Responsibilities:**  
  - Receive user form input via POST request.  
  - Format input into structured prompt for LLM.  
  - Call OpenAI API (GPT-3.5 Turbo recommended).  
  - Parse LLM response into clear, actionable output.  
  - Return results to frontend.

### LLM Integration
- **Model:** GPT-3.5 Turbo (fast, cost-effective).  
- **Function:** LLM to act as fraud expert and Analyze message details and classify risk.  
- **Output:** Simple labels and explanation for seniors (e.g., “High risk: phishing email” with advice).  

### Error Handling
- **Frontend:** User-friendly error messages if form submission fails.  
- **Backend:** Graceful handling of API failures; default to “Unable to check – be cautious.”  

---

## MVP Feature Set
- Scam type selector.  
- Yes/No checklist of scam indicators.  
- LLM analysis of structured input.  
- Simple results page with next steps.  
- Accessibility-first UI.


---

## Security & Privacy
- No sensitive data stored.  
- All analysis is ephemeral.  
- HTTPS enforced.  
- Clear disclaimer that results are educational, not guaranteed.

---

## Future Enhancements (Out of Scope)
- Add caregiver dashboards.  
- Support for attachments/screenshots.  
- Integration with national scam-reporting hotlines.  
- Gamified “learning” mode after checks.  
