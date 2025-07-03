"""
Erweiterte Gruppenverwaltung mit automatischer Abhängigkeiten-Verwaltung
Stellt sicher, dass alle abhängigen Daten korrekt angelegt/gelöscht werden
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Dict, List, Optional
import json

from app.models import (
    Group, GroupUserRole, GroupWarning, GroupMute, 
    ScheduledMessage, User, SignalGroup
)
from ..database import get_db

logger = logging.getLogger(__name__)

class EnhancedGroupManagement:
    """Erweiterte Gruppenverwaltung mit vollständiger Abhängigkeiten-Verwaltung"""
    
    def create_group_with_dependencies(self, group_data: Dict, owner_id: int, db: Session) -> Dict:
        """Erstellt eine Gruppe mit allen abhängigen Daten"""
        try:
            # 1. Gruppe erstellen
            new_group = Group(
                group_id=group_data.get("group_id"),
                name=group_data.get("name", "Neue Gruppe"),
                settings=json.dumps(group_data.get("settings", {})),
                welcome_text=group_data.get("welcome_text", "Willkommen in der Gruppe!"),
                night_mode=group_data.get("night_mode", False),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_group)
            db.flush()  # Um die ID zu erhalten
            
            # 2. Besitzer als Admin hinzufügen
            owner_role = GroupUserRole(
                user_id=owner_id,
                group_id=new_group.id,
                role="owner",
                warnings=0,
                mutes=0,
                is_banned=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(owner_role)
            
            # 3. Standard-Einstellungen anwenden
            self._apply_default_group_settings(new_group, db)
            
            db.commit()
            
            logger.info(f"Gruppe {new_group.id} mit Besitzer {owner_id} erstellt")
            
            return {
                "success": True,
                "group_id": new_group.id,
                "telegram_group_id": new_group.group_id,
                "name": new_group.name
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Gruppe: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def delete_group_with_dependencies(self, group_id: int, db: Session) -> Dict:
        """Löscht eine Gruppe und alle abhängigen Daten"""
        try:
            group = db.query(Group).filter(Group.id == group_id).first()
            if not group:
                return {"success": False, "error": "Gruppe nicht gefunden"}
            
            logger.info(f"Lösche Gruppe {group_id} mit allen Abhängigkeiten")
            
            # 1. Alle User-Rollen löschen
            deleted_roles = db.query(GroupUserRole).filter(
                GroupUserRole.group_id == group_id
            ).delete()
            
            # 2. Alle Warnungen löschen
            deleted_warnings = db.query(GroupWarning).filter(
                GroupWarning.group_id == group_id
            ).delete()
            
            # 3. Alle Mutes löschen
            deleted_mutes = db.query(GroupMute).filter(
                GroupMute.group_id == group_id
            ).delete()
            
            # 4. Alle geplanten Nachrichten löschen
            deleted_messages = db.query(ScheduledMessage).filter(
                ScheduledMessage.chat_id == group.group_id
            ).delete()
            
            # 5. Gruppe selbst löschen
            db.delete(group)
            
            db.commit()
            
            logger.info(f"Gruppe {group_id} gelöscht: {deleted_roles} Rollen, {deleted_warnings} Warnungen, {deleted_mutes} Mutes, {deleted_messages} Nachrichten")
            
            return {
                "success": True,
                "deleted_roles": deleted_roles,
                "deleted_warnings": deleted_warnings,
                "deleted_mutes": deleted_mutes,
                "deleted_messages": deleted_messages
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Gruppe: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def update_group_settings(self, group_id: int, settings: Dict, db: Session) -> Dict:
        """Aktualisiert Gruppeneinstellungen und speichert sie in der DB"""
        try:
            group = db.query(Group).filter(Group.id == group_id).first()
            if not group:
                return {"success": False, "error": "Gruppe nicht gefunden"}
            
            # Aktuelle Einstellungen laden
            current_settings = {}
            if group.settings:
                try:
                    current_settings = json.loads(group.settings)
                except:
                    current_settings = {}
            
            # Neue Einstellungen mit aktuellen zusammenführen
            updated_settings = {**current_settings, **settings}
            
            # Gruppe aktualisieren
            group.settings = json.dumps(updated_settings)
            group.updated_at = datetime.utcnow()
            
            # Spezifische Felder aktualisieren
            if "welcome_text" in settings:
                group.welcome_text = settings["welcome_text"]
            
            if "night_mode" in settings:
                group.night_mode = settings["night_mode"]
            
            db.commit()
            
            logger.info(f"Gruppeneinstellungen für Gruppe {group_id} aktualisiert")
            
            return {
                "success": True,
                "group_id": group_id,
                "settings": updated_settings
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Gruppeneinstellungen: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def add_user_to_group(self, group_id: int, user_id: int, db: Session, role: str = "user") -> Dict:
        """Fügt einen User zu einer Gruppe hinzu"""
        try:
            # Prüfe ob User bereits in der Gruppe ist
            existing_role = db.query(GroupUserRole).filter(
                and_(
                    GroupUserRole.group_id == group_id,
                    GroupUserRole.user_id == user_id
                )
            ).first()
            
            if existing_role:
                # Rolle aktualisieren
                existing_role.role = role
                existing_role.updated_at = datetime.utcnow()
                action = "updated"
            else:
                # Neue Rolle erstellen
                new_role = GroupUserRole(
                    user_id=user_id,
                    group_id=group_id,
                    role=role,
                    warnings=0,
                    mutes=0,
                    is_banned=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_role)
                action = "created"
            
            db.commit()
            
            logger.info(f"User {user_id} zur Gruppe {group_id} hinzugefügt (Rolle: {role})")
            
            return {
                "success": True,
                "action": action,
                "user_id": user_id,
                "group_id": group_id,
                "role": role
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen des Users zur Gruppe: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def remove_user_from_group(self, group_id: int, user_id: int, db: Session) -> Dict:
        """Entfernt einen User aus einer Gruppe und löscht alle zugehörigen Daten"""
        try:
            # User-Rolle löschen
            deleted_role = db.query(GroupUserRole).filter(
                and_(
                    GroupUserRole.group_id == group_id,
                    GroupUserRole.user_id == user_id
                )
            ).delete()
            
            # Warnungen löschen
            deleted_warnings = db.query(GroupWarning).filter(
                and_(
                    GroupWarning.group_id == group_id,
                    GroupWarning.user_id == user_id
                )
            ).delete()
            
            # Mutes löschen
            deleted_mutes = db.query(GroupMute).filter(
                and_(
                    GroupMute.group_id == group_id,
                    GroupMute.user_id == user_id
                )
            ).delete()
            
            db.commit()
            
            logger.info(f"User {user_id} aus Gruppe {group_id} entfernt: {deleted_role} Rolle, {deleted_warnings} Warnungen, {deleted_mutes} Mutes")
            
            return {
                "success": True,
                "deleted_role": deleted_role,
                "deleted_warnings": deleted_warnings,
                "deleted_mutes": deleted_mutes
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Entfernen des Users aus der Gruppe: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def warn_user(self, group_id: int, user_id: int, reason: str, issued_by: int, db: Session) -> Dict:
        """Verwarnt einen User in einer Gruppe"""
        try:
            # Warnung erstellen
            warning = GroupWarning(
                user_id=user_id,
                group_id=group_id,
                reason=reason,
                issued_by=issued_by,
                timestamp=datetime.utcnow()
            )
            db.add(warning)
            
            # User-Rolle aktualisieren
            user_role = db.query(GroupUserRole).filter(
                and_(
                    GroupUserRole.group_id == group_id,
                    GroupUserRole.user_id == user_id
                )
            ).first()
            
            if user_role:
                user_role.warnings += 1
                user_role.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"User {user_id} in Gruppe {group_id} verwarnt: {reason}")
            
            return {
                "success": True,
                "warning_id": warning.id,
                "user_id": user_id,
                "group_id": group_id,
                "reason": reason,
                "warnings_count": user_role.warnings if user_role else 0
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Verwarnen des Users: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def mute_user(self, group_id: int, user_id: int, duration_seconds: int, reason: str, issued_by: int, db: Session) -> Dict:
        """Mutiert einen User in einer Gruppe"""
        try:
            end_time = datetime.utcnow() + timedelta(seconds=duration_seconds)
            
            # Mute erstellen
            mute = GroupMute(
                user_id=user_id,
                group_id=group_id,
                start_time=datetime.utcnow(),
                end_time=end_time,
                reason=reason,
                issued_by=issued_by,
                active=True,
                timestamp=datetime.utcnow()
            )
            db.add(mute)
            
            # User-Rolle aktualisieren
            user_role = db.query(GroupUserRole).filter(
                and_(
                    GroupUserRole.group_id == group_id,
                    GroupUserRole.user_id == user_id
                )
            ).first()
            
            if user_role:
                user_role.mutes += 1
                user_role.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"User {user_id} in Gruppe {group_id} gemutet für {duration_seconds} Sekunden: {reason}")
            
            return {
                "success": True,
                "mute_id": mute.id,
                "user_id": user_id,
                "group_id": group_id,
                "duration_seconds": duration_seconds,
                "end_time": end_time.isoformat(),
                "mutes_count": user_role.mutes if user_role else 0
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Mutieren des Users: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def _apply_default_group_settings(self, group: Group, db: Session):
        """Wendet Standard-Einstellungen auf eine neue Gruppe an"""
        try:
            default_settings = {
                "welcome_message": "Willkommen in der Gruppe!",
                "night_mode_enabled": False,
                "night_mode_start": "22:00",
                "night_mode_end": "08:00",
                "forwarding_allowed": True,
                "links_allowed": True,
                "badwords_enabled": False,
                "badwords_list": [],
                "auto_delete_spam": False,
                "max_warnings": 3,
                "max_mutes": 5
            }
            
            group.settings = json.dumps(default_settings)
            group.welcome_text = default_settings["welcome_message"]
            group.night_mode = default_settings["night_mode_enabled"]
            
        except Exception as e:
            logger.error(f"Fehler beim Anwenden der Standard-Einstellungen: {e}")

# Globale Instanz
group_manager = EnhancedGroupManagement() 