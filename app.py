#!/usr/bin/env python3
"""
Signal Moderation Bot - Fixed Version
Works directly with signal-cli data without requiring REST API service
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import os
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SignalBotService:
    def __init__(self):
        self.phone_number = "+15614121835"
        self.group_id = "group.MWdCWUZWeG5vWDI2L0c4OVhNaXQ3VHZOKzFwZTZJbjZDaGp3bW5ldm1GTT0="
        
        # Signal-CLI data paths
        self.signal_data_dir = "/home/.local/share/signal-cli"
        self.account_dir = f"{self.signal_data_dir}/data/271089.d"
        self.db_path = f"{self.account_dir}/account.db"
        self.accounts_json = f"{self.signal_data_dir}/data/accounts.json"
        
        logger.info(f"Initialized SignalBotService for {self.phone_number}")
        logger.info(f"Account directory: {self.account_dir}")
        logger.info(f"Database path: {self.db_path}")
        
    def check_system_status(self) -> Dict:
        """Check if Signal system is working properly"""
        try:
            # Check if signal-cli data exists
            if not os.path.exists(self.signal_data_dir):
                return {"status": "error", "message": "Signal-CLI data directory not found"}
                
            if not os.path.exists(self.accounts_json):
                return {"status": "error", "message": "Accounts.json not found"}
                
            if not os.path.exists(self.db_path):
                return {"status": "error", "message": "Account database not found"}
                
            # Check if we can read the database
            members = self.get_group_members()
            if members is None:
                return {"status": "error", "message": "Cannot read group members from database"}
                
            return {"status": "ok", "message": f"System working - {len(members)} members found"}
            
        except Exception as e:
            logger.error(f"System status check failed: {e}")
            return {"status": "error", "message": f"System check failed: {str(e)}"}
    
    def get_group_members(self) -> Optional[List[Dict]]:
        """Get group members from signal-cli database"""
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"Database not found: {self.db_path}")
                return None
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query to get recipients (contacts) from signal-cli database
            # Signal-CLI stores contacts in the recipient table
            query = """
            SELECT 
                _id,
                aci,
                number,
                profile_given_name,
                profile_family_name,
                given_name,
                family_name,
                username
            FROM recipient 
            WHERE (number IS NOT NULL OR aci IS NOT NULL)
            AND (number != ? OR number IS NULL)
            """
            
            cursor.execute(query, (self.phone_number,))
            rows = cursor.fetchall()
            
            members = []
            for row in rows:
                recipient_id, aci, number, profile_given_name, profile_family_name, given_name, family_name, username = row
                
                # Build display name from available name fields
                display_name = "Unknown"
                if profile_given_name and profile_family_name:
                    display_name = f"{profile_given_name} {profile_family_name}"
                elif profile_given_name:
                    display_name = profile_given_name
                elif given_name and family_name:
                    display_name = f"{given_name} {family_name}"
                elif given_name:
                    display_name = given_name
                elif username:
                    display_name = username
                elif number:
                    display_name = number
                
                member = {
                    "id": str(recipient_id),  # Convert to string for frontend compatibility
                    "uuid": aci,  # Signal-CLI uses 'aci' field for UUID
                    "phone": number,
                    "name": display_name,
                    "display_name": display_name,
                    "given_name": given_name or profile_given_name,
                    "family_name": family_name or profile_family_name,
                    "username": username,
                    "role": "member",  # Signal-CLI doesn't store roles in recipient table
                    "has_profile": bool(profile_given_name or profile_family_name or given_name or family_name),
                    "has_phone": bool(number),
                    "member_type": "phone" if number else "uuid"
                }
                members.append(member)
            
            conn.close()
            logger.info(f"Found {len(members)} group members")
            return members
            
        except Exception as e:
            logger.error(f"Error getting group members: {e}")
            return None
    
    def get_member_statistics(self) -> Dict:
        """Get group statistics"""
        try:
            members = self.get_group_members()
            if members is None:
                return {
                    "total_members": 0,
                    "members_with_profiles": 0,
                    "profile_resolution_rate": 0,
                    "phone_members": 0,
                    "uuid_members": 0
                }
            
            total = len(members)
            known_profiles = len([m for m in members if m["has_profile"]])
            phone_numbers = len([m for m in members if m["has_phone"]])
            uuid_members = len([m for m in members if m["uuid"]])
            profile_rate = int((known_profiles/total*100)) if total > 0 else 0
            
            return {
                "total_members": total,
                "members_with_profiles": known_profiles,
                "profile_resolution_rate": profile_rate,
                "phone_members": phone_numbers,
                "uuid_members": uuid_members
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_members": 0,
                "members_with_profiles": 0,
                "profile_resolution_rate": 0,
                "phone_members": 0,
                "uuid_members": 0
            }
    
    def get_health(self) -> Dict:
        """Get system health status"""
        status = self.check_system_status()
        return {
            "status": "healthy" if status["status"] == "ok" else "unhealthy",
            "signal_api": status["status"] == "ok",
            "database": status["status"] == "ok",
            "message": status["message"]
        }

# Global service instance
signal_service = SignalBotService()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "signal-moderation-bot"})

@app.route('/api/stats')
def get_stats():
    """Get member statistics"""
    try:
        stats = signal_service.get_member_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members')
def get_members():
    """Get all group members"""
    try:
        members = signal_service.get_group_members()
        if members is None:
            return jsonify([])
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members/search')
def search_members():
    """Search members"""
    query = request.args.get('q', '').lower()
    try:
        members = signal_service.get_group_members()
        if members is None:
            return jsonify([])
        
        # Filter members by search query
        filtered = [m for m in members if query in m.get('display_name', '').lower() or 
                   query in m.get('phone', '').lower() or 
                   query in str(m.get('uuid', '')).lower()]
        return jsonify(filtered)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members/inactive')
def get_inactive_members():
    """Get inactive members (members without profiles)"""
    try:
        members = signal_service.get_group_members()
        if members is None:
            return jsonify([])
        
        inactive = [m for m in members if not m["has_profile"]]
        return jsonify(inactive)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/groups')
def get_groups():
    """Get all groups"""
    try:
        # Return mock group data since we're working with a specific group
        return jsonify([{
            "id": signal_service.group_id,
            "name": "Signal Group",
            "members_count": len(signal_service.get_group_members() or [])
        }])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Send message to group (simulated for now)"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message.strip():
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400
        
        # Simulate sending message for now (signal-cli not available in container)
        logger.info(f"Would send message to group: {message}")
        return jsonify({"success": True, "message": "Message sent successfully (simulated - signal-cli not available)"})
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/sync-profiles', methods=['POST'])
def sync_profiles():
    """Force profile sync (simulated)"""
    try:
        members = signal_service.get_group_members()
        count = len(members) if members else 0
        return jsonify({
            "success": True, 
            "message": f"Profile sync completed for {count} members (simulated)"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/send-member-list', methods=['POST'])
def send_member_list():
    """Send member list to group (simulated)"""
    try:
        # Get member statistics
        stats = signal_service.get_member_statistics()
        members = signal_service.get_group_members()
        
        if not members:
            return jsonify({"success": False, "error": "No members found"})
        
        # Create member list message
        message = f"📊 **Group Member Report**\\n\\n"
        message += f"👥 **Total Members:** {stats['total_members']}\\n"
        message += f"✅ **Known Profiles:** {stats['members_with_profiles']} ({stats['profile_resolution_rate']}%)\\n"
        message += f"📱 **Phone Numbers:** {stats['phone_members']}\\n"
        message += f"🆔 **UUID Members:** {stats['uuid_members']}\\n\\n"
        
        message += "**Member List:**\\n"
        for i, member in enumerate(members[:20], 1):  # Limit to first 20 for message length
            icon = "📱" if member.get('member_type') == 'phone' else "👤"
            status = "✅" if member.get('has_profile') else "❓"
            message += f"{i}. {icon} {member.get('display_name')} {status}\\n"
        
        if len(members) > 20:
            message += f"\\n... and {len(members) - 20} more members\\n"
        
        message += f"\\n🤖 Generated by Signal Moderation Bot"
        
        logger.info(f"Would send member list to group: {len(message)} characters")
        return jsonify({"success": True, "message": "Member list sent successfully (simulated)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

