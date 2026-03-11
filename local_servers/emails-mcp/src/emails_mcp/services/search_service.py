import logging
from typing import List, Optional
from ..models.email import EmailMessage
from ..utils.exceptions import EmailMCPError


class SearchService:
    """Email search service layer"""

    def __init__(self, imap_backend):
        self.imap_backend = imap_backend

    def search_emails_by_query(self, query: str, folder: Optional[str] = None) -> List[str]:
        """Search emails and return email IDs"""
        try:
            # If no folder specified, use INBOX as default
            if not folder:
                folder = 'INBOX'
            return self.imap_backend.search_emails(query, folder)
        except Exception as e:
            raise EmailMCPError(f"Failed to search emails: {str(e)}")

    def search_by_sender(self, sender: str, folder: Optional[str] = None) -> List[str]:
        """Search emails by sender using PG full-text search on from_addr"""
        try:
            if not folder:
                folder = 'INBOX'
            # Delegate to the backend's search which searches subject+body.
            # For sender-specific search we query the DB directly.
            self.imap_backend.ensure_connected()
            folder_id = self.imap_backend._get_or_create_folder(folder)
            with self.imap_backend.connection.cursor() as cur:
                cur.execute(
                    "SELECT id FROM email.messages "
                    "WHERE folder_id = %s AND from_addr ILIKE %s "
                    "ORDER BY date DESC, id DESC",
                    (folder_id, f"%{sender}%"),
                )
                rows = cur.fetchall()
            return [str(r[0]) for r in rows]
        except Exception as e:
            raise EmailMCPError(f"Failed to search by sender: {str(e)}")

    def search_by_subject(self, subject: str, folder: Optional[str] = None) -> List[str]:
        """Search emails by subject using PG ILIKE"""
        try:
            if not folder:
                folder = 'INBOX'
            self.imap_backend.ensure_connected()
            folder_id = self.imap_backend._get_or_create_folder(folder)
            with self.imap_backend.connection.cursor() as cur:
                cur.execute(
                    "SELECT id FROM email.messages "
                    "WHERE folder_id = %s AND subject ILIKE %s "
                    "ORDER BY date DESC, id DESC",
                    (folder_id, f"%{subject}%"),
                )
                rows = cur.fetchall()
            return [str(r[0]) for r in rows]
        except Exception as e:
            raise EmailMCPError(f"Failed to search by subject: {str(e)}")

    def search_by_date_range(self, since_date: str, before_date: Optional[str] = None,
                           folder: Optional[str] = None) -> List[str]:
        """Search emails by date range (YYYY-MM-DD format)"""
        try:
            if not folder:
                folder = 'INBOX'
            self.imap_backend.ensure_connected()
            folder_id = self.imap_backend._get_or_create_folder(folder)

            sql = "SELECT id FROM email.messages WHERE folder_id = %s AND date >= %s::date"
            params: list = [folder_id, since_date]
            if before_date:
                sql += " AND date < %s::date"
                params.append(before_date)
            sql += " ORDER BY date DESC, id DESC"

            with self.imap_backend.connection.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            return [str(r[0]) for r in rows]
        except Exception as e:
            raise EmailMCPError(f"Failed to search by date: {str(e)}")