# Credit Card Statement Parser

A web application that automatically extracts key information from credit card statements across multiple Indian banks.

## Overview

The Credit Card Statement Parser is a tool that analyzes PDF credit card statements and extracts critical information such as:

- Issuer/Bank name
- Card last 4 digits
- Card type/network (Visa, Mastercard, RuPay, etc.)
- Statement billing period
- Payment due date

The system supports statements from major Indian banks including ICICI, HDFC, Axis Bank, and Kotak Mahindra Bank, with a modular architecture for adding additional issuers.

## Features

- 📄 Upload PDF credit card statements
- 🔍 Automatic bank detection
- 🔐 Support for password-protected PDFs
- 🏦 Multi-bank support with specialized parsers
- 📊 Confidence scoring for extraction accuracy
- 📱 Responsive UI design with Tailwind CSS

## Tech Stack

### Backend
- FastAPI (Python web framework)
- pdfplumber for PDF text extraction
- Custom parsing logic for each supported bank
- Modular design for easy addition of new banks

### Frontend
- React with Vite for fast development
- Tailwind CSS for responsive styling
- Drag-and-drop file upload

## Supported Banks

- ICICI Bank
- HDFC Bank
- Axis Bank
- Kotak Mahindra Bank

## Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/credit-card-statement-parser.git
cd credit-card-statement-parser/backend

# Create and activate virtual environment
python -m venv env
# On Windows
env\Scripts\activate
# On Unix/MacOS
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000