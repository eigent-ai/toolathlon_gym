import argparse
import json
import os
import uuid
import psycopg2

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": 5432,
    "dbname": os.environ.get("PGDATABASE", "toolathlon_gym"),
    "user": "eigent",
    "password": "camel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent_workspace", required=False)
    parser.add_argument("--launch_time", required=False)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Clear email schema
        cur.execute("DELETE FROM email.attachments")
        cur.execute("DELETE FROM email.sent_log")
        cur.execute("DELETE FROM email.messages")

        # Ensure folders exist
        cur.execute("DELETE FROM email.folders")
        cur.execute(
            "INSERT INTO email.folders (id, name) VALUES (1, 'INBOX'), (2, 'Sent'), (3, 'Drafts')"
        )

        # Inject noise emails
        noise_emails = [
            {
                "folder_id": 1,
                "message_id": str(uuid.uuid4()),
                "subject": "Weekly Bookstore Inventory Update",
                "from_addr": "inventory@university.edu",
                "to_addr": json.dumps(["bookstore_manager@university.edu"]),
                "date": "2025-11-01 09:00:00",
                "body_text": "This week's inventory report shows normal stock levels across all departments.",
                "is_read": True,
            },
            {
                "folder_id": 1,
                "message_id": str(uuid.uuid4()),
                "subject": "Campus Event: Tech Fair Next Month",
                "from_addr": "events@university.edu",
                "to_addr": json.dumps(["all_staff@university.edu"]),
                "date": "2025-10-28 14:30:00",
                "body_text": "Join us for the annual tech fair showcasing student projects and new electronics.",
                "is_read": True,
            },
            {
                "folder_id": 1,
                "message_id": str(uuid.uuid4()),
                "subject": "Re: Textbook Orders for Spring Semester",
                "from_addr": "academic_affairs@university.edu",
                "to_addr": json.dumps(["bookstore_manager@university.edu"]),
                "date": "2025-10-20 11:15:00",
                "body_text": "Please confirm the textbook order list for the upcoming spring semester courses.",
                "is_read": False,
            },
            {
                "folder_id": 2,
                "message_id": str(uuid.uuid4()),
                "subject": "Supplier Quote: Electronics Batch",
                "from_addr": "bookstore_manager@university.edu",
                "to_addr": json.dumps(["supplier@techvendor.com"]),
                "date": "2025-10-15 16:00:00",
                "body_text": "Requesting updated quotes for our next electronics inventory batch.",
                "is_read": True,
            },
            {
                "folder_id": 1,
                "message_id": str(uuid.uuid4()),
                "subject": "Student Discount Program Proposal",
                "from_addr": "marketing@university.edu",
                "to_addr": json.dumps(["bookstore_manager@university.edu"]),
                "date": "2025-10-10 08:45:00",
                "body_text": "Attached is the draft proposal for the student discount program. Please review.",
                "is_read": True,
            },
        ]

        for e in noise_emails:
            cur.execute(
                """INSERT INTO email.messages
                (folder_id, message_id, subject, from_addr, to_addr, date, body_text, is_read)
                VALUES (%(folder_id)s, %(message_id)s, %(subject)s, %(from_addr)s,
                        %(to_addr)s::jsonb, %(date)s, %(body_text)s, %(is_read)s)""",
                e,
            )

        conn.commit()
        print("Preprocess completed: email schema cleared and noise emails injected.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
