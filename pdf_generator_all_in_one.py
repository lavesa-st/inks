#!/usr/bin/env python3
"""
Universal PDF Generator - All Languages Support
A single-file web tool that generates PDFs from multiple programming languages with database logging
"""

from flask import Flask, request, send_file, redirect, url_for, Response, jsonify
import os
import tempfile
import traceback
import subprocess
import sys
import logging
import time
from datetime import datetime
import re
import json

# Database imports
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.secret_key = 'universal_pdf_generator_secret_key'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    class PDFGeneration(Base):
        __tablename__ = "pdf_generations"
        
        id = Column(Integer, primary_key=True, index=True)
        language = Column(String(50), nullable=False)
        code_length = Column(Integer)
        success = Column(Boolean, default=False)
        error_message = Column(Text, nullable=True)
        fixes_applied = Column(Text, nullable=True)
        file_size = Column(Float, nullable=True)
        generation_time = Column(Float, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        user_ip = Column(String(45))

    # Create tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database setup error: {e}")

    def log_generation(language, code_length, success, error_message=None, fixes_applied=None, 
                      file_size=None, generation_time=None, user_ip=None):
        """Log PDF generation to database"""
        try:
            db = SessionLocal()
            log_entry = PDFGeneration(
                language=language,
                code_length=code_length,
                success=success,
                error_message=error_message,
                fixes_applied=json.dumps(fixes_applied) if fixes_applied else None,
                file_size=file_size,
                generation_time=generation_time,
                user_ip=user_ip
            )
            db.add(log_entry)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Database logging error: {e}")
else:
    def log_generation(*args, **kwargs):
        """Fallback when database is not available"""
        logger.info("Database not available, skipping log")

# HTML Templates as strings
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lavesa Inks - Beautiful PDF Creator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(90deg, #d5c3f1 0%, #f5c9d6 100%);
            min-height: 100vh;
            color: #2c2569;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 60px;
            padding: 60px 0;
        }
        
        .logo {
            width: 300px;
            height: auto;
            margin-bottom: 30px;
            filter: drop-shadow(0 8px 16px rgba(44, 37, 105, 0.3));
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        
        .brand-name {
            font-size: 3.5rem;
            font-weight: 700;
            color: #2c2569;
            margin-bottom: 15px;
            text-shadow: 0 4px 8px rgba(44, 37, 105, 0.2);
            letter-spacing: 2px;
        }
        
        .brand-tagline {
            font-size: 1.3rem;
            color: #2c2569;
            opacity: 0.85;
            font-weight: 400;
            margin-bottom: 30px;
        }
        
        .content-wrapper {
            background: linear-gradient(90deg, #ffeef3 0%, #d5c3f1 100%);
            border-radius: 25px;
            border: 3px solid #2c2569;
            box-shadow: 0 15px 40px rgba(44, 37, 105, 0.2);
            overflow: hidden;
            margin-bottom: 40px;
        }
        
        .instructions-section {
            padding: 50px 40px;
            background: rgba(255, 255, 255, 0.3);
            border-bottom: 2px solid #2c2569;
        }
        
        .instructions-title {
            font-size: 2rem;
            font-weight: 600;
            color: #2c2569;
            margin-bottom: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 35px;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.8);
            border: 2px solid #2c2569;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 10px;
            display: block;
        }
        
        .feature-title {
            font-weight: 600;
            margin-bottom: 8px;
            color: #2c2569;
        }
        
        .feature-desc {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .auto-fix-banner {
            background: #f5c9d6;
            border: 2px solid #2c2569;
            border-radius: 18px;
            padding: 25px;
            margin-top: 30px;
        }
        
        .auto-fix-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: #2c2569;
        }
        
        .stats-link {
            color: #2c2569;
            text-decoration: none;
            font-weight: 500;
            border-bottom: 2px solid #f5c9d6;
            transition: all 0.3s ease;
        }
        
        .stats-link:hover {
            background-color: #f5c9d6;
            padding: 4px 8px;
            border-radius: 6px;
        }
        
        .tabs-section {
            padding: 0 40px;
        }
        
        .language-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 0;
            border-bottom: 3px solid #2c2569;
            padding-bottom: 0;
            justify-content: center;
        }
        
        .tab {
            background: #f5c9d6;
            border: 2px solid #2c2569;
            border-bottom: none;
            color: #2c2569;
            padding: 15px 30px;
            font-size: 1.1rem;
            font-weight: 500;
            border-radius: 15px 15px 0 0;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }
        
        .tab:hover {
            background: #f5c9d6;
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(44, 37, 105, 0.25);
        }
        
        .tab.active {
            background: linear-gradient(90deg, #ffeef3 0%, #d5c3f1 100%);
            font-weight: 600;
            transform: translateY(-3px);
            box-shadow: 0 6px 12px rgba(44, 37, 105, 0.25);
        }
        
        .form-section {
            padding: 50px 40px;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 35px;
        }
        
        .form-label {
            display: block;
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c2569;
            margin-bottom: 15px;
        }
        
        .example-code {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid #2c2569;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 0.85rem;
            color: #2c2569;
            overflow-x: auto;
            white-space: pre;
        }
        
        .code-textarea {
            width: 100%;
            height: 350px;
            padding: 20px;
            border: 2px solid #2c2569;
            border-radius: 12px;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 0.9rem;
            background: rgba(255, 255, 255, 0.9);
            color: #2c2569;
            resize: vertical;
            transition: all 0.3s ease;
        }
        
        .code-textarea:focus {
            outline: none;
            border-color: #f5c9d6;
            box-shadow: 0 0 0 3px rgba(245, 201, 214, 0.3);
            background: rgba(255, 255, 255, 1);
        }
        
        .code-textarea::placeholder {
            color: rgba(44, 37, 105, 0.5);
        }
        
        .generate-btn {
            background: #f5c9d6;
            border: 3px solid #2c2569;
            color: #2c2569;
            padding: 20px 50px;
            font-size: 1.2rem;
            font-weight: 600;
            border-radius: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            display: flex;
            align-items: center;
            gap: 15px;
            margin: 30px auto;
            box-shadow: 0 6px 20px rgba(44, 37, 105, 0.25);
        }
        
        .generate-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(44, 37, 105, 0.35);
            background: #f5c9d6;
            filter: brightness(1.05);
        }
        
        .generate-btn:active {
            transform: translateY(0);
        }
        
        .message-area {
            margin: 20px 0;
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 12px;
            border: 2px solid #2c2569;
            margin-bottom: 15px;
            font-weight: 500;
        }
        
        .alert-success {
            background: #f5c9d6;
            color: #2c2569;
            border-color: #2c2569;
        }
        
        .alert-error {
            background: #ffeef3;
            color: #2c2569;
            border-color: #2c2569;
        }
        
        @media (max-width: 768px) {
            .main-container {
                padding: 15px;
            }
            
            .brand-name {
                font-size: 2rem;
            }
            
            .language-tabs {
                flex-wrap: wrap;
            }
            
            .tab {
                flex: 1;
                min-width: 120px;
                text-align: center;
                padding: 10px 15px;
                font-size: 0.9rem;
            }
            
            .feature-grid {
                grid-template-columns: 1fr;
            }
            
            .instructions-section,
            .form-section {
                padding: 30px 25px;
            }
        }
        
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(44, 37, 105, 0.3);
            border-radius: 50%;
            border-top-color: #2c2569;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <header class="header">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" alt="Lavesa Logo" class="logo" id="logo">
            <h1 class="brand-name">Lavesa Inks</h1>
            <p class="brand-tagline">✨ Beautiful PDF creation made simple and magical ✨</p>
        </header>
        
        <div class="content-wrapper">
            <section class="instructions-section">
                <h2 class="instructions-title">
                    <span>🎨</span>
                    Create Beautiful PDFs Effortlessly
                </h2>
                
                <div class="feature-grid">
                    <div class="feature-card">
                        <span class="feature-icon">🔧</span>
                        <div class="feature-title">Smart Auto-Fix</div>
                        <div class="feature-desc">Automatically fixes common errors in your code</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🌐</span>
                        <div class="feature-title">Multi-Language</div>
                        <div class="feature-desc">Python, HTML/CSS, JavaScript & Matplotlib</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">🛡️</span>
                        <div class="feature-title">Safe & Secure</div>
                        <div class="feature-desc">Code validation for your safety</div>
                    </div>
                    <div class="feature-card">
                        <span class="feature-icon">📊</span>
                        <div class="feature-title">Analytics</div>
                        <div class="feature-desc">Track and analyze your generations</div>
                    </div>
                </div>
                
                <div class="auto-fix-banner">
                    <div class="auto-fix-title">🤖 Enhanced Smart Fixes Include:</div>
                    <p>Smart quotes, unicode characters, missing imports, syntax errors, file paths, variable names, error handling, and language-specific optimizations!</p>
                    <p style="margin-top: 10px;">📈 <a href="/stats" target="_blank" class="stats-link">View Generation Statistics</a></p>
                </div>
            </section>
            
            <section class="tabs-section">
                <div class="language-tabs">
                    <button class="tab active" onclick="switchTab('python')">🐍 Python</button>
                    <button class="tab" onclick="switchTab('html')">🌐 HTML/CSS</button>
                    <button class="tab" onclick="switchTab('javascript')">⚡ JavaScript</button>
                    <button class="tab" onclick="switchTab('matplotlib')">📊 Matplotlib</button>
                </div>
            </section>
            
            <section class="form-section">
                <div id="message-area" class="message-area"></div>
                
                <form id="pdf-form" method="POST" action="/generate">
                    <input type="hidden" id="language" name="language" value="python">
                    
                    <!-- Python Tab -->
                    <div id="python-content" class="tab-content active">
                        <div class="form-group">
                            <label class="form-label">🐍 Python (ReportLab) Code:</label>
                            <div class="example-code"># Example:
file_path = "my_document.pdf"
pdf = SimpleDocTemplate(file_path, pagesize=A4)
story = []
story.append(Paragraph("Hello World!", getSampleStyleSheet()['Title']))
pdf.build(story)</div>
                            <textarea class="code-textarea" name="code" placeholder="Paste your Python ReportLab code here and watch the magic happen! ✨"></textarea>
                        </div>
                    </div>

                    <!-- HTML Tab -->
                    <div id="html-content" class="tab-content">
                        <div class="form-group">
                            <label class="form-label">🌐 HTML/CSS Code:</label>
                            <div class="example-code">&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        body { font-family: Arial; margin: 20px; }
        h1 { color: #2c2569; }
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;My Beautiful PDF&lt;/h1&gt;
    &lt;p&gt;This will be converted to PDF!&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;</div>
                            <textarea class="code-textarea" name="code" placeholder="Paste your HTML/CSS code here to create stunning web-to-PDF conversions! 🌐"></textarea>
                        </div>
                    </div>

                    <!-- JavaScript Tab -->
                    <div id="javascript-content" class="tab-content">
                        <div class="form-group">
                            <label class="form-label">⚡ JavaScript (jsPDF) Code:</label>
                            <div class="example-code">// Example:
const { jsPDF } = require('jspdf');
const doc = new jsPDF();
doc.text('Hello World!', 20, 20);
doc.save('my_document.pdf');</div>
                            <textarea class="code-textarea" name="code" placeholder="Paste your JavaScript code here for dynamic PDF generation! ⚡"></textarea>
                        </div>
                    </div>

                    <!-- Matplotlib Tab -->
                    <div id="matplotlib-content" class="tab-content">
                        <div class="form-group">
                            <label class="form-label">📊 Python (Matplotlib) Code:</label>
                            <div class="example-code"># Example:
import matplotlib.pyplot as plt
plt.figure(figsize=(8, 6))
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title('My Beautiful Chart')
plt.savefig('chart.pdf')
plt.close()</div>
                            <textarea class="code-textarea" name="code" placeholder="Paste your Matplotlib code here to create beautiful chart PDFs! 📊"></textarea>
                        </div>
                    </div>
                    
                    <button type="submit" class="generate-btn">
                        <span>✨</span>
                        Generate Beautiful PDF
                        <span>✨</span>
                    </button>
                </form>
            </section>
        </div>
    </div>

    <script>
        // Load the logo
        document.addEventListener('DOMContentLoaded', function() {
            const logoImg = document.getElementById('logo');
            logoImg.src = 'data:image/png;base64,' + btoa('PLACEHOLDER_FOR_LOGO');
            // The logo will be served by Flask route
            logoImg.onerror = function() {
                this.style.display = 'none';
            };
            
            // Try to load the actual logo
            fetch('/logo')
                .then(response => response.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    logoImg.src = url;
                    logoImg.style.display = 'block';
                })
                .catch(() => {
                    logoImg.style.display = 'none';
                });
        });
        
        function switchTab(language) {
            // Hide all content
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Remove active from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected content
            document.getElementById(language + '-content').classList.add('active');
            event.target.classList.add('active');
            
            // Update hidden input
            document.getElementById('language').value = language;
        }

        // Handle form submission with AJAX for better UX
        document.getElementById('pdf-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const messageArea = document.getElementById('message-area');
            const submitBtn = document.querySelector('.generate-btn');
            const originalContent = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<div class="loading-spinner"></div> Generating your beautiful PDF...';
            submitBtn.disabled = true;
            
            messageArea.innerHTML = '<div class="alert alert-success">🎨 Creating your beautiful PDF... Please wait while we work our magic! ✨</div>';
            
            fetch('/generate', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    return response.text().then(text => {
                        throw new Error(text);
                    });
                }
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'lavesa_generated_document.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                messageArea.innerHTML = '<div class="alert alert-success">✨ Success! Your beautiful PDF has been generated and downloaded! 🎉</div>';
            })
            .catch(error => {
                messageArea.innerHTML = '<div class="alert alert-error">🚫 Oops! Something went wrong: ' + error.message + '</div>';
            })
            .finally(() => {
                // Restore button state
                submitBtn.innerHTML = originalContent;
                submitBtn.disabled = false;
            });
        });
        
        // Add cute hover effects
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px) scale(1.02)';
                this.style.boxShadow = '0 8px 25px rgba(44, 37, 105, 0.2)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = 'none';
            });
        });
    </script>
</body>
</html>"""

def auto_fix_python_code(code):
    """Auto-fix Python ReportLab code with comprehensive error handling"""
    fixes_applied = []
    
    try:
        # Fix smart quotes (common copy-paste issue)
        if '"' in code or '"' in code or ''' in code or ''' in code:
            code = code.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
            fixes_applied.append("Fixed smart quotes → regular quotes")
        
        # Fix common unicode issues
        unicode_fixes = {
            '–': '-',  # en-dash to hyphen
            '—': '-',  # em-dash to hyphen
            '…': '...',  # ellipsis
            ''': "'",  # left single quote
            ''': "'",  # right single quote
        }
        for old, new in unicode_fixes.items():
            if old in code:
                code = code.replace(old, new)
                fixes_applied.append(f"Fixed unicode character: {old} → {new}")
        
        # Add missing imports for complex ReportLab code
        if 'from reportlab' not in code and 'import reportlab' not in code:
            imports = """from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.units import inch, mm, cm, pica
from reportlab.platypus import (
    SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, 
    Table, TableStyle, PageBreak, KeepTogether, Flowable, Image, NextPageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
import os
import sys

"""
            code = imports + code
            fixes_applied.append("Added comprehensive ReportLab imports")
        
        # Fix file paths
        path_fixes = {
            '/mnt/data/': './',
            '~/': './',
            'C:\\': './',
            'D:\\': './',
        }
        for old, new in path_fixes.items():
            if old in code:
                code = code.replace(old, new)
                fixes_applied.append(f"Fixed file path: {old} → {new}")
        
        # Fix common variable naming issues
        var_fixes = {
            'fileName': 'file_name',
            'filename': 'file_path',
            'pdfFile': 'pdf_file',
            'outputFile': 'output_file',
        }
        for old, new in var_fixes.items():
            if f'{old} =' in code:
                code = code.replace(f'{old} =', f'{new} =')
                fixes_applied.append(f"Fixed variable name: {old} → {new}")
        
        # Ensure the main function gets called
        if 'def build_pdf(' in code and 'if __name__ == "__main__":' in code:
            # The code has a proper structure, just make sure it runs
            if 'build_pdf(' not in code.split('if __name__ == "__main__":')[1]:
                # Add function call after the if __name__ block
                code += '\n\n# Auto-added function call\nbuild_pdf()'
                fixes_applied.append("Added missing function call")
        elif 'def ' in code and ('build' in code or 'generate' in code or 'create' in code):
            # Has a function but no main block - add it
            function_names = []
            lines = code.split('\n')
            for line in lines:
                if line.strip().startswith('def ') and any(word in line for word in ['build', 'generate', 'create']):
                    func_name = line.split('def ')[1].split('(')[0]
                    function_names.append(func_name)
            
            if function_names:
                code += f'\n\n# Auto-added function call\n{function_names[0]}()'
                fixes_applied.append(f"Added missing {function_names[0]}() call")
        
        # For simple ReportLab code patterns
        elif ('Paragraph(' in code or 'Spacer(' in code) and 'story = []' not in code:
            if 'pdf = SimpleDocTemplate(' in code:
                pdf_line_index = code.find('pdf = SimpleDocTemplate(')
                next_line_index = code.find('\n', pdf_line_index)
                if next_line_index != -1:
                    code = code[:next_line_index] + '\nstory = []' + code[next_line_index:]
                    fixes_applied.append("Added missing story list")
            
            # Add pdf.build if missing
            if 'story.append(' in code and 'pdf.build(' not in code and 'doc.build(' not in code:
                code += '\n\npdf.build(story)'
                fixes_applied.append("Added missing pdf.build(story)")
        
        # Fix alignment values
        alignment_fixes = {
            'alignment=center': 'alignment=1',
            'alignment="center"': 'alignment=1',
            'alignment=left': 'alignment=0',
            'alignment="left"': 'alignment=0',
            'alignment=right': 'alignment=2',
            'alignment="right"': 'alignment=2',
            'alignment=justify': 'alignment=4',
            'alignment="justify"': 'alignment=4',
        }
        
        for old, new in alignment_fixes.items():
            if old in code:
                code = code.replace(old, new)
                fixes_applied.append(f"Fixed alignment: {old} → {new}")
        
        # Fix common syntax errors
        syntax_fixes = {
            'colors.hexcolor(': 'colors.HexColor(',
            'Colors.HexColor(': 'colors.HexColor(',
            'getSampleStylesheet()': 'getSampleStyleSheet()',
            'getStyleSheet()': 'getSampleStyleSheet()',
        }
        
        for old, new in syntax_fixes.items():
            if old in code:
                code = code.replace(old, new)
                fixes_applied.append(f"Fixed syntax: {old} → {new}")
        
        # Add missing error handling
        if 'def ' in code and 'try:' not in code and 'except' not in code:
            # Wrap the main function call in try-except
            if 'build_pdf()' in code:
                code = code.replace('build_pdf()', '''try:
    build_pdf()
    print("✅ PDF generated successfully!")
except Exception as e:
    print(f"❌ Error: {e}")''')
                fixes_applied.append("Added error handling")
        
    except Exception as e:
        logger.error(f"Error in auto_fix_python_code: {e}")
        fixes_applied.append(f"Auto-fix encountered error: {str(e)}")
    
    return code, fixes_applied

def auto_fix_html_code(code):
    """Auto-fix HTML/CSS code with comprehensive error handling"""
    fixes_applied = []
    
    try:
        # Fix smart quotes and unicode issues (same as Python)
        if '"' in code or '"' in code or ''' in code or ''' in code:
            code = code.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
            fixes_applied.append("Fixed smart quotes → regular quotes")
        
        # Add DOCTYPE if missing
        if '<!DOCTYPE' not in code and '<html' in code:
            code = '<!DOCTYPE html>\n' + code
            fixes_applied.append("Added missing DOCTYPE")
        
        # Add charset if missing
        if '<meta charset=' not in code and '<head>' in code:
            code = code.replace('<head>', '<head>\n    <meta charset="UTF-8">')
            fixes_applied.append("Added UTF-8 charset")
        
        # Add viewport if missing
        if '<meta name="viewport"' not in code and '<head>' in code:
            code = code.replace('<head>', '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
            fixes_applied.append("Added viewport meta tag")
        
        # Add basic structure if missing
        if '<html' not in code:
            code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated PDF Document</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #213A5C; }}
        h2 {{ color: #5A7CA4; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="container">
{code}
    </div>
</body>
</html>"""
            fixes_applied.append("Added complete HTML5 document structure")
        
        # Fix common HTML issues
        html_fixes = {
            '<br>': '<br/>',
            '<hr>': '<hr/>',
            '<img ': '<img ',  # Will be caught by other fixes
            '&': '&amp;',  # Basic HTML encoding
        }
        
        for old, new in html_fixes.items():
            if old in code and old != '&amp;':  # Don't double-encode
                code = code.replace(old, new)
                fixes_applied.append(f"Fixed HTML: {old} → {new}")
        
        # Add title if missing
        if '<title>' not in code and '<head>' in code:
            code = code.replace('</head>', '    <title>PDF Document</title>\n</head>')
            fixes_applied.append("Added missing title tag")
        
    except Exception as e:
        logger.error(f"Error in auto_fix_html_code: {e}")
        fixes_applied.append(f"Auto-fix encountered error: {str(e)}")
    
    return code, fixes_applied

def auto_fix_javascript_code(code):
    """Auto-fix JavaScript code"""
    fixes_applied = []
    
    # Add jsPDF require if missing
    if 'jsPDF' in code and 'require(' not in code and 'import' not in code:
        code = "const { jsPDF } = require('jspdf');\n" + code
        fixes_applied.append("Added jsPDF import")
    
    # Fix common variable issues
    if 'doc.save(' not in code and 'new jsPDF()' in code:
        code += "\ndoc.save('document.pdf');"
        fixes_applied.append("Added missing doc.save()")
    
    return code, fixes_applied

def auto_fix_matplotlib_code(code):
    """Auto-fix Matplotlib code with comprehensive error handling"""
    fixes_applied = []
    
    try:
        # Fix smart quotes (same as Python)
        if '"' in code or '"' in code or ''' in code or ''' in code:
            code = code.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
            fixes_applied.append("Fixed smart quotes → regular quotes")
        
        # Add comprehensive imports if missing
        if 'matplotlib' not in code and ('plt.' in code or 'pyplot' in code):
            imports = """import matplotlib
matplotlib.use('Agg')  # Backend for server environment
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
"""
            code = imports + code
            fixes_applied.append("Added comprehensive matplotlib imports")
        
        # Add backend setting if missing
        if 'matplotlib.use(' not in code and 'import matplotlib' in code:
            code = code.replace('import matplotlib', 'import matplotlib\nmatplotlib.use(\'Agg\')')
            fixes_applied.append("Added Agg backend for server environment")
        
        # Add numpy import if array operations detected
        if ('np.' in code or 'numpy' in code) and 'import numpy' not in code:
            code = 'import numpy as np\n' + code
            fixes_applied.append("Added numpy import")
        
        # Add pandas import if DataFrame operations detected
        if ('pd.' in code or 'DataFrame' in code) and 'import pandas' not in code:
            code = 'import pandas as pd\n' + code
            fixes_applied.append("Added pandas import")
        
        # Fix common matplotlib issues
        mpl_fixes = {
            'plt.show()': '# plt.show() removed for PDF generation',
            'pyplot.show()': '# pyplot.show() removed for PDF generation',
            'plt.ion()': '# plt.ion() removed for server environment',
            'plt.ioff()': '# plt.ioff() removed for server environment',
        }
        
        for old, new in mpl_fixes.items():
            if old in code:
                code = code.replace(old, new)
                fixes_applied.append(f"Fixed matplotlib: {old} → {new}")
        
        # Add savefig if missing
        if 'plt.' in code and 'savefig(' not in code and 'save(' not in code:
            code += "\n\n# Auto-added save commands\nplt.tight_layout()\nplt.savefig('chart.pdf', bbox_inches='tight', dpi=300)\nplt.close()"
            fixes_applied.append("Added plt.savefig() with tight layout and close")
        
        # Fix file paths
        if 'savefig(' in code:
            # Ensure PDF extension
            if '.png' in code:
                code = code.replace('.png', '.pdf')
                fixes_applied.append("Changed output format from PNG to PDF")
            elif '.jpg' in code or '.jpeg' in code:
                code = code.replace('.jpg', '.pdf').replace('.jpeg', '.pdf')
                fixes_applied.append("Changed output format from JPEG to PDF")
        
    except Exception as e:
        logger.error(f"Error in auto_fix_matplotlib_code: {e}")
        fixes_applied.append(f"Auto-fix encountered error: {str(e)}")
    
    return code, fixes_applied

def execute_python_code(code):
    """Execute Python code and return PDF file path"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    try:
        exec_globals = {}
        exec(compile(open(temp_file_path).read(), temp_file_path, 'exec'), exec_globals)
        os.unlink(temp_file_path)
        
        # Find generated PDF
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        if pdf_files:
            return max(pdf_files, key=os.path.getctime)
        return None
    except Exception as e:
        os.unlink(temp_file_path)
        raise e

def execute_html_code(code):
    """Convert HTML to PDF using weasyprint"""
    try:
        import weasyprint
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        pdf_path = 'html_document.pdf'
        weasyprint.HTML(filename=temp_file_path).write_pdf(pdf_path)
        os.unlink(temp_file_path)
        return pdf_path
    except ImportError:
        # Fallback to wkhtmltopdf
        return execute_html_with_wkhtmltopdf(code)

def execute_html_with_wkhtmltopdf(code):
    """Convert HTML to PDF using wkhtmltopdf"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    pdf_path = 'html_document.pdf'
    subprocess.run(['wkhtmltopdf', temp_file_path, pdf_path], check=True)
    os.unlink(temp_file_path)
    return pdf_path

def execute_javascript_code(code):
    """Execute JavaScript code (simplified - would need Node.js setup)"""
    # For now, we'll create a simple PDF response
    # In a full implementation, you'd set up Node.js with jsPDF
    raise Exception("JavaScript execution requires Node.js setup. Please use Python or HTML instead.")

@app.route('/')
def index():
    """Main page"""
    return Response(INDEX_HTML, mimetype='text/html')

@app.route('/logo')
def logo():
    """Serve the logo image"""
    try:
        return send_file('lavesa_logo.png', mimetype='image/png')
    except:
        # Return a transparent pixel if logo not found
        return Response(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00IEND\xaeB`\x82', 
                        mimetype='image/png')

@app.route('/generate', methods=['POST'])
def generate_pdf():
    """Generate PDF from submitted code with comprehensive error handling and logging"""
    start_time = time.time()
    language = 'unknown'
    user_code = ''
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    
    try:
        # Input validation
        language = request.form.get('language', 'python').lower().strip()
        user_code = request.form.get('code', '').strip()
        
        # Validate language
        supported_languages = ['python', 'html', 'matplotlib', 'javascript']
        if language not in supported_languages:
            error_msg = f"Unsupported language: {language}. Supported: {', '.join(supported_languages)}"
            log_generation(language, len(user_code), False, error_msg, None, None, None, user_ip)
            return Response(error_msg, status=400)
        
        if not user_code:
            error_msg = "Please enter some code to generate PDF"
            log_generation(language, 0, False, error_msg, None, None, None, user_ip)
            return Response(error_msg, status=400)
        
        # Security check - basic validation
        dangerous_patterns = [
            'import subprocess', '__import__', 'eval(', 'exec(', 'open(',
            'file(', 'input(', 'raw_input(', 'compile(', 'globals()',
            'locals()', 'vars()', 'dir()', 'hasattr(', 'getattr(',
            'setattr(', 'delattr(', 'reload(', 'memoryview('
        ]
        
        # Allow some patterns if they're in safe contexts
        safe_contexts = ['exec(compile(open(temp_file_path).read()']
        code_lower = user_code.lower()
        
        for pattern in dangerous_patterns:
            if pattern in code_lower and not any(safe in user_code for safe in safe_contexts):
                error_msg = f"Code contains potentially dangerous pattern: {pattern}"
                log_generation(language, len(user_code), False, error_msg, None, None, None, user_ip)
                return Response(error_msg, status=400)
        
        logger.info(f"Processing {language} code: {len(user_code)} characters")
        
        # Auto-fix code based on language
        fixes_applied = []
        try:
            if language == 'python':
                fixed_code, fixes_applied = auto_fix_python_code(user_code)
                pdf_file = execute_python_code(fixed_code)
            elif language == 'html':
                fixed_code, fixes_applied = auto_fix_html_code(user_code)
                pdf_file = execute_html_code(fixed_code)
            elif language == 'matplotlib':
                fixed_code, fixes_applied = auto_fix_matplotlib_code(user_code)
                pdf_file = execute_python_code(fixed_code)
            elif language == 'javascript':
                fixed_code, fixes_applied = auto_fix_javascript_code(user_code)
                pdf_file = execute_javascript_code(fixed_code)
            else:
                raise ValueError(f"Unsupported language: {language}")
        
        except Exception as code_error:
            error_msg = f"Code execution error: {str(code_error)}"
            generation_time = time.time() - start_time
            log_generation(language, len(user_code), False, error_msg, fixes_applied, None, generation_time, user_ip)
            logger.error(f"Code execution failed: {code_error}")
            return Response(error_msg, status=500)
        
        # Check if PDF was generated
        if pdf_file and os.path.exists(pdf_file):
            try:
                file_size = os.path.getsize(pdf_file)
                generation_time = time.time() - start_time
                
                # Log successful generation
                log_generation(language, len(user_code), True, None, fixes_applied, file_size, generation_time, user_ip)
                
                logger.info(f"PDF generated successfully: {pdf_file}, {file_size} bytes, {generation_time:.2f}s")
                
                return send_file(pdf_file, as_attachment=True)
            except Exception as file_error:
                error_msg = f"Error sending file: {str(file_error)}"
                generation_time = time.time() - start_time
                log_generation(language, len(user_code), False, error_msg, fixes_applied, None, generation_time, user_ip)
                return Response(error_msg, status=500)
        else:
            error_msg = "No PDF file was generated. Check your code for errors."
            generation_time = time.time() - start_time
            log_generation(language, len(user_code), False, error_msg, fixes_applied, None, generation_time, user_ip)
            return Response(error_msg, status=400)
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        generation_time = time.time() - start_time
        log_generation(language, len(user_code), False, error_msg, None, None, generation_time, user_ip)
        logger.error(f"Unexpected error in generate_pdf: {e}")
        logger.error(traceback.format_exc())
        return Response(error_msg, status=500)

@app.route('/stats')
def stats():
    """Show generation statistics"""
    if not DATABASE_URL:
        return jsonify({"error": "Database not available"})
    
    try:
        db = SessionLocal()
        
        # Get basic stats
        total_generations = db.query(PDFGeneration).count()
        successful_generations = db.query(PDFGeneration).filter(PDFGeneration.success == True).count()
        
        # Language breakdown
        from sqlalchemy import func
        language_stats = db.query(
            PDFGeneration.language,
            func.count(PDFGeneration.id).label('count'),
            func.avg(PDFGeneration.generation_time).label('avg_time')
        ).group_by(PDFGeneration.language).all()
        
        # Recent generations
        recent = db.query(PDFGeneration).order_by(PDFGeneration.created_at.desc()).limit(10).all()
        
        db.close()
        
        stats_data = {
            "total_generations": total_generations,
            "successful_generations": successful_generations,
            "success_rate": f"{(successful_generations/total_generations*100):.1f}%" if total_generations > 0 else "0%",
            "language_stats": [
                {
                    "language": lang,
                    "count": count,
                    "avg_time": f"{avg_time:.2f}s" if avg_time else "N/A"
                }
                for lang, count, avg_time in language_stats
            ],
            "recent_generations": [
                {
                    "language": gen.language,
                    "success": gen.success,
                    "created_at": gen.created_at.isoformat(),
                    "file_size": gen.file_size,
                    "generation_time": gen.generation_time
                }
                for gen in recent
            ]
        }
        
        return jsonify(stats_data)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🌍 Universal PDF Generator Starting...")
    print("=" * 50)
    print("📝 Supports: Python, HTML/CSS, Matplotlib, JavaScript")
    print("🔧 Auto-fix: Automatically fixes common errors")
    print("🚀 Ready at: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)