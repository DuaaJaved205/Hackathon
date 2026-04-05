You are a senior software engineer, security auditor, and project documentation expert.
Your task is to analyze my repository and provide the following without modifying any code:
1. Project Understanding
Analyze full project structure
Identify tech stack (Node.js, Python, React, etc.)
Understand what the project does
Detect dependencies, APIs, databases, and services used
2. Generate QWEN.md
Include:
Project Overview: what it does, main features, purpose
Folder Structure: explain important folders/files in simple terms
Setup Instructions: step-by-step guide
How to Run: commands to start the project
Build & Deployment: instructions if applicable
Dependencies: key libraries, frameworks, tools
3. Environment Variables Guidance
Detect all variables that should be in .env, including:
API keys
Database URLs
Ports
Secret keys
OAuth tokens (like Gmail or other services)
Create a .env.example file using placeholders only, e.g.:

GMAIL_CLIENT_ID=YOUR_CLIENT_ID_HERE
GMAIL_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
DATABASE_URL=YOUR_DATABASE_URL_HERE
API_KEY=YOUR_API_KEY_HERE
PORT=YOUR_PORT_HERE
Add comments explaining each variable
Clearly indicate which values must never be pushed to GitHub
Explain which values are safe to share
4. Verify Project Works Without Your Deleted Gmail
Ensure the project runs safely using placeholders instead of your old credentials
Highlight any parts that would fail if personal credentials are missing
Provide guidance for someone else to run the project safely with their own credentials
5. Security Awareness Section
Why .env is used
What kind of data should be kept secret
Best practices to avoid leaking sensitive data
6. Future Developer Guidance
Highlight missing configurations
Suggest improvements in structure or security
7. Output Format
Provide:
Complete QWEN.md content
Complete .env.example file with placeholders and comments
List of sensitive variables that must never be shared
Verification summary: “Project works with generic credentials” or any warnings
Rules
Do NOT include any real secrets
Do NOT modify project files
Use placeholders only
Be clear, structured, and beginner-friendly