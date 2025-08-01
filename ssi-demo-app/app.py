#!/usr/bin/env python3
"""
SSI Demo Application - Main Entry Point
Single agent acting as both issuer and verifier with minimal SSI steps.
Uses the working issuer logic from the original implementation.
"""

import asyncio
import logging
import aiohttp_cors
from aiohttp import web
from aiohttp.web import Application

# Import our modules
from src.backend.ssi_agent import SSIAgent
from src.backend.api_routes import routes
from src.templates.templates import index_page

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_agent(app: Application):
    """Initialize the SSI agent"""
    try:
        # Use single agent on port 8021 (same as working Faber issuer)
        agent = SSIAgent("http://localhost:8021")
        
        # Start HTTP session
        await agent.start_session()
        
        # Setup schema and credential definition
        logger.info("Setting up schema and credential definition...")
        setup_success = await agent.setup_schema_and_cred_def()
        
        if setup_success:
            logger.info("✅ Agent setup completed successfully")
            logger.info(f"📋 Schema ID: {agent.schema_id}")
            logger.info(f"🔑 Credential Definition ID: {agent.cred_def_id}")
        else:
            logger.error("❌ Failed to setup agent")
            logger.error("💡 Make sure ACA-Py agent is running on http://localhost:8021")
        
        # Store agent in app for use in routes
        app["ssi_agent"] = agent
        
        return setup_success
        
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}")
        return False

async def cleanup_agent(app: Application):
    """Cleanup agent session"""
    try:
        agent = app.get("ssi_agent")
        if agent:
            await agent.close_session()
            logger.info("Agent session closed")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

async def create_app() -> Application:
    """Create and configure the web application"""
    app = Application()
    
    # Add main page route
    app.router.add_get('/', index_page)
    
    # Add API routes
    app.router.add_routes(routes)
    
    # Setup CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Add CORS to all routes
    for route in list(app.router.routes()):
        cors.add(route)
    
    # Setup startup and cleanup
    app.on_startup.append(init_agent)
    app.on_cleanup.append(cleanup_agent)
    
    return app

def main():
    """Main entry point"""
    logger.info("🚀 Starting SSI Demo Application...")
    logger.info("📋 Single Agent - Issuer & Verifier")
    logger.info("🌐 Web interface: http://localhost:8080")
    logger.info("📱 Make sure your Aries Bifold wallet is ready!")
    logger.info("🔧 Make sure ACA-Py agent is running on port 8021")
    
    # Create application
    app = create_app()
    
    # Run the web server
    web.run_app(app, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
