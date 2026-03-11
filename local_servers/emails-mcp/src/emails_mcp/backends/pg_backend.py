import json
import logging
import os
import uuid
from datetime import datetime
from email import policy
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.parser import Parser
from email.utils import formataddr, formatdate, make_msgid
from typing import List, Optional, Tuple

import psycopg2
import psycopg2.extras

from ..models.config import EmailConfig
from ..models.email import EmailAttachment, EmailFolder, EmailMessage
from ..utils.exceptions import ConnectionError, FolderError, SendEmailError


def _get_pg_conn_params() -> dict:
    """Get PostgreSQL connection parameters from environment variables."""
    return {
        "host": os.environ.get("PG_HOST", "localhost"),
        "port": int(os.environ.get("PG_PORT", "5432")),
        "database": os.environ.get("PG_DATABASE", "toolathlon"),
        "user": os.environ.get("PG_USER", "postgres"),
        "password": os.environ.get("PG_PASSWORD", "postgres"),
    }


def _jsonb_list_to_comma_str(jsonb_val) -> str:
    """Convert a JSONB list (or Python list) to a comma-separated string."""
    if jsonb_val is None:
        return ""
    if isinstance(jsonb_val, str):
        try:
            jsonb_val = json.loads(jsonb_val)
        except (json.JSONDecodeError, TypeError):
            return jsonb_val
    if isinstance(jsonb_val, list):
        return ", ".join(str(v) for v in jsonb_val if v)
    return str(jsonb_val)


def _comma_str_to_jsonb_list(comma_str: Optional[str]) -> list:
    """Convert a comma-separated string to a JSON-serializable list."""
    if not comma_str:
        return []
    return [addr.strip() for addr in comma_str.split(",") if addr.strip()]


class PgIMAPBackend:
    """PostgreSQL-backed IMAP replacement backend for email operations."""

    def __init__(self, config: EmailConfig):
        self.config = config
        self.connection = None  # psycopg2 connection
        self.current_folder: Optional[str] = None
        self.utf8_enabled = True  # Always true for PG

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """Establish PostgreSQL connection."""
        try:
            self.connection = psycopg2.connect(**_get_pg_conn_params())
            self.connection.autocommit = True
            logging.info("PgIMAPBackend connected to PostgreSQL")
            return True
        except Exception as e:
            logging.error(f"PgIMAPBackend connection failed: {e}")
            raise ConnectionError(f"PostgreSQL connection failed: {e}")

    def disconnect(self):
        """Close PostgreSQL connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            finally:
                self.connection = None
                self.current_folder = None

    def ensure_connected(self):
        """Ensure PostgreSQL connection is active."""
        if self.connection is None or self.connection.closed:
            self.connect()
            return
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT 1")
        except Exception:
            logging.warning("PgIMAPBackend connection lost, reconnecting...")
            self.disconnect()
            self.connect()

    # ------------------------------------------------------------------
    # Folder operations
    # ------------------------------------------------------------------

    def _get_or_create_folder(self, folder_name: str) -> int:
        """Return folder id, creating the folder row if it doesn't exist."""
        self.ensure_connected()
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO email.folders (name) VALUES (%s) "
                "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name "
                "RETURNING id",
                (folder_name,),
            )
            return cur.fetchone()[0]

    def _refresh_folder_counts(self, folder_id: int):
        """Refresh message_count and unread_count for a folder."""
        with self.connection.cursor() as cur:
            cur.execute(
                "UPDATE email.folders SET "
                "message_count = (SELECT COUNT(*) FROM email.messages WHERE folder_id = %s), "
                "unread_count  = (SELECT COUNT(*) FROM email.messages WHERE folder_id = %s AND is_read = FALSE) "
                "WHERE id = %s",
                (folder_id, folder_id, folder_id),
            )

    def select_folder(self, folder: str) -> Tuple[int, int]:
        """Select email folder and return (total_messages, unread_messages)."""
        self.ensure_connected()
        folder = folder.strip()
        folder_id = self._get_or_create_folder(folder)
        self._refresh_folder_counts(folder_id)
        self.current_folder = folder

        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT message_count, unread_count FROM email.folders WHERE id = %s",
                (folder_id,),
            )
            row = cur.fetchone()
            if row is None:
                raise FolderError(f"Folder '{folder}' not found")
            return row[0], row[1]

    def list_folders(self) -> List[EmailFolder]:
        """List all available folders."""
        self.ensure_connected()
        with self.connection.cursor() as cur:
            cur.execute("SELECT id, name, message_count, unread_count FROM email.folders ORDER BY name")
            rows = cur.fetchall()

        folders = []
        for row in rows:
            folder_id, name, msg_count, unread_count = row
            # Refresh counts for accuracy
            self._refresh_folder_counts(folder_id)
            with self.connection.cursor() as cur:
                cur.execute(
                    "SELECT message_count, unread_count FROM email.folders WHERE id = %s",
                    (folder_id,),
                )
                updated = cur.fetchone()
            folders.append(
                EmailFolder(
                    name=name,
                    total_messages=updated[0] if updated else msg_count,
                    unread_messages=updated[1] if updated else unread_count,
                    can_select=True,
                )
            )
        return folders

    def create_folder(self, folder_name: str) -> bool:
        """Create a new email folder."""
        self.ensure_connected()
        folder_name = folder_name.strip()
        try:
            self._get_or_create_folder(folder_name)
            logging.info(f"Folder '{folder_name}' created (or already exists)")
            return True
        except Exception as e:
            logging.error(f"Error creating folder '{folder_name}': {e}")
            raise FolderError(f"Failed to create folder: {e}")

    def delete_folder(self, folder_name: str) -> bool:
        """Delete an email folder and all its messages."""
        self.ensure_connected()
        folder_name = folder_name.strip()
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT id FROM email.folders WHERE name = %s", (folder_name,))
                row = cur.fetchone()
                if row is None:
                    raise FolderError(f"Folder '{folder_name}' not found")
                folder_id = row[0]
                # Delete messages in folder (attachments cascade)
                cur.execute("DELETE FROM email.messages WHERE folder_id = %s", (folder_id,))
                cur.execute("DELETE FROM email.folders WHERE id = %s", (folder_id,))
            logging.info(f"Folder '{folder_name}' deleted")
            return True
        except FolderError:
            raise
        except Exception as e:
            logging.error(f"Error deleting folder '{folder_name}': {e}")
            raise FolderError(f"Failed to delete folder: {e}")

    # ------------------------------------------------------------------
    # Email ID operations
    # ------------------------------------------------------------------

    def get_email_ids(self, folder: str, limit: Optional[int] = None) -> List[str]:
        """Get email IDs from folder (newest first)."""
        self.ensure_connected()
        folder = folder.strip()
        folder_id = self._get_or_create_folder(folder)

        query = (
            "SELECT m.id FROM email.messages m WHERE m.folder_id = %s ORDER BY m.date DESC, m.id DESC"
        )
        params: list = [folder_id]
        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        with self.connection.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        return [str(r[0]) for r in rows]

    # ------------------------------------------------------------------
    # Fetch
    # ------------------------------------------------------------------

    def fetch_email(self, email_id: str) -> EmailMessage:
        """Fetch single email by ID (primary key)."""
        self.ensure_connected()
        msg_pk = int(email_id)

        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                "SELECT m.*, f.name AS folder_name "
                "FROM email.messages m "
                "JOIN email.folders f ON f.id = m.folder_id "
                "WHERE m.id = %s",
                (msg_pk,),
            )
            row = cur.fetchone()
            if row is None:
                raise FolderError(f"Email {email_id} not found")

            # Fetch attachments
            cur.execute(
                "SELECT id, filename, content_type, size, content FROM email.attachments WHERE message_id = %s",
                (msg_pk,),
            )
            att_rows = cur.fetchall()

        attachments = []
        for a in att_rows:
            attachments.append(
                EmailAttachment(
                    filename=a["filename"],
                    content_type=a["content_type"] or "application/octet-stream",
                    size=a["size"] or 0,
                    attachment_id=str(a["id"]),
                    content=bytes(a["content"]) if a["content"] else None,
                )
            )

        date_val = row["date"]
        date_str = date_val.isoformat() if isinstance(date_val, datetime) else str(date_val) if date_val else None

        email_obj = EmailMessage(
            email_id=str(row["id"]),
            subject=row["subject"] or "",
            from_addr=row["from_addr"] or "",
            to_addr=_jsonb_list_to_comma_str(row["to_addr"]),
            cc_addr=_jsonb_list_to_comma_str(row["cc_addr"]) or None,
            bcc_addr=_jsonb_list_to_comma_str(row["bcc_addr"]) or None,
            date=date_str,
            message_id=row["message_id"],
            body_text=row["body_text"],
            body_html=row["body_html"],
            attachments=attachments,
            is_read=row["is_read"],
            is_important=row["is_important"],
            folder=row["folder_name"],
        )
        return email_obj

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_emails(self, query: str, folder: str = None) -> List[str]:
        """Search emails using PostgreSQL full-text search on subject and body_text."""
        self.ensure_connected()

        # Build tsquery from the raw query string.
        # Split into words and join with '&' for AND semantics.
        words = query.strip().split()
        if not words:
            return []
        ts_query_str = " & ".join(words)

        sql = (
            "SELECT m.id FROM email.messages m "
        )
        params: list = []

        if folder:
            folder = folder.strip()
            folder_id = self._get_or_create_folder(folder)
            sql += "WHERE m.folder_id = %s AND "
            params.append(folder_id)
        else:
            sql += "WHERE "

        sql += (
            "to_tsvector('simple', COALESCE(m.subject, '') || ' ' || COALESCE(m.body_text, '')) "
            "@@ to_tsquery('simple', %s) "
            "ORDER BY m.date DESC, m.id DESC"
        )
        params.append(ts_query_str)

        with self.connection.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [str(r[0]) for r in rows]

    # ------------------------------------------------------------------
    # Flag operations
    # ------------------------------------------------------------------

    def mark_as_read(self, email_id: str) -> bool:
        self.ensure_connected()
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    "UPDATE email.messages SET is_read = TRUE WHERE id = %s", (int(email_id),)
                )
            return True
        except Exception as e:
            logging.error(f"Error marking email {email_id} as read: {e}")
            return False

    def mark_as_unread(self, email_id: str) -> bool:
        self.ensure_connected()
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    "UPDATE email.messages SET is_read = FALSE WHERE id = %s", (int(email_id),)
                )
            return True
        except Exception as e:
            logging.error(f"Error marking email {email_id} as unread: {e}")
            return False

    def mark_as_important(self, email_id: str) -> bool:
        self.ensure_connected()
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    "UPDATE email.messages SET is_important = TRUE WHERE id = %s", (int(email_id),)
                )
            return True
        except Exception as e:
            logging.error(f"Error marking email {email_id} as important: {e}")
            return False

    def mark_as_not_important(self, email_id: str) -> bool:
        self.ensure_connected()
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    "UPDATE email.messages SET is_important = FALSE WHERE id = %s", (int(email_id),)
                )
            return True
        except Exception as e:
            logging.error(f"Error removing important flag from email {email_id}: {e}")
            return False

    # ------------------------------------------------------------------
    # Delete / Move / Append
    # ------------------------------------------------------------------

    def delete_email(self, email_id: str):
        """Delete email from database."""
        self.ensure_connected()
        try:
            with self.connection.cursor() as cur:
                cur.execute("DELETE FROM email.messages WHERE id = %s", (int(email_id),))
        except Exception as e:
            logging.error(f"Error deleting email {email_id}: {e}")
            raise FolderError(f"Failed to delete email: {e}")

    def move_email(self, email_id: str, target_folder: str) -> Optional[str]:
        """Move email to another folder. Returns None (consistent with IMAP backend)."""
        self.ensure_connected()
        target_folder = target_folder.strip()
        target_folder_id = self._get_or_create_folder(target_folder)

        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    "UPDATE email.messages SET folder_id = %s WHERE id = %s",
                    (target_folder_id, int(email_id)),
                )
            logging.info(f"Moved email {email_id} to folder '{target_folder}'")
            return None
        except Exception as e:
            logging.error(f"Error moving email {email_id} to {target_folder}: {e}")
            raise FolderError(f"Failed to move email: {e}")

    def append_message(self, folder: str, message: str, flags: str = "\\Seen") -> bool:
        """Parse an RFC822 message string and insert it into the specified folder."""
        self.ensure_connected()
        folder = folder.strip()
        folder_id = self._get_or_create_folder(folder)

        try:
            parser = Parser(policy=policy.default)
            msg = parser.parsestr(message)

            subject = msg.get("Subject", "")
            from_addr = msg.get("From", "")
            to_addr = msg.get("To", "")
            cc_addr = msg.get("Cc", "")
            bcc_addr = msg.get("Bcc", "")
            message_id_hdr = msg.get("Message-ID", None)
            in_reply_to = msg.get("In-Reply-To", None)
            references_hdr = msg.get("References", None)
            date_hdr = msg.get("Date", None)

            # Extract body
            body_text = None
            body_html = None
            if msg.is_multipart():
                for part in msg.walk():
                    ct = part.get_content_type()
                    if ct == "text/plain" and body_text is None:
                        body_text = part.get_content()
                    elif ct == "text/html" and body_html is None:
                        body_html = part.get_content()
            else:
                ct = msg.get_content_type()
                content = msg.get_content()
                if ct == "text/html":
                    body_html = content
                else:
                    body_text = content

            is_read = "\\Seen" in flags
            is_flagged = "\\Flagged" in flags

            to_list = _comma_str_to_jsonb_list(to_addr)
            cc_list = _comma_str_to_jsonb_list(cc_addr)
            bcc_list = _comma_str_to_jsonb_list(bcc_addr)

            with self.connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO email.messages "
                    "(folder_id, message_id, subject, from_addr, to_addr, cc_addr, bcc_addr, "
                    "date, body_text, body_html, is_read, is_flagged, in_reply_to, references_header, "
                    "size) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, "
                    "COALESCE(%s::timestamptz, NOW()), %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id",
                    (
                        folder_id,
                        message_id_hdr,
                        subject,
                        from_addr,
                        json.dumps(to_list),
                        json.dumps(cc_list),
                        json.dumps(bcc_list),
                        date_hdr,
                        body_text,
                        body_html,
                        is_read,
                        is_flagged,
                        in_reply_to,
                        references_hdr,
                        len(message),
                    ),
                )
                new_id = cur.fetchone()[0]

            # Handle attachments from multipart message
            if msg.is_multipart():
                for part in msg.iter_attachments():
                    filename = part.get_filename() or "attachment"
                    content_type = part.get_content_type()
                    payload = part.get_payload(decode=True)
                    size = len(payload) if payload else 0
                    content_id = part.get("Content-ID", None)
                    with self.connection.cursor() as cur:
                        cur.execute(
                            "INSERT INTO email.attachments "
                            "(message_id, filename, content_type, size, content, content_id) "
                            "VALUES (%s, %s, %s, %s, %s, %s)",
                            (new_id, filename, content_type, size,
                             psycopg2.Binary(payload) if payload else None, content_id),
                        )

            logging.info(f"Message appended to folder '{folder}' with id {new_id}")
            return True

        except Exception as e:
            logging.error(f"Error appending message to folder '{folder}': {e}")
            raise FolderError(f"Failed to append message to {folder}: {e}")


class PgSMTPBackend:
    """PostgreSQL-backed SMTP replacement backend.

    Instead of actually sending emails over SMTP, this backend inserts
    the message into the ``email.messages`` table (in the 'Sent' folder)
    and logs the send in ``email.sent_log``.
    """

    def __init__(self, config: EmailConfig):
        self.config = config
        self.connection = None  # psycopg2 connection

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> bool:
        """Establish PostgreSQL connection."""
        try:
            self.connection = psycopg2.connect(**_get_pg_conn_params())
            self.connection.autocommit = True
            logging.info("PgSMTPBackend connected to PostgreSQL")
            return True
        except Exception as e:
            logging.error(f"PgSMTPBackend connection failed: {e}")
            raise ConnectionError(f"PostgreSQL connection failed: {e}")

    def disconnect(self):
        """Close PostgreSQL connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            finally:
                self.connection = None

    def ensure_connected(self):
        """Ensure PostgreSQL connection is active."""
        if self.connection is None or self.connection.closed:
            self.connect()
            return
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT 1")
        except Exception:
            logging.warning("PgSMTPBackend connection lost, reconnecting...")
            self.disconnect()
            self.connect()

    # ------------------------------------------------------------------
    # Send (insert into DB)
    # ------------------------------------------------------------------

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> tuple:
        """Compose and 'send' an email by inserting into the database.

        Returns:
            tuple[bool, Optional[str]]: (success, RFC822 message string)
        """
        self.ensure_connected()

        try:
            # ---- Build the MIME message (for the returned RFC822 string) ----
            if html_body or attachments:
                msg = MIMEMultipart("alternative" if html_body and not attachments else "mixed")
                text_part = MIMEText(body, "plain", "utf-8")
                msg.attach(text_part)
                if html_body:
                    html_part = MIMEText(html_body, "html", "utf-8")
                    msg.attach(html_part)
            else:
                msg = MIMEText(body, "plain", "utf-8")

            from email.header import Header

            msg["Subject"] = Header(subject, "utf-8")
            if self.config.name:
                encoded_name = Header(self.config.name, "utf-8")
                msg["From"] = formataddr((str(encoded_name), self.config.email))
            else:
                msg["From"] = self.config.email
            msg["To"] = to
            if cc:
                msg["Cc"] = cc
            if bcc:
                msg["Bcc"] = bcc
            msg["Date"] = formatdate(localtime=True)
            msg["Message-ID"] = make_msgid()

            # Attachments
            attachment_data_list = []
            if attachments:
                if not isinstance(msg, MIMEMultipart):
                    original_msg = msg
                    msg = MIMEMultipart("mixed")
                    msg["Subject"] = Header(subject, "utf-8")
                    if self.config.name:
                        msg["From"] = formataddr((self.config.name, self.config.email))
                    else:
                        msg["From"] = self.config.email
                    msg["To"] = to
                    if cc:
                        msg["Cc"] = cc
                    if bcc:
                        msg["Bcc"] = bcc
                    msg.attach(original_msg)

                for file_path in attachments:
                    filename = os.path.basename(file_path)
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    attachment_data_list.append((filename, "application/octet-stream", file_data))

                    att = MIMEBase("application", "octet-stream")
                    att.set_payload(file_data)
                    encoders.encode_base64(att)
                    att.add_header("Content-Disposition", f"attachment; filename= {filename}")
                    msg.attach(att)

            message_string = msg.as_string()

            # ---- Insert into database ----
            to_list = _comma_str_to_jsonb_list(to)
            cc_list = _comma_str_to_jsonb_list(cc)
            bcc_list = _comma_str_to_jsonb_list(bcc)

            # Ensure 'Sent' folder exists
            with self.connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO email.folders (name) VALUES ('Sent') "
                    "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name "
                    "RETURNING id"
                )
                sent_folder_id = cur.fetchone()[0]

                cur.execute(
                    "INSERT INTO email.messages "
                    "(folder_id, message_id, subject, from_addr, to_addr, cc_addr, bcc_addr, "
                    "date, body_text, body_html, is_read, size) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, TRUE, %s) "
                    "RETURNING id",
                    (
                        sent_folder_id,
                        msg["Message-ID"],
                        subject,
                        msg["From"],
                        json.dumps(to_list),
                        json.dumps(cc_list),
                        json.dumps(bcc_list),
                        body,
                        html_body,
                        len(message_string),
                    ),
                )
                new_msg_id = cur.fetchone()[0]

                # Insert attachments
                for filename, content_type, file_data in attachment_data_list:
                    cur.execute(
                        "INSERT INTO email.attachments "
                        "(message_id, filename, content_type, size, content) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (new_msg_id, filename, content_type, len(file_data),
                         psycopg2.Binary(file_data)),
                    )

                # Log to sent_log
                cur.execute(
                    "INSERT INTO email.sent_log (message_id) VALUES (%s)",
                    (new_msg_id,),
                )

            logging.info(f"Email 'sent' (stored) to {to} with id {new_msg_id}")
            return True, message_string

        except Exception as e:
            logging.error(f"Error sending email: {e}")
            raise SendEmailError(f"Failed to send email: {e}")

    # ------------------------------------------------------------------
    # Test connection
    # ------------------------------------------------------------------

    def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
        try:
            self.ensure_connected()
            return True
        except Exception:
            return False


class PgDraftBackend:
    """PostgreSQL-backed draft storage."""

    def __init__(self):
        self.connection = None

    def _ensure_connected(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(**_get_pg_conn_params())
            self.connection.autocommit = True

    def save_draft(self, subject, body, html_body=None, to=None, cc=None, bcc=None, from_addr=None):
        self._ensure_connected()
        to_list = _comma_str_to_jsonb_list(to)
        cc_list = _comma_str_to_jsonb_list(cc)
        bcc_list = _comma_str_to_jsonb_list(bcc)
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO email.drafts (subject, from_addr, to_addr, cc_addr, bcc_addr, body_text, body_html) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (subject, from_addr, json.dumps(to_list), json.dumps(cc_list), json.dumps(bcc_list), body, html_body),
            )
            return str(cur.fetchone()[0])

    def get_drafts(self, page=1, page_size=20):
        self._ensure_connected()
        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT COUNT(*) FROM email.drafts")
            total = cur.fetchone()[0]
            offset = (page - 1) * page_size
            cur.execute(
                "SELECT * FROM email.drafts ORDER BY updated_at DESC LIMIT %s OFFSET %s",
                (page_size, offset),
            )
            rows = cur.fetchall()
        total_pages = max(1, (total + page_size - 1) // page_size)
        drafts = []
        for r in rows:
            drafts.append({
                'draft_id': str(r['id']),
                'subject': r['subject'] or '',
                'to': _jsonb_list_to_comma_str(r['to_addr']),
                'cc': _jsonb_list_to_comma_str(r['cc_addr']),
                'bcc': _jsonb_list_to_comma_str(r['bcc_addr']),
                'body': r['body_text'] or '',
                'html_body': r['body_html'],
                'created_at': r['created_at'].isoformat() if r['created_at'] else '',
                'updated_at': r['updated_at'].isoformat() if r['updated_at'] else '',
            })
        return {'drafts': drafts, 'total_drafts': total, 'current_page': page, 'total_pages': total_pages, 'page_size': page_size}

    def get_draft(self, draft_id):
        self._ensure_connected()
        with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM email.drafts WHERE id = %s", (int(draft_id),))
            r = cur.fetchone()
            if r is None:
                raise FolderError(f"Draft not found: {draft_id}")
        return {
            'draft_id': str(r['id']),
            'subject': r['subject'] or '',
            'to': _jsonb_list_to_comma_str(r['to_addr']),
            'cc': _jsonb_list_to_comma_str(r['cc_addr']),
            'bcc': _jsonb_list_to_comma_str(r['bcc_addr']),
            'body': r['body_text'] or '',
            'html_body': r['body_html'],
            'created_at': r['created_at'].isoformat() if r['created_at'] else '',
            'updated_at': r['updated_at'].isoformat() if r['updated_at'] else '',
        }

    def update_draft(self, draft_id, subject=None, body=None, html_body=None, to=None, cc=None, bcc=None):
        self._ensure_connected()
        sets = ["updated_at = NOW()"]
        params = []
        if subject is not None:
            sets.append("subject = %s"); params.append(subject)
        if body is not None:
            sets.append("body_text = %s"); params.append(body)
        if html_body is not None:
            sets.append("body_html = %s"); params.append(html_body)
        if to is not None:
            sets.append("to_addr = %s"); params.append(json.dumps(_comma_str_to_jsonb_list(to)))
        if cc is not None:
            sets.append("cc_addr = %s"); params.append(json.dumps(_comma_str_to_jsonb_list(cc)))
        if bcc is not None:
            sets.append("bcc_addr = %s"); params.append(json.dumps(_comma_str_to_jsonb_list(bcc)))
        params.append(int(draft_id))
        with self.connection.cursor() as cur:
            cur.execute(f"UPDATE email.drafts SET {', '.join(sets)} WHERE id = %s", params)
            if cur.rowcount == 0:
                raise FolderError(f"Draft not found: {draft_id}")
        return True

    def delete_draft(self, draft_id):
        self._ensure_connected()
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM email.drafts WHERE id = %s", (int(draft_id),))
            if cur.rowcount == 0:
                raise FolderError(f"Draft not found: {draft_id}")
        return True
