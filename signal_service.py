import requests
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class SignalModerationService:
    def __init__(self, signal_api_url="http://localhost:8080", account="+15614121835"):
        self.signal_api_url = signal_api_url
        self.account = account
        self.db_path = "/home/.local/share/signal-cli/data/271089.d/account.db"
        
    def get_health(self) -> Dict:
        """Check Signal API health"""
        try:
            response = requests.get(f"{self.signal_api_url}/v1/about", timeout=10)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "signal_api": True,
                "database": self._check_database()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "signal_api": False,
                "database": self._check_database(),
                "error": str(e)
            }
    
    def _check_database(self) -> bool:
        """Check if SQLite database is accessible"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipient")
            conn.close()
            return True
        except:
            return False
    
    def get_groups(self) -> List[Dict]:
        """Get all groups for the account"""
        try:
            response = requests.get(f"{self.signal_api_url}/v1/groups/{self.account}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []
    
    def get_group_members(self, group_id: str = None) -> List[Dict]:
        """Get members of a specific group or all groups"""
        try:
            groups = self.get_groups()
            all_members = []
            
            for group in groups:
                if group_id and group.get('id') != group_id:
                    continue
                    
                members = group.get('members', [])
                for member in members:
                    member_info = self._get_member_profile(member)
                    member_info['group_id'] = group.get('id')
                    member_info['group_name'] = group.get('name', 'Unknown Group')
                    all_members.append(member_info)
            
            return all_members
        except Exception as e:
            print(f"Error getting group members: {e}")
            return []
    
    def _get_member_profile(self, member_id: str) -> Dict:
        """Get profile information for a member from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try to find by ACI (UUID) or phone number
            cursor.execute("""
                SELECT aci, number, profile_given_name, profile_family_name, 
                       profile_last_update_timestamp, blocked, mute_until
                FROM recipient 
                WHERE aci = ? OR number = ?
            """, (member_id, member_id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                aci, number, given_name, family_name, last_update, blocked, mute_until = result
                
                # Combine names
                display_name = ""
                if given_name and family_name:
                    display_name = f"{given_name} {family_name}"
                elif given_name:
                    display_name = given_name
                elif number:
                    display_name = number
                else:
                    display_name = f"Member {member_id[:8]}"
                
                return {
                    "id": member_id,
                    "aci": aci,
                    "number": number,
                    "display_name": display_name,
                    "given_name": given_name,
                    "family_name": family_name,
                    "last_profile_update": last_update,
                    "blocked": bool(blocked),
                    "muted": bool(mute_until and mute_until > 0),
                    "has_profile": bool(given_name or family_name),
                    "member_type": "phone" if number else "uuid"
                }
            else:
                return {
                    "id": member_id,
                    "display_name": f"Member {member_id[:8]}",
                    "has_profile": False,
                    "member_type": "unknown"
                }
                
        except Exception as e:
            print(f"Error getting member profile: {e}")
            return {
                "id": member_id,
                "display_name": f"Member {member_id[:8]}",
                "has_profile": False,
                "member_type": "error"
            }
    
    def get_member_statistics(self) -> Dict:
        """Get statistics about group members"""
        members = self.get_group_members()
        
        total_members = len(members)
        members_with_profiles = len([m for m in members if m.get('has_profile')])
        phone_members = len([m for m in members if m.get('member_type') == 'phone'])
        uuid_members = len([m for m in members if m.get('member_type') == 'uuid'])
        blocked_members = len([m for m in members if m.get('blocked')])
        muted_members = len([m for m in members if m.get('muted')])
        
        return {
            "total_members": total_members,
            "members_with_profiles": members_with_profiles,
            "phone_members": phone_members,
            "uuid_members": uuid_members,
            "blocked_members": blocked_members,
            "muted_members": muted_members,
            "profile_resolution_rate": round((members_with_profiles / total_members * 100) if total_members > 0 else 0, 1)
        }
    
    def send_message_to_group(self, message: str, group_id: str = None) -> Dict:
        """Send a message to a group"""
        try:
            # If no group_id specified, use the first available group
            if not group_id:
                groups = self.get_groups()
                if not groups:
                    return {"success": False, "error": "No groups found"}
                group_id = groups[0].get('id')
            
            payload = {
                "message": message,
                "recipients": [group_id]
            }
            
            response = requests.post(
                f"{self.signal_api_url}/v2/send",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                return {"success": True, "timestamp": response.json().get('timestamp')}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def force_profile_sync(self) -> Dict:
        """Force a profile sync for group members"""
        try:
            # Send a sync request
            response = requests.post(f"{self.signal_api_url}/v1/send-sync-request/{self.account}", timeout=30)
            
            if response.status_code == 200:
                return {"success": True, "message": "Profile sync initiated"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_members(self, query: str) -> List[Dict]:
        """Search members by name or ID"""
        members = self.get_group_members()
        query_lower = query.lower()
        
        filtered_members = []
        for member in members:
            if (query_lower in member.get('display_name', '').lower() or
                query_lower in member.get('id', '').lower() or
                query_lower in member.get('number', '').lower()):
                filtered_members.append(member)
        
        return filtered_members
    
    def get_inactive_members(self, days: int = 30) -> List[Dict]:
        """Get members who haven't updated their profile recently"""
        members = self.get_group_members()
        cutoff_timestamp = (datetime.now().timestamp() - (days * 24 * 60 * 60)) * 1000
        
        inactive_members = []
        for member in members:
            last_update = member.get('last_profile_update', 0)
            if last_update == 0 or last_update < cutoff_timestamp:
                member['days_since_update'] = days if last_update == 0 else int((datetime.now().timestamp() * 1000 - last_update) / (24 * 60 * 60 * 1000))
                inactive_members.append(member)
        
        return inactive_members

