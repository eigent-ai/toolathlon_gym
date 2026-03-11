from typing import List
import logging
from ..models.email import EmailFolder, MailboxStats
from ..utils.exceptions import EmailMCPError, FolderError
from ..utils.validators import validate_folder_name

class FolderService:
    """Folder management service layer"""

    def __init__(self, imap_backend):
        self.imap_backend = imap_backend

    def get_folders(self) -> List[EmailFolder]:
        """Get list of all email folders"""
        try:
            return self.imap_backend.list_folders()
        except Exception as e:
            raise EmailMCPError(f"Failed to get folders: {str(e)}")

    def create_folder(self, folder_name: str) -> bool:
        """Create new email folder"""
        # Validate folder name
        valid, error = validate_folder_name(folder_name)
        if not valid:
            raise FolderError(error)

        try:
            return self.imap_backend.create_folder(folder_name)
        except FolderError:
            raise
        except Exception as e:
            raise FolderError(f"Failed to create folder: {str(e)}")

    def delete_folder(self, folder_name: str) -> bool:
        """Delete email folder"""
        # Validate folder name
        valid, error = validate_folder_name(folder_name)
        if not valid:
            raise FolderError(error)

        # Prevent deletion of system folders
        system_folders = ['INBOX', 'Sent', 'Drafts', 'Trash', 'Spam']
        if folder_name.strip() in system_folders:
            raise FolderError(f"Cannot delete system folder: {folder_name}")

        try:
            return self.imap_backend.delete_folder(folder_name)
        except FolderError:
            raise
        except Exception as e:
            raise FolderError(f"Failed to delete folder: {str(e)}")

    def get_folder_stats(self, folder_name: str) -> MailboxStats:
        """Get statistics for specific folder"""
        try:
            folder_name = folder_name.strip()
            total_messages, unread_messages = self.imap_backend.select_folder(folder_name)

            return MailboxStats(
                folder_name=folder_name,
                total_messages=total_messages,
                unread_messages=unread_messages
            )

        except Exception as e:
            raise EmailMCPError(f"Failed to get folder stats: {str(e)}")

    def get_unread_count(self, folder_name: str = None) -> int:
        """Get unread message count for folder or all folders"""
        try:
            if folder_name:
                folder_name = folder_name.strip()
                _, unread_count = self.imap_backend.select_folder(folder_name)
                return unread_count
            else:
                # Get unread count for all folders
                folders = self.get_folders()
                total_unread = 0
                for folder in folders:
                    if folder.can_select:
                        total_unread += folder.unread_messages
                return total_unread

        except Exception as e:
            raise EmailMCPError(f"Failed to get unread count: {str(e)}")