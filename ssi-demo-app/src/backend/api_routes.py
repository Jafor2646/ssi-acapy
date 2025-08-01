#!/usr/bin/env python3
"""
API Routes for SSI Demo Application
This module contains all the web API endpoints for the SSI demo.
"""

import json
import logging
import urllib.parse
import qrcode
from io import BytesIO
import base64
from datetime import datetime
from aiohttp import web
from aiohttp.web import Request, Response, RouteTableDef

logger = logging.getLogger(__name__)
routes = RouteTableDef()

# Global state
app_state = {
    "connections": {},
    "pending_attributes": {}
}

def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 string"""
    try:
        # If data is already a URL, use it directly
        if data.startswith('http'):
            qr_data = data
        else:
            # If it's JSON invitation data, try to parse and format properly
            try:
                invitation_json = json.loads(data) if isinstance(data, str) else data
                encoded_invitation = urllib.parse.quote(json.dumps(invitation_json))
                qr_data = f"https://didcomm.org/out-of-band/?oob={encoded_invitation}"
            except (json.JSONDecodeError, TypeError):
                qr_data = str(data)
        
        logger.info(f"Generating QR code for: {qr_data[:100]}...")
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=5
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
        
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"Error: {str(e)}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode()

@routes.post('/api/issuer/create-invitation')
async def api_issuer_create_invitation(request: Request) -> Response:
    """Create issuer connection invitation"""
    try:
        data = await request.json()
        
        # Store the credential attributes for later use
        app_state["pending_attributes"] = {
            "username": data.get("username", ""),
            "email": data.get("email", ""),
            "occupation": data.get("occupation", ""),
            "citizenship": data.get("citizenship", "")
        }
        
        # Get the agent from the app
        agent = request.app["ssi_agent"]
        
        # Create invitation
        invitation_result = await agent.create_invitation("issuer")
        logger.info(f"Invitation result: {invitation_result}")
        
        if "invitation" in invitation_result and "connection_id" in invitation_result:
            connection_id = invitation_result["connection_id"]
            invitation = invitation_result["invitation"]
            
            # Generate QR code from invitation
            qr_data = None
            
            if "invitation_url" in invitation_result:
                qr_data = invitation_result["invitation_url"]
                logger.info(f"Using invitation_url: {qr_data}")
            elif "invitation_url" in invitation:
                qr_data = invitation["invitation_url"]
                logger.info(f"Using invitation.invitation_url: {qr_data}")
            else:
                try:
                    invitation_json = json.dumps(invitation)
                    encoded_invitation = urllib.parse.quote(invitation_json)
                    qr_data = f"https://didcomm.org/out-of-band/?oob={encoded_invitation}"
                    logger.info(f"Created invitation URL from object: {qr_data[:100]}...")
                except Exception as e:
                    logger.error(f"Error creating invitation URL: {e}")
                    qr_data = json.dumps(invitation)
            
            if not qr_data:
                logger.error("No valid QR data found")
                return web.json_response({
                    "success": False,
                    "error": "Failed to generate QR code data"
                })
            
            try:
                qr_code = generate_qr_code(qr_data)
            except Exception as e:
                logger.error(f"QR code generation failed: {e}")
                return web.json_response({
                    "success": False,
                    "error": f"QR code generation failed: {str(e)}"
                })
            
            # Store connection info
            app_state["connections"][connection_id] = {
                "type": "issuer",
                "status": "invitation_sent",
                "attributes": app_state["pending_attributes"].copy(),
                "created_at": datetime.now().isoformat(),
                "invitation": invitation
            }
            
            return web.json_response({
                "success": True,
                "connection_id": connection_id,
                "qr_code": qr_code,
                "cred_def_id": agent.cred_def_id,
                "invitation_data": qr_data[:200] + "..." if len(str(qr_data)) > 200 else str(qr_data)
            })
        else:
            logger.error(f"Invalid invitation result: {invitation_result}")
            return web.json_response({
                "success": False,
                "error": f"Failed to create invitation: {invitation_result.get('error', 'Unknown error')}"
            })
            
    except Exception as e:
        logger.error(f"Error creating issuer invitation: {str(e)}")
        return web.json_response({
            "success": False,
            "error": str(e)
        })

@routes.post('/api/verifier/create-invitation')
async def api_verifier_create_invitation(request: Request) -> Response:
    """Create verifier connection invitation"""
    try:
        # Get the agent from the app
        agent = request.app["ssi_agent"]
        
        if not agent.cred_def_id:
            return web.json_response({
                "success": False,
                "error": "No credential definition available. Please issue a credential first."
            })
        
        # Create invitation
        invitation_result = await agent.create_invitation("verifier")
        logger.info(f"Verifier invitation result: {invitation_result}")
        
        if "invitation" in invitation_result and "connection_id" in invitation_result:
            connection_id = invitation_result["connection_id"]
            invitation = invitation_result["invitation"]
            
            # Generate QR code from invitation
            qr_data = None
            
            if "invitation_url" in invitation_result:
                qr_data = invitation_result["invitation_url"]
                logger.info(f"Using verifier invitation_url: {qr_data}")
            elif "invitation_url" in invitation:
                qr_data = invitation["invitation_url"]
                logger.info(f"Using verifier invitation.invitation_url: {qr_data}")
            else:
                try:
                    invitation_json = json.dumps(invitation)
                    encoded_invitation = urllib.parse.quote(invitation_json)
                    qr_data = f"https://didcomm.org/out-of-band/?oob={encoded_invitation}"
                    logger.info(f"Created verifier invitation URL from object: {qr_data[:100]}...")
                except Exception as e:
                    logger.error(f"Error creating verifier invitation URL: {e}")
                    qr_data = json.dumps(invitation)
            
            if not qr_data:
                logger.error("No valid verifier QR data found")
                return web.json_response({
                    "success": False,
                    "error": "Failed to generate verifier QR code data"
                })
            
            try:
                qr_code = generate_qr_code(qr_data)
            except Exception as e:
                logger.error(f"Verifier QR code generation failed: {e}")
                return web.json_response({
                    "success": False,
                    "error": f"Verifier QR code generation failed: {str(e)}"
                })
            
            # Store connection info
            app_state["connections"][connection_id] = {
                "type": "verifier",
                "status": "invitation_sent",
                "cred_def_id": agent.cred_def_id,
                "created_at": datetime.now().isoformat(),
                "invitation": invitation
            }
            
            return web.json_response({
                "success": True,
                "connection_id": connection_id,
                "qr_code": qr_code,
                "cred_def_id": agent.cred_def_id,
                "invitation_data": qr_data[:200] + "..." if len(str(qr_data)) > 200 else str(qr_data)
            })
        else:
            logger.error(f"Invalid verifier invitation result: {invitation_result}")
            return web.json_response({
                "success": False,
                "error": f"Failed to create verifier invitation: {invitation_result.get('error', 'Unknown error')}"
            })
            
    except Exception as e:
        logger.error(f"Error creating verifier invitation: {str(e)}")
        return web.json_response({
            "success": False,
            "error": str(e)
        })

@routes.get('/api/issuer/status/{connection_id}')
async def api_issuer_status(request: Request) -> Response:
    """Get issuer connection status"""
    connection_id = request.match_info['connection_id']
    
    try:
        agent = request.app["ssi_agent"]
        
        # Check connection status
        connections_result = await agent.admin_request("GET", f"/connections/{connection_id}")
        
        if "error" in connections_result:
            return web.json_response({
                "connected": False,
                "error": connections_result["error"]
            })
        
        if "state" in connections_result:
            state = connections_result["state"]
            rfc23_state = connections_result.get("rfc23_state", "")
            
            logger.info(f"Connection {connection_id} state: {state}, rfc23_state: {rfc23_state}")
            
            # Connection is active when state is "active"
            is_connected = state == "active"
            # Mobile wallet interaction detected if state changed from initial invitation
            wallet_interacted = state != "invitation"
            
            if connection_id in app_state["connections"]:
                current_status = app_state["connections"][connection_id].get("status", "")
                app_state["connections"][connection_id]["status"] = state
                
                # Issue credential when connection becomes active and we haven't issued yet
                if state == "active" and "credential_issued" not in app_state["connections"][connection_id]:
                    attributes = app_state["connections"][connection_id].get("attributes", {})
                    
                    logger.info(f"Auto-issuing credential for connection {connection_id} (state: {state})")
                    try:
                        credential_result = await agent.issue_credential(connection_id, attributes)
                        
                        if "credential_exchange_id" in credential_result:
                            app_state["connections"][connection_id]["credential_issued"] = True
                            app_state["connections"][connection_id]["credential_exchange_id"] = credential_result["credential_exchange_id"]
                            logger.info(f"Credential auto-issued successfully: {credential_result['credential_exchange_id']}")
                        else:
                            logger.error(f"Failed to auto-issue credential: {credential_result}")
                            
                    except Exception as cred_error:
                        logger.error(f"Error auto-issuing credential: {str(cred_error)}")
            
            return web.json_response({
                "connected": is_connected,
                "state": state,
                "rfc23_state": rfc23_state,
                "wallet_interacted": wallet_interacted
            })
        else:
            return web.json_response({
                "connected": False,
                "error": f"Failed to get connection status: {connections_result}"
            })
            
    except Exception as e:
        logger.error(f"Error checking issuer status: {str(e)}")
        return web.json_response({
            "connected": False,
            "error": str(e)
        })

@routes.get('/api/verifier/status/{connection_id}')
async def api_verifier_status(request: Request) -> Response:
    """Get verifier connection status"""
    connection_id = request.match_info['connection_id']
    
    try:
        agent = request.app["ssi_agent"]
        
        # Check connection status
        connections_result = await agent.admin_request("GET", f"/connections/{connection_id}")
        
        if "error" in connections_result:
            return web.json_response({
                "connected": False,
                "error": connections_result["error"]
            })
        
        if "state" in connections_result:
            state = connections_result["state"]
            rfc23_state = connections_result.get("rfc23_state", "")
            
            # Connection is active when state is "active"
            is_connected = state == "active"
            
            logger.info(f"Verifier connection {connection_id} state: {state}, rfc23_state: {rfc23_state}")
            
            if connection_id in app_state["connections"]:
                app_state["connections"][connection_id]["status"] = state
                
                # If connected and not already requested proof, request it
                if is_connected and "proof_requested" not in app_state["connections"][connection_id]:
                    logger.info(f"Auto-requesting proof for connection {connection_id}")
                    
                    try:
                        proof_result = await agent.request_proof(connection_id)
                        
                        if "presentation_exchange_id" in proof_result:
                            app_state["connections"][connection_id]["proof_requested"] = True
                            app_state["connections"][connection_id]["presentation_exchange_id"] = proof_result["presentation_exchange_id"]
                            logger.info(f"Proof request sent successfully: {proof_result['presentation_exchange_id']}")
                        else:
                            logger.error(f"Failed to request proof: {proof_result}")
                            
                    except Exception as proof_error:
                        logger.error(f"Error requesting proof: {str(proof_error)}")
            
            return web.json_response({
                "connected": is_connected,
                "state": state,
                "rfc23_state": rfc23_state
            })
        else:
            return web.json_response({
                "connected": False,
                "error": f"Failed to get connection status: {connections_result}"
            })
            
    except Exception as e:
        logger.error(f"Error checking verifier status: {str(e)}")
        return web.json_response({
            "connected": False,
            "error": str(e)
        })

@routes.get('/api/issuer/credential-status/{connection_id}')
async def api_issuer_credential_status(request: Request) -> Response:
    """Get credential issuance status"""
    connection_id = request.match_info['connection_id']
    
    try:
        agent = request.app["ssi_agent"]
        
        if connection_id in app_state["connections"]:
            connection_info = app_state["connections"][connection_id]
            
            if "credential_exchange_id" in connection_info:
                cred_ex_id = connection_info["credential_exchange_id"]
                
                # Check credential exchange status
                cred_status_result = await agent.admin_request("GET", f"/issue-credential/records/{cred_ex_id}")
                
                if "state" in cred_status_result:
                    state = cred_status_result["state"]
                    
                    # Different states of credential exchange
                    is_issued = state in ["credential_acked", "done"]
                    is_offered = state == "offer_sent"
                    is_requested = state == "request_received"
                    is_pending = state in ["offer_sent", "request_received"]
                    
                    logger.info(f"Credential exchange {cred_ex_id} state: {state}")
                    
                    return web.json_response({
                        "issued": is_issued,
                        "offered": is_offered,
                        "requested": is_requested,
                        "pending": is_pending,
                        "state": state,
                        "credential_exchange_id": cred_ex_id
                    })
                else:
                    return web.json_response({
                        "issued": False,
                        "error": f"Failed to get credential status: {cred_status_result}"
                    })
            else:
                return web.json_response({
                    "issued": False,
                    "state": "not_started"
                })
        else:
            return web.json_response({
                "issued": False,
                "error": "Connection not found"
            })
            
    except Exception as e:
        logger.error(f"Error checking credential status: {str(e)}")
        return web.json_response({
            "issued": False,
            "error": str(e)
        })

@routes.get('/api/verifier/proof-status/{connection_id}')
async def api_verifier_proof_status(request: Request) -> Response:
    """Get proof verification status"""
    connection_id = request.match_info['connection_id']
    
    try:
        agent = request.app["ssi_agent"]
        
        # Get proof records for this connection
        result = await agent.admin_request("GET", f"/present-proof/records")
        
        if "error" in result:
            return web.json_response({
                "verified": False,
                "requested": False,
                "error": result["error"]
            })
        
        # Look for proof records related to this connection
        proof_records = result.get("results", [])
        
        for record in proof_records:
            if record.get("connection_id") == connection_id:
                state = record.get("state", "")
                verified = state == "verified"
                requested = state in ["request_sent", "presentation_received", "verified"]
                
                if verified:
                    # Extract verified attributes from the proof
                    presentation = record.get("presentation", {})
                    revealed_attrs = {}
                    
                    if presentation:
                        try:
                            requested_proof = presentation.get("requested_proof", {})
                            if requested_proof:
                                revealed_attrs_v1 = requested_proof.get("revealed_attrs", {})
                                for attr_name, attr_data in revealed_attrs_v1.items():
                                    if "raw" in attr_data:
                                        # Extract the actual attribute name from referent
                                        actual_name = attr_name.replace("_referent", "")
                                        revealed_attrs[actual_name] = attr_data["raw"]
                        except Exception as e:
                            logger.error(f"Error extracting proof attributes: {str(e)}")
                    
                    return web.json_response({
                        "verified": True,
                        "requested": True,
                        "attributes": revealed_attrs,
                        "proof_record": record
                    })
                
                return web.json_response({
                    "verified": verified,
                    "requested": requested,
                    "state": state
                })
        
        return web.json_response({
            "verified": False,
            "requested": False
        })
        
    except Exception as e:
        logger.error(f"Error getting proof status: {str(e)}")
        return web.json_response({
            "verified": False,
            "requested": False,
            "error": str(e)
        })

@routes.post('/api/issuer/force-credential/{connection_id}')
async def api_force_issue_credential(request: Request) -> Response:
    """Force issue credential regardless of connection state"""
    connection_id = request.match_info['connection_id']
    
    try:
        agent = request.app["ssi_agent"]
        
        if connection_id in app_state["connections"]:
            attributes = app_state["connections"][connection_id].get("attributes", {})
            
            logger.info(f"Force issuing credential for connection {connection_id}")
            credential_result = await agent.issue_credential(connection_id, attributes)
            
            if "credential_exchange_id" in credential_result:
                app_state["connections"][connection_id]["credential_exchange_id"] = credential_result["credential_exchange_id"]
                app_state["connections"][connection_id]["credential_issued"] = True
                
                return web.json_response({
                    "success": True,
                    "message": "Credential issued successfully",
                    "credential_exchange_id": credential_result["credential_exchange_id"]
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": f"Failed to issue credential: {credential_result.get('error', 'Unknown error')}"
                })
        else:
            return web.json_response({
                "success": False,
                "error": "Connection not found"
            })
            
    except Exception as e:
        logger.error(f"Error force issuing credential: {str(e)}")
        return web.json_response({
            "success": False,
            "error": str(e)
        })

@routes.post('/api/verifier/force-proof/{connection_id}')
async def api_force_proof_request(request: Request) -> Response:
    """Force request proof regardless of connection state"""
    connection_id = request.match_info['connection_id']
    
    try:
        agent = request.app["ssi_agent"]
        
        if connection_id in app_state["connections"]:
            logger.info(f"Force requesting proof for connection {connection_id}")
            
            proof_result = await agent.request_proof(connection_id)
            
            if "presentation_exchange_id" in proof_result:
                app_state["connections"][connection_id]["proof_requested"] = True
                app_state["connections"][connection_id]["force_requested"] = True
                app_state["connections"][connection_id]["presentation_exchange_id"] = proof_result["presentation_exchange_id"]
                
                return web.json_response({
                    "success": True,
                    "presentation_exchange_id": proof_result["presentation_exchange_id"],
                    "message": "Proof request sent successfully"
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": f"Failed to request proof: {proof_result.get('error', 'Unknown error')}"
                })
        else:
            return web.json_response({
                "success": False,
                "error": "Connection not found"
            })
            
    except Exception as e:
        logger.error(f"Error force requesting proof: {str(e)}")
        return web.json_response({
            "success": False,
            "error": str(e)
        })

@routes.get('/api/agent/info')
async def api_agent_info(request: Request) -> Response:
    """Get agent schema and credential definition information"""
    try:
        agent = request.app["ssi_agent"]
        
        return web.json_response({
            "success": True,
            "schema_id": agent.schema_id,
            "cred_def_id": agent.cred_def_id,
            "available": agent.schema_id is not None and agent.cred_def_id is not None
        })
    except Exception as e:
        logger.error(f"Error getting agent info: {str(e)}")
        return web.json_response({
            "success": False,
            "error": str(e)
        })
