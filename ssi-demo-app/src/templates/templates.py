#!/usr/bin/env python3
"""
Frontend Templates for SSI Demo Application
This module contains the HTML templates for the SSI demo interface.
"""

from aiohttp import web
from aiohttp.web import Request, Response

async def index_page(request: Request) -> Response:
    """Serve main page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SSI Demo - User Identity Issuer & Verifier</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            }
            h1 {
                text-align: center;
                color: #5a67d8;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .section {
                margin: 30px 0;
                padding: 25px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                transition: all 0.3s ease;
            }
            .section:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }
            .issuer-section {
                background: linear-gradient(135deg, #c3f0ca 0%, #e8f5e8 100%);
                border-color: #68d391;
            }
            .verifier-section {
                background: linear-gradient(135deg, #bfdbfe 0%, #e8e8f5 100%);
                border-color: #63b3ed;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                margin: 10px 5px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            button:disabled {
                background: #a0aec0;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .qr-container {
                text-align: center;
                margin: 25px 0;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
            }
            .qr-code {
                max-width: 300px;
                margin: 20px auto;
                display: block;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .status {
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
                font-weight: 600;
                border-left: 5px solid;
            }
            .status.success {
                background-color: #c6f6d5;
                color: #22543d;
                border-left-color: #38a169;
            }
            .status.warning {
                background-color: #fefcbf;
                color: #744210;
                border-left-color: #ecc94b;
            }
            .status.error {
                background-color: #fed7d7;
                color: #742a2a;
                border-left-color: #e53e3e;
            }
            .form-group {
                margin: 20px 0;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #4a5568;
            }
            input[type="text"], input[type="email"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s ease;
                box-sizing: border-box;
            }
            input[type="text"]:focus, input[type="email"]:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .steps {
                background: #f7fafc;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border: 1px solid #e2e8f0;
            }
            .step {
                margin: 12px 0;
                padding: 15px;
                border-left: 4px solid #cbd5e0;
                background: white;
                border-radius: 0 8px 8px 0;
                transition: all 0.3s ease;
            }
            .step.completed {
                border-left-color: #38a169;
                background: #c6f6d5;
                color: #22543d;
            }
            .step.current {
                border-left-color: #ecc94b;
                background: #fefcbf;
                color: #744210;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            .credentials-info {
                background: #edf2f7;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 5px solid #667eea;
            }
            .attribute {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #e2e8f0;
            }
            .attribute:last-child {
                border-bottom: none;
            }
            .attribute-name {
                font-weight: 600;
                color: #4a5568;
            }
            .attribute-value {
                color: #2d3748;
                font-family: monospace;
                background: #f7fafc;
                padding: 2px 8px;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 SSI Demo Application</h1>
            <p class="subtitle">Single Agent - Issuer & Verifier (Minimal SSI Steps)</p>
            <div class="credentials-info">
                <h3>📋 Credential Attributes</h3>
                <p>This demo issues and verifies credentials with these attributes:</p>
                <div class="attribute">
                    <span class="attribute-name">username</span>
                    <span class="attribute-value">User's chosen username</span>
                </div>
                <div class="attribute">
                    <span class="attribute-name">email</span>
                    <span class="attribute-value">User's email address</span>
                </div>
                <div class="attribute">
                    <span class="attribute-name">occupation</span>
                    <span class="attribute-value">User's job title</span>
                </div>
                <div class="attribute">
                    <span class="attribute-name">citizenship</span>
                    <span class="attribute-value">User's nationality</span>
                </div>
            </div>
            
            <!-- Issuer Section -->
            <div class="section issuer-section">
                <h2>📋 Credential Issuer</h2>
                <p>Issue a User Identity credential to your mobile wallet.</p>
                
                <div class="form-group">
                    <label for="username">👤 Username:</label>
                    <input type="text" id="username" placeholder="e.g., john_doe" required>
                </div>
                
                <div class="form-group">
                    <label for="email">📧 Email:</label>
                    <input type="email" id="email" placeholder="e.g., john@example.com" required>
                </div>
                
                <div class="form-group">
                    <label for="occupation">💼 Occupation:</label>
                    <input type="text" id="occupation" placeholder="e.g., Software Engineer" required>
                </div>
                
                <div class="form-group">
                    <label for="citizenship">🌍 Citizenship:</label>
                    <input type="text" id="citizenship" placeholder="e.g., United States" required>
                </div>
                
                <button onclick="startIssuerFlow()">🎯 Generate Issuer QR Code</button>
                
                <div id="issuer-qr-container" class="qr-container" style="display: none;">
                    <h3>📱 Scan with Aries Bifold wallet:</h3>
                    <img id="issuer-qr" class="qr-code" src="" alt="Issuer QR Code">
                    <p><small>Credential will be issued automatically when connected</small></p>
                </div>
                
                <div id="issuer-status"></div>
                
                <div id="issuer-steps" class="steps" style="display: none;">
                    <h4>📈 Issuer Steps:</h4>
                    <div id="issuer-step-1" class="step">1️⃣ Generate invitation</div>
                    <div id="issuer-step-2" class="step">2️⃣ Connect mobile wallet</div>
                    <div id="issuer-step-3" class="step">3️⃣ Issue credential</div>
                    <div id="issuer-step-4" class="step">4️⃣ Credential stored</div>
                </div>
            </div>
            
            <!-- Verifier Section -->
            <div class="section verifier-section">
                <h2>✅ Credential Verifier</h2>
                <p>Request proof of the User Identity credential.</p>
                
                <button onclick="startVerifierFlow()">🔍 Generate Verifier QR Code</button>
                
                <div id="verifier-qr-container" class="qr-container" style="display: none;">
                    <h3>📱 Scan with Aries Bifold wallet:</h3>
                    <img id="verifier-qr" class="qr-code" src="" alt="Verifier QR Code">
                    <p><small>Present your credential when prompted</small></p>
                </div>
                
                <div id="verifier-status"></div>
                
                <div id="verifier-steps" class="steps" style="display: none;">
                    <h4>🔍 Verifier Steps:</h4>
                    <div id="verifier-step-1" class="step">1️⃣ Generate invitation</div>
                    <div id="verifier-step-2" class="step">2️⃣ Connect mobile wallet</div>
                    <div id="verifier-step-3" class="step">3️⃣ Send proof request</div>
                    <div id="verifier-step-4" class="step">4️⃣ Verify proof</div>
                    <div id="verifier-step-5" class="step">5️⃣ Display results</div>
                </div>
                
                <div id="proof-results" style="display: none;">
                    <h4>🎉 Verification Results:</h4>
                    <div id="proof-data"></div>
                </div>
            </div>
        </div>

        <script>
            let issuerConnectionId = null;
            let verifierConnectionId = null;
            let credDefId = null;
            
            function showStatus(elementId, message, type = 'warning') {
                const element = document.getElementById(elementId);
                element.innerHTML = `<div class="status ${type}">${message}</div>`;
            }
            
            function updateStep(stepId, completed = false, current = false) {
                const step = document.getElementById(stepId);
                step.className = 'step';
                if (completed) step.className += ' completed';
                if (current) step.className += ' current';
            }
            
            function validateForm() {
                const username = document.getElementById('username').value.trim();
                const email = document.getElementById('email').value.trim();
                const occupation = document.getElementById('occupation').value.trim();
                const citizenship = document.getElementById('citizenship').value.trim();
                
                if (!username || !email || !occupation || !citizenship) {
                    showStatus('issuer-status', '❌ Please fill in all fields', 'error');
                    return null;
                }
                
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    showStatus('issuer-status', '❌ Please enter a valid email', 'error');
                    return null;
                }
                
                return { username, email, occupation, citizenship };
            }
            
            async function startIssuerFlow() {
                const formData = validateForm();
                if (!formData) return;
                
                document.getElementById('issuer-steps').style.display = 'block';
                updateStep('issuer-step-1', false, true);
                
                try {
                    showStatus('issuer-status', '🔄 Creating invitation...', 'warning');
                    
                    const response = await fetch('/api/issuer/create-invitation', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(formData)
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        issuerConnectionId = data.connection_id;
                        credDefId = data.cred_def_id;
                        
                        document.getElementById('issuer-qr').src = `data:image/png;base64,${data.qr_code}`;
                        document.getElementById('issuer-qr-container').style.display = 'block';
                        
                        updateStep('issuer-step-1', true);
                        updateStep('issuer-step-2', false, true);
                        
                        showStatus('issuer-status', '✅ QR Code generated! Scan with your wallet.', 'success');
                        
                        pollIssuerConnection();
                    } else {
                        showStatus('issuer-status', `❌ Error: ${data.error}`, 'error');
                    }
                } catch (error) {
                    showStatus('issuer-status', `❌ Error: ${error.message}`, 'error');
                }
            }
            
            async function startVerifierFlow() {
                if (!credDefId) {
                    showStatus('verifier-status', '❌ Please complete issuer flow first', 'error');
                    return;
                }
                
                document.getElementById('verifier-steps').style.display = 'block';
                updateStep('verifier-step-1', false, true);
                
                try {
                    showStatus('verifier-status', '🔄 Creating invitation...', 'warning');
                    
                    const response = await fetch('/api/verifier/create-invitation', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({})
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        verifierConnectionId = data.connection_id;
                        
                        document.getElementById('verifier-qr').src = `data:image/png;base64,${data.qr_code}`;
                        document.getElementById('verifier-qr-container').style.display = 'block';
                        
                        updateStep('verifier-step-1', true);
                        updateStep('verifier-step-2', false, true);
                        
                        showStatus('verifier-status', '✅ QR Code generated! Scan with your wallet.', 'success');
                        
                        pollVerifierConnection();
                    } else {
                        showStatus('verifier-status', `❌ Error: ${data.error}`, 'error');
                    }
                } catch (error) {
                    showStatus('verifier-status', `❌ Error: ${error.message}`, 'error');
                }
            }
            
            async function pollIssuerConnection() {
                try {
                    const response = await fetch(`/api/issuer/status/${issuerConnectionId}`);
                    const data = await response.json();
                    
                    if (data.connected) {
                        updateStep('issuer-step-2', true);
                        updateStep('issuer-step-3', false, true);
                        showStatus('issuer-status', '🔄 Connected! Issuing credential...', 'warning');
                        
                        setTimeout(async () => {
                            const credResponse = await fetch(`/api/issuer/credential-status/${issuerConnectionId}`);
                            const credData = await credResponse.json();
                            
                            if (credData.issued) {
                                updateStep('issuer-step-3', true);
                                updateStep('issuer-step-4', true);
                                showStatus('issuer-status', '🎉 Credential issued successfully!', 'success');
                            } else {
                                setTimeout(pollIssuerConnection, 3000);
                            }
                        }, 3000);
                    } else {
                        showStatus('issuer-status', '⏳ Waiting for mobile wallet...', 'warning');
                        setTimeout(pollIssuerConnection, 3000);
                    }
                } catch (error) {
                    console.error('Error polling issuer:', error);
                    setTimeout(pollIssuerConnection, 3000);
                }
            }
            
            async function pollVerifierConnection() {
                try {
                    const response = await fetch(`/api/verifier/status/${verifierConnectionId}`);
                    const data = await response.json();
                    
                    if (data.connected) {
                        updateStep('verifier-step-2', true);
                        updateStep('verifier-step-3', false, true);
                        showStatus('verifier-status', '🔄 Connected! Sending proof request...', 'warning');
                        
                        setTimeout(async () => {
                            const proofResponse = await fetch(`/api/verifier/proof-status/${verifierConnectionId}`);
                            const proofData = await proofResponse.json();
                            
                            if (proofData.verified) {
                                updateStep('verifier-step-3', true);
                                updateStep('verifier-step-4', true);
                                updateStep('verifier-step-5', true);
                                showStatus('verifier-status', '🎉 Proof verified successfully!', 'success');
                                
                                document.getElementById('proof-results').style.display = 'block';
                                document.getElementById('proof-data').innerHTML = `
                                    <div class="status success">
                                        <h4>✅ Verified Attributes:</h4>
                                        <div class="attribute">
                                            <span class="attribute-name">👤 Username:</span>
                                            <span class="attribute-value">${proofData.attributes.username || 'N/A'}</span>
                                        </div>
                                        <div class="attribute">
                                            <span class="attribute-name">📧 Email:</span>
                                            <span class="attribute-value">${proofData.attributes.email || 'N/A'}</span>
                                        </div>
                                        <div class="attribute">
                                            <span class="attribute-name">💼 Occupation:</span>
                                            <span class="attribute-value">${proofData.attributes.occupation || 'N/A'}</span>
                                        </div>
                                        <div class="attribute">
                                            <span class="attribute-name">🌍 Citizenship:</span>
                                            <span class="attribute-value">${proofData.attributes.citizenship || 'N/A'}</span>
                                        </div>
                                    </div>
                                `;
                            } else if (proofData.requested) {
                                updateStep('verifier-step-3', true);
                                updateStep('verifier-step-4', false, true);
                                showStatus('verifier-status', '⏳ Proof request sent. Waiting...', 'warning');
                                setTimeout(pollVerifierConnection, 3000);
                            } else {
                                setTimeout(pollVerifierConnection, 3000);
                            }
                        }, 3000);
                    } else {
                        setTimeout(pollVerifierConnection, 3000);
                    }
                } catch (error) {
                    console.error('Error polling verifier:', error);
                    setTimeout(pollVerifierConnection, 3000);
                }
            }
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')
