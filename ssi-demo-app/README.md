# SSI Demo Application - Self-Sovereign Identity Credential System

A comprehensive Self-Sovereign Identity (SSI) demonstration application that showcases digital credential issuance and verification using Hyperledger Aries Cloud Agent Python (ACA-Py) and mobile wallet integration.

![SSI Demo](https://img.shields.io/badge/SSI-Demo-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![ACA-Py](https://img.shields.io/badge/ACA--Py-0.12.3-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 🎯 Overview

This application demonstrates a complete SSI workflow where a single ACA-Py agent acts as both **credential issuer** and **verifier**. Users can:

- **Issue UserIdentity credentials** containing username, email, occupation, and citizenship
- **Verify credentials** through cryptographic proof requests
- **Mobile wallet integration** using Aries Bifold wallet
- **Real-time QR code generation** for secure connections

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   SSI Demo App  │    │   ACA-Py Agent  │
│   (localhost:   │◄──►│   (Port 8080)   │◄──►│   (Port 8021)   │
│      8080)      │    │                 │    │    (Faber)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │ QR Code Scanning      │ ngrok tunnel
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Aries Bifold    │    │ External Access │
                       │ Mobile Wallet   │    │ (Mobile Wallet) │
                       └─────────────────┘    └─────────────────┘
```

### System Components

1. **SSI Demo Application** (`app.py`): Web interface for credential operations
2. **SSI Agent** (`src/backend/ssi_agent.py`): Core SSI functionality
3. **API Routes** (`src/backend/api_routes.py`): REST API endpoints
4. **Templates** (`src/templates/templates.py`): HTML user interface
5. **ACA-Py Agent**: Hyperledger Aries agent (Faber configuration)

## 🔑 Features

### Credential Management
- **UserIdentity Schema**: Contains username, email, occupation, citizenship
- **Automatic Issuance**: Credentials issued upon wallet connection
- **Secure Storage**: Credentials stored in Aries Bifold wallet
- **Real-time Status**: Live updates on credential states

### Proof Verification
- **Zero-Knowledge Proofs**: Verify credentials without exposing raw data
- **Selective Disclosure**: Request specific attributes only
- **Cryptographic Verification**: Ensure credential authenticity
- **Instant Results**: Real-time verification status

### Technical Features
- **Single Agent Architecture**: One agent handles both issuing and verification
- **QR Code Generation**: Dynamic QR codes for mobile wallet connections
- **ngrok Integration**: External access for mobile wallets
- **WebSocket Updates**: Real-time status updates
- **Error Handling**: Comprehensive error handling and logging

## 📋 Prerequisites

### Required Software

1. **Python 3.8+**
2. **ACA-Py (Aries Cloud Agent Python)**
3. **ngrok** (for mobile wallet connectivity)
4. **von-network** (local Indy ledger for development)

### Mobile Wallet

- **Aries Bifold** mobile wallet app (iOS/Android)

## 🚀 Installation & Setup

### Step 1: Clone and Setup von-network (Local Ledger)

```bash
# Clone von-network for local Indy ledger
git clone https://github.com/bcgov/von-network.git
cd von-network

# Build and start the local ledger
./manage build
./manage start --logs

# Verify ledger is running at http://localhost:9000
```

### Step 2: Install ngrok (for mobile connectivity)

```bash
# Ubuntu/Debian
sudo snap install ngrok

# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

### Step 3: Start ACA-Py Agent

The project includes a script that starts both Faber and Alice agents, but our demo uses only the **Faber agent** (port 8021) as a single agent for both issuing and verifying:

```bash
# From the main SSI_New directory
./start-working-demo.sh
```

This script will:
- Start the **Faber agent** on port 8021 (admin) and 8020 (endpoint) - **Used by our demo**
- Start the Alice agent on port 8031 (admin) and 8030 (endpoint) - Not used in this demo
- Configure ngrok for external access
- Set up proper ledger connections
- Display connection status

**Note**: Our SSI demo application connects only to the Faber agent (port 8021) which handles both credential issuance and verification.

**Manual ACA-Py Setup (Alternative):**

```bash
# Install ACA-Py
pip install aries-cloudagent[indy]

# Start the agent manually
aca-py start \
  --inbound-transport http 0.0.0.0 8020 \
  --outbound-transport http \
  --admin 0.0.0.0 8021 \
  --admin-insecure-mode \
  --genesis-url http://localhost:9000/genesis \
  --seed 000000000000000000000000Trustee1 \
  --endpoint http://localhost:8020 \
  --label "SSI Demo Agent" \
  --public-invites \
  --auto-provision \
  --wallet-type indy \
  --wallet-name demo_wallet \
  --wallet-key demo_key \
  --auto-ping-connection \
  --auto-respond-messages \
  --auto-accept-invites \
  --auto-accept-requests
```

### Step 4: Install Demo Application

```bash
# Navigate to the demo application directory
cd ssi-demo-app

# Install Python dependencies
pip install -r requirements.txt
```

### Step 5: Run the Demo Application

```bash
# Start the SSI demo application
python3 app.py
```

The application will start on `http://localhost:8080`

## 📱 Usage Guide

### Complete SSI Workflow Demonstration

#### 1. Preparation

1. **Start the infrastructure:**
   ```bash
   # Terminal 1: Start von-network ledger
   cd von-network && ./manage start --logs
   
   # Terminal 2: Start ACA-Py agent
   cd SSI_New && ./start-working-demo.sh
   
   # Terminal 3: Start demo application
   cd ssi-demo-app && python3 app.py
   ```

2. **Install Aries Bifold** on your mobile device
   - iOS: Search "Aries Bifold" in App Store
   - Android: Search "Aries Bifold" in Google Play Store

3. **Open the demo application** at `http://localhost:8080`

#### 2. Credential Issuance Process

1. **Fill out the credential form:**
   - **Username**: Your chosen identifier (e.g., "john_doe")
   - **Email**: Your email address (e.g., "john@example.com")
   - **Occupation**: Your job title (e.g., "Software Engineer")
   - **Citizenship**: Your nationality (e.g., "United States")

2. **Generate issuer connection:**
   - Click **"Generate Issuer QR Code"**
   - A QR code will appear on the screen

3. **Connect with mobile wallet:**
   - Open Aries Bifold on your mobile device
   - Tap the "Scan" button
   - Scan the QR code displayed in the web browser
   - Accept the connection in your wallet

4. **Credential issuance:**
   - The credential will be automatically issued once connected
   - Accept the credential in your Aries Bifold wallet
   - The credential is now stored securely in your wallet

#### 3. Credential Verification Process

1. **Start verification:**
   - Click **"Generate Verifier QR Code"** in the web interface
   - A new QR code will appear

2. **Connect for verification:**
   - Scan the verifier QR code with your Aries Bifold wallet
   - Accept the new connection

3. **Proof request:**
   - A proof request will be automatically sent to your wallet
   - Your wallet will ask which credential to use for the proof

4. **Present proof:**
   - Select the UserIdentity credential in your wallet
   - Choose which attributes to share (username, email, occupation, citizenship)
   - Submit the proof

5. **Verification results:**
   - The web interface will display the verified attributes
   - Confirmation that the proof is cryptographically valid

### Understanding the Process States

#### Connection States
- **`invitation`**: QR code generated, waiting for wallet scan
- **`request`**: Wallet scanned QR code, sending connection request
- **`response`**: Connection established, exchanging keys
- **`active`**: Connection fully established ✅

#### Credential States
- **`offer_sent`**: Credential offer sent to wallet
- **`request_received`**: Wallet requested the credential
- **`credential_issued`**: Credential issued by agent
- **`credential_acked`**: Credential accepted and stored in wallet ✅

#### Proof States
- **`request_sent`**: Proof request sent to wallet
- **`presentation_received`**: Wallet submitted proof
- **`verified`**: Proof cryptographically verified ✅

## 🔧 Implementation Details

### Project Structure

```
ssi-demo-app/
├── app.py                          # Main application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This documentation
└── src/
    ├── backend/
    │   ├── ssi_agent.py           # Core SSI agent functionality
    │   └── api_routes.py          # Web API endpoints
    └── templates/
        └── templates.py           # HTML user interface
```

### Core Components

#### 1. SSI Agent (`src/backend/ssi_agent.py`)
```python
class SSIAgent:
    """Single SSI Agent handling both issuer and verifier roles"""
    
    async def setup_schema_and_cred_def(self):
        """Create UserIdentity schema and credential definition"""
        
    async def issue_credential(self, connection_id: str, attributes: dict):
        """Issue UserIdentity credential to connected wallet"""
        
    async def request_proof(self, connection_id: str):
        """Request proof of UserIdentity attributes"""
```

#### 2. API Routes (`src/backend/api_routes.py`)
- `POST /api/issuer/create-invitation` - Create issuer connection
- `GET /api/issuer/status/{connection_id}` - Check connection status
- `GET /api/issuer/credential-status/{connection_id}` - Check credential status
- `POST /api/verifier/create-invitation` - Create verifier connection
- `GET /api/verifier/proof-status/{connection_id}` - Check proof status

#### 3. User Interface (`src/templates/templates.py`)
- Responsive web interface with real-time updates
- QR code display for mobile wallet connections
- Step-by-step process visualization
- Real-time status monitoring

### Schema Definition

The UserIdentity credential schema contains exactly four attributes:

```json
{
  "schema_name": "UserIdentityCredential",
  "schema_version": "1.0",
  "attributes": [
    "username",    // User's chosen identifier
    "email",       // User's email address
    "occupation",  // User's job title or profession
    "citizenship"  // User's nationality
  ]
}
```

### Security Features

#### Cryptographic Security
- **Digital Signatures**: All credentials are cryptographically signed
- **Zero-Knowledge Proofs**: Verify attributes without revealing the full credential
- **Schema Validation**: Credentials conform to predefined schemas
- **Tamper Protection**: Any modification invalidates the credential

#### Privacy Protection
- **Selective Disclosure**: Share only requested attributes
- **Minimal Disclosure**: Only necessary information is revealed
- **Unlinkability**: Different proof presentations cannot be correlated
- **Data Sovereignty**: Users control their own credentials

## 🛠️ Development

### Adding New Credential Types

1. **Modify the schema** in `src/backend/ssi_agent.py`:
```python
schema_data = {
    "schema_name": "YourNewCredential",
    "schema_version": "1.0",
    "attributes": ["attr1", "attr2", "attr3"]
}
```

2. **Update the issuance logic** in `issue_credential()` method
3. **Update the verification logic** in `request_proof()` method
4. **Modify the web interface** in `src/templates/templates.py`

### Customizing the Interface

- **HTML/CSS**: Modify `src/templates/templates.py`
- **API endpoints**: Add new routes in `src/backend/api_routes.py`
- **Business logic**: Extend `src/backend/ssi_agent.py`

### Testing

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test full workflow
3. **Mobile Testing**: Test with different wallet apps
4. **Network Testing**: Test with external ledgers

## 🔍 Troubleshooting

### Common Issues

#### Agent Connection Problems
```bash
# Check if ACA-Py is running
curl http://localhost:8021/status

# Check agent logs
tail -f /path/to/agent/logs
```

#### Mobile Wallet Issues
- Ensure mobile device is on the same network
- Check ngrok tunnel status
- Verify QR code is properly generated
- Try force refresh in wallet app

#### Credential Issuance Problems
- Verify schema and credential definition are created
- Check connection state is "active"
- Review agent logs for errors
- Ensure wallet accepts credential offers

#### Proof Verification Issues
- Confirm credential exists in wallet
- Check proof request format
- Verify credential definition matches
- Review verification logs

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Log Analysis

Monitor application logs for:
- Connection state changes
- Credential exchange states
- Proof verification results
- Error messages and stack traces

## 🌟 Advanced Features

### Custom Workflows

The application can be extended to support:

- **Multi-step verification**: Chain multiple proof requests
- **Conditional issuance**: Issue credentials based on existing proofs
- **Batch operations**: Handle multiple credentials simultaneously
- **Custom schemas**: Define domain-specific credential types

### Integration Options

- **Database integration**: Store transaction history
- **API integration**: Connect to external systems
- **Webhook support**: Real-time notifications
- **Analytics dashboard**: Usage metrics and insights

## 📖 Standards and Protocols

This implementation follows industry standards:

- **W3C Verifiable Credentials**: Standard for digital credentials
- **DID (Decentralized Identifiers)**: For agent identification
- **Aries RFCs**: Hyperledger Aries protocol specifications
- **AnonCreds**: Anonymous credentials specification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hyperledger Aries** community for the ACA-Py agent
- **BC Gov** for von-network and Aries Bifold wallet
- **W3C** for Verifiable Credentials standards
- **OpenWallet Foundation** for advancing digital wallet technologies

## 📞 Support

For questions, issues, or contributions:

1. **GitHub Issues**: Report bugs and feature requests
2. **Discussions**: Ask questions and share ideas
3. **Documentation**: Check the comprehensive guides
4. **Community**: Join the Hyperledger Aries community

---

**Built with ❤️ using Self-Sovereign Identity principles and open-source technologies**
