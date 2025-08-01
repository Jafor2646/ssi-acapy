#!/usr/bin/env python3
"""
SSI Agent - Single agent acting as both issuer and verifier
This module contains the core SSI agent functionality for credential issuance and verification.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional
from aiohttp import ClientSession

logger = logging.getLogger(__name__)

class SSIAgent:
    """Single SSI Agent that can both issue and verify credentials"""
    
    def __init__(self, admin_url: str):
        self.admin_url = admin_url
        self.session: Optional[ClientSession] = None
        self.schema_id = None
        self.cred_def_id = None
        
    async def start_session(self):
        """Start HTTP session"""
        self.session = ClientSession()
        
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            
    async def admin_request(self, method: str, path: str, data: dict = None) -> dict:
        """Make request to agent admin API"""
        url = f"{self.admin_url}{path}"
        headers = {"Content-Type": "application/json"}
        
        try:
            async with self.session.request(method, url, json=data, headers=headers) as resp:
                response_text = await resp.text()
                logger.info(f"{method} {path} -> {resp.status}: {response_text[:200]}...")
                
                if resp.status == 200:
                    if response_text:
                        try:
                            return json.loads(response_text)
                        except json.JSONDecodeError:
                            return {"success": True, "response": response_text}
                    else:
                        return {"success": True}
                else:
                    logger.error(f"Admin API error: {resp.status} - {response_text}")
                    return {"error": f"Status {resp.status}: {response_text}"}
        except Exception as e:
            logger.error(f"Admin API request failed: {str(e)}")
            return {"error": str(e)}
    
    async def setup_schema_and_cred_def(self):
        """Setup schema and credential definition for user identity"""
        try:
            # Get public DID
            dids_result = await self.admin_request("GET", "/wallet/did/public")
            if "result" not in dids_result:
                logger.error("Failed to get public DID")
                return False
                
            public_did = dids_result["result"]["did"]
            logger.info(f"Using public DID: {public_did}")
            
            # Create fresh UserIdentity schema and credential definition
            schema_data = {
                "schema_name": "UserIdentityCredential",
                "schema_version": "1.0", 
                "attributes": ["username", "email", "occupation", "citizenship"]
            }
            
            logger.info("Creating UserIdentity schema...")
            schema_result = await self.admin_request("POST", "/schemas", schema_data)
            
            # Handle existing schema
            if 'error' in schema_result and 'already exists' in str(schema_result['error']):
                logger.info("UserIdentity schema already exists, fetching existing schema...")
                schemas_result = await self.admin_request("GET", "/schemas/created")
                if "schema_ids" in schemas_result:
                    for schema_id in schemas_result["schema_ids"]:
                        if "UserIdentityCredential" in schema_id and "1.0" in schema_id:
                            self.schema_id = schema_id
                            logger.info(f"Using existing UserIdentity schema: {self.schema_id}")
                            break
                    
                    if not self.schema_id:
                        logger.error("Could not find existing UserIdentityCredential schema")
                        return False
                else:
                    logger.error("Could not fetch existing schemas")
                    return False
            elif "schema_id" in schema_result:
                self.schema_id = schema_result["schema_id"]
                logger.info(f"UserIdentity schema created: {self.schema_id}")
            else:
                logger.error(f"Failed to create UserIdentity schema: {schema_result}")
                return False
                
            # Wait for schema to be available
            await asyncio.sleep(2)
            
            # Create credential definition
            cred_def_data = {
                "schema_id": self.schema_id,
                "tag": "UserIdentity"
            }
            
            logger.info("Creating UserIdentity credential definition...")
            cred_def_result = await self.admin_request("POST", "/credential-definitions", cred_def_data)
            
            # Handle existing cred def
            if 'error' in cred_def_result and 'already exists' in str(cred_def_result['error']):
                logger.info("UserIdentity credential definition already exists, fetching existing cred def...")
                cred_defs_result = await self.admin_request("GET", "/credential-definitions/created")
                if "credential_definition_ids" in cred_defs_result:
                    for cred_def_id in cred_defs_result["credential_definition_ids"]:
                        if "UserIdentity" in cred_def_id:
                            self.cred_def_id = cred_def_id
                            logger.info(f"Using existing UserIdentity credential definition: {self.cred_def_id}")
                            break
                    
                    if not self.cred_def_id:
                        # If no UserIdentity tag found, look for schema-based match 
                        schema_parts = self.schema_id.split(":")
                        schema_seq_no = schema_parts[2] if len(schema_parts) > 2 else None
                        
                        if schema_seq_no:
                            for cred_def_id in cred_defs_result["credential_definition_ids"]:
                                if f":CL:{schema_seq_no}:" in cred_def_id:
                                    self.cred_def_id = cred_def_id
                                    logger.info(f"Using UserIdentity credential definition for schema {schema_seq_no}: {self.cred_def_id}")
                                    break
                        
                        if not self.cred_def_id:
                            logger.error("Could not find existing UserIdentity credential definition")
                            return False
                else:
                    logger.error("Could not fetch existing credential definitions")
                    return False
            elif "credential_definition_id" in cred_def_result:
                self.cred_def_id = cred_def_result["credential_definition_id"]
                logger.info(f"UserIdentity credential definition created: {self.cred_def_id}")
            else:
                logger.error(f"Failed to create UserIdentity credential definition: {cred_def_result}")
                return False
                
            # Verify credential definition is accessible
            verify_result = await self.admin_request("GET", f"/credential-definitions/{self.cred_def_id}")
            if "error" not in verify_result:
                logger.info(f"✅ Verified UserIdentity credential definition is accessible")
                return True
            else:
                logger.error(f"❌ UserIdentity credential definition verification failed: {verify_result}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up UserIdentity schema and cred def: {str(e)}")
            return False
    
    async def create_invitation(self, purpose: str = "general") -> dict:
        """Create connection invitation"""
        unique_suffix = str(uuid.uuid4())[:8]
        
        invitation_data = {
            "alias": f"SSI_Agent_{purpose}_{unique_suffix}",
            "my_label": f"SSI Agent - {purpose.title()}",
            "auto_accept": True
        }
        
        result = await self.admin_request("POST", "/connections/create-invitation", invitation_data)
        return result
        
    async def issue_credential(self, connection_id: str, attributes: dict) -> dict:
        """Issue credential using UserIdentity schema"""
        
        credential_data = {
            "connection_id": connection_id,
            "cred_def_id": self.cred_def_id,
            "credential_proposal": {
                "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
                "attributes": [
                    {"name": "username", "value": str(attributes.get("username", "user123"))},
                    {"name": "email", "value": str(attributes.get("email", "user@email.com"))},
                    {"name": "occupation", "value": str(attributes.get("occupation", "Software Engineer"))},
                    {"name": "citizenship", "value": str(attributes.get("citizenship", "USA"))}
                ]
            },
            "auto_remove": False,
            "comment": "Your UserIdentity Credential",
            "trace": False
        }
        
        logger.info(f"Issuing credential with UserIdentity schema: {credential_data}")
        result = await self.admin_request("POST", "/issue-credential/send", credential_data)
        return result
        
    async def request_proof(self, connection_id: str) -> dict:
        """Request proof from holder using UserIdentity schema attributes"""
        
        proof_request_data = {
            "connection_id": connection_id,
            "proof_request": {
                "name": "UserIdentity Verification", 
                "version": "1.0",
                "nonce": str(uuid.uuid4().int),
                "requested_attributes": {
                    "username_referent": {
                        "name": "username",
                        "restrictions": [{"cred_def_id": self.cred_def_id}]
                    },
                    "email_referent": {
                        "name": "email", 
                        "restrictions": [{"cred_def_id": self.cred_def_id}]
                    },
                    "occupation_referent": {
                        "name": "occupation",
                        "restrictions": [{"cred_def_id": self.cred_def_id}]
                    },
                    "citizenship_referent": {
                        "name": "citizenship",
                        "restrictions": [{"cred_def_id": self.cred_def_id}]
                    }
                },
                "requested_predicates": {}
            },
            "auto_verify": True,
            "comment": "Please provide proof of your UserIdentity credentials",
            "trace": False
        }
        
        logger.info(f"Requesting proof with data: {proof_request_data}")
        result = await self.admin_request("POST", "/present-proof/send-request", proof_request_data)
        return result
