#!/bin/bash

echo "🚀 Starting SSI Demo using sudo + run_demo (Direct Method)"
echo "==========================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if we're in the correct directory
if [ ! -d "acapy" ] || [ ! -d "ssi-demo-app" ]; then
    echo -e "${RED}❌ Please run this script from the SSI_New directory${NC}"
    exit 1
fi

echo -e "${BLUE}📋 This demo will issue credentials with these exact attributes:${NC}"
echo -e "   • ${GREEN}username${NC} - User's chosen identifier"
echo -e "   • ${GREEN}email${NC} - User's email address"  
echo -e "   • ${GREEN}occupation${NC} - User's job title or profession"
echo -e "   • ${GREEN}citizenship${NC} - User's nationality"
echo ""

# Configuration
LEDGER_URL="http://dev.greenlight.bcovrin.vonx.io"

# Check if ngrok is available
NGROK_AVAILABLE=false
if command -v ngrok &> /dev/null; then
    NGROK_AVAILABLE=true
    echo -e "${GREEN}✅ ngrok detected${NC}"
else
    echo -e "${YELLOW}⚠️  ngrok not found - install with: snap install ngrok${NC}"
fi

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping agents...${NC}"
    
    # Kill any running processes
    sudo pkill -f "run_demo" 2>/dev/null || true
    pkill -f "ngrok http" 2>/dev/null || true
    
    # Stop any docker containers (using --bg creates containers named faber/alice)
    sudo docker stop faber alice 2>/dev/null || true
    sudo docker rm faber alice 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set trap for cleanup on script exit
trap cleanup EXIT INT TERM

# Function to start issuer (faber)
start_issuer() {
    echo -e "${YELLOW}🏭 Starting Issuer Agent (Faber)...${NC}"
    
    if [ "$NGROK_AVAILABLE" = true ]; then
        # Start ngrok for external endpoint
        echo -e "${BLUE}🌐 Starting ngrok for external endpoint...${NC}"
        ngrok http 8020 --log stdout > /tmp/ngrok_issuer.log 2>&1 &
        NGROK_PID=$!
        
        # Wait for ngrok to start
        sleep 5
        
        # Get ngrok URL
        ISSUER_ENDPOINT=$(curl -s http://localhost:4040/api/tunnels | grep -o "https://[^\"]*\.ngrok-free\.app" | head -1)
        
        if [ -z "$ISSUER_ENDPOINT" ]; then
            echo -e "${YELLOW}⚠️  Could not get ngrok URL, using localhost${NC}"
            ISSUER_ENDPOINT="http://localhost:8020"
        else
            echo -e "${GREEN}🌐 Issuer endpoint: $ISSUER_ENDPOINT${NC}"
        fi
    else
        ISSUER_ENDPOINT="http://localhost:8020"
    fi
    
    echo -e "${BLUE}📍 Starting Faber with endpoint: $ISSUER_ENDPOINT${NC}"
    
    # Use sudo with the exact command pattern that worked
    cd acapy
    sudo LEDGER_URL="$LEDGER_URL" AGENT_ENDPOINT="$ISSUER_ENDPOINT" \
        ./demo/run_demo run faber --bg &
    
    FABER_PID=$!
    echo -e "${GREEN}✅ Faber started (PID: $FABER_PID)${NC}"
    cd ..
}

# Function to start verifier (alice) 
start_verifier() {
    echo -e "${YELLOW}🔍 Starting Verifier Agent (Alice)...${NC}"
    
    # Alice uses localhost endpoint
    VERIFIER_ENDPOINT="http://localhost:8030"
    
    echo -e "${BLUE}📍 Starting Alice with endpoint: $VERIFIER_ENDPOINT${NC}"
    
    # Use sudo with the exact command pattern
    cd acapy
    sudo LEDGER_URL="$LEDGER_URL" AGENT_ENDPOINT="$VERIFIER_ENDPOINT" \
        ./demo/run_demo run alice --bg &
    
    ALICE_PID=$!
    echo -e "${GREEN}✅ Alice started (PID: $ALICE_PID)${NC}"
    cd ..
}

# Start agents sequentially
start_issuer
echo -e "${BLUE}⏳ Waiting for Faber to initialize...${NC}"
sleep 15

start_verifier
echo -e "${BLUE}⏳ Waiting for Alice to initialize...${NC}"
sleep 15

echo ""
echo -e "${GREEN}🎉 SSI Demo Started Successfully!${NC}"
echo "=================================="
echo ""

# Test if agents are responding
echo -e "${BLUE}🔍 Testing agent connectivity...${NC}"

# Test Faber
if curl -s -f http://localhost:8021/status > /dev/null 2>&1; then
    echo -e "• Issuer (Faber): ${GREEN}✅ Responding on port 8021${NC}"
else
    echo -e "• Issuer (Faber): ${RED}❌ Not responding on port 8021${NC}"
fi

# Test Alice
if curl -s -f http://localhost:8031/status > /dev/null 2>&1; then
    echo -e "• Verifier (Alice): ${GREEN}✅ Responding on port 8031${NC}"
else
    echo -e "• Verifier (Alice): ${RED}❌ Not responding on port 8031${NC}"
fi

echo -e "• Ledger: ${GREEN}$LEDGER_URL${NC}"

if [ "$NGROK_AVAILABLE" = true ] && [ ! -z "$ISSUER_ENDPOINT" ] && [[ "$ISSUER_ENDPOINT" == *"ngrok"* ]]; then
    echo -e "• External Endpoint: ${GREEN}$ISSUER_ENDPOINT${NC}"
else
    echo -e "• External Endpoint: ${YELLOW}localhost only${NC}"
fi

echo ""
echo -e "${BLUE}📱 Next Steps:${NC}"
echo -e "1. Run full test: ${YELLOW}./test-new-setup.sh${NC}"
echo -e "2. Start web app: ${YELLOW}cd ssi-demo-app && python3 app.py${NC}"
echo -e "3. Open ${GREEN}http://localhost:8080${NC} in browser"
echo -e "4. Use Aries Bifold mobile app to scan QR codes"
echo ""
echo -e "${YELLOW}⏳ Agents running... Press Ctrl+C to stop${NC}"

# Keep running with periodic health checks
while true; do
    sleep 30
    echo -e "${BLUE}💓 Health check - $(date '+%H:%M:%S')${NC}"
    
    # Quick health check
    if curl -s -f http://localhost:8021/status > /dev/null 2>&1; then
        echo -e "  • Faber: ${GREEN}✅${NC}"
    else
        echo -e "  • Faber: ${RED}❌${NC}"
    fi
    
    if curl -s -f http://localhost:8031/status > /dev/null 2>&1; then
        echo -e "  • Alice: ${GREEN}✅${NC}"
    else
        echo -e "  • Alice: ${RED}❌${NC}"
    fi
done
