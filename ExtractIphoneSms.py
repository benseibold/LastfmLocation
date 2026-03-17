"""
Extract SMS messages from iPhone backup and convert to XML format.

This script:
1. Finds the most recent iPhone backup on Windows
2. Extracts messages from the sms.db SQLite database
3. Converts to XML format compatible with DigitalJournal.py

Usage:
    python ExtractIphoneSms.py

Output:
    Data/SmsData.xml - SMS messages in XML format
"""

import sqlite3
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path


def find_latest_backup():
    """Find the most recent iPhone backup folder."""
    backup_path = Path(r'C:\Users\Ben\Apple\MobileSync\Backup\00008150-001C31490A7A401C')

    if not backup_path.exists():
        raise FileNotFoundError(f"iTunes backup folder not found at: {backup_path}")

    print(f"Found backup: {backup_path.name}")
    print(f"Last modified: {datetime.fromtimestamp(backup_path.stat().st_mtime)}")

    return backup_path


def find_sms_database(backup_folder):
    """Locate the SMS database file in the backup."""
    # The SMS database has a specific hash in iPhone backups
    sms_db_path = backup_folder / '3d' / '3d0d7e5fb2ce288813306e4d4636395e047a3d28'

    if not sms_db_path.exists():
        raise FileNotFoundError(f"SMS database not found at: {sms_db_path}")

    return sms_db_path


def extract_messages(db_path):
    """Extract messages from the SMS database."""
    print(f"\nConnecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to get messages with contact information
    # The message table has: ROWID, text, date, is_from_me, handle_id
    # The handle table has: ROWID, id (phone number/email)
    query = """
    SELECT
        message.text,
        message.date,
        message.is_from_me,
        handle.id as contact
    FROM message
    LEFT JOIN handle ON message.handle_id = handle.ROWID
    ORDER BY message.date ASC
    """

    cursor.execute(query)
    messages = cursor.fetchall()

    print(f"Found {len(messages)} messages")

    conn.close()

    return messages


def apple_timestamp_to_unix_ms(apple_timestamp):
    """
    Convert Apple's timestamp to Unix epoch milliseconds.

    Apple uses seconds since 2001-01-01 00:00:00 UTC
    Unix uses milliseconds since 1970-01-01 00:00:00 UTC
    """
    if apple_timestamp is None:
        return 0

    # Apple epoch starts at 2001-01-01 (978307200 seconds after Unix epoch)
    # Convert nanoseconds to seconds, add offset, then convert to milliseconds
    unix_timestamp = (apple_timestamp / 1000000000) + 978307200
    return int(unix_timestamp * 1000)


def normalize_contact(contact_id):
    """Normalize contact identifier (phone number or email)."""
    if not contact_id:
        return "Unknown"

    # Remove common phone number formatting
    contact_id = contact_id.replace('+1', '').replace('-', '').replace('(', '').replace(')', '').replace(' ', '')

    return contact_id


def indent_xml(elem, level=0):
    """Pretty print XML (compatible with Python < 3.9)."""
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_xml(messages, output_path):
    """Create XML file from messages."""
    root = ET.Element('smses', count=str(len(messages)))

    for text, apple_date, is_from_me, contact in messages:
        # Convert timestamp
        unix_ms = apple_timestamp_to_unix_ms(apple_date)

        # Determine message type (1=received, 2=sent)
        msg_type = '2' if is_from_me else '1'

        # Normalize contact
        contact_name = normalize_contact(contact)

        # Create SMS element
        sms = ET.SubElement(root, 'sms')
        sms.set('body', text or '')
        sms.set('date', str(unix_ms))
        sms.set('type', msg_type)
        sms.set('contact_name', contact_name)

    # Create the tree and write to file
    tree = ET.ElementTree(root)

    # Pretty print - compatible with older Python versions
    indent_xml(root)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"\nWrote {len(messages)} messages to {output_path}")


def main():
    """Main execution function."""
    try:
        print("iPhone SMS Extractor")
        print("=" * 50)

        # Find the latest backup
        backup_folder = find_latest_backup()

        # Find the SMS database
        sms_db = find_sms_database(backup_folder)

        # Extract messages
        messages = extract_messages(sms_db)

        if not messages:
            print("\nNo messages found in backup!")
            return

        # Create XML output
        output_path = Path('Data/SmsData.xml')
        create_xml(messages, output_path)

        print("\n" + "=" * 50)
        print("Extraction complete!")
        print(f"First message: {datetime.fromtimestamp(apple_timestamp_to_unix_ms(messages[0][1]) / 1000)}")
        print(f"Last message: {datetime.fromtimestamp(apple_timestamp_to_unix_ms(messages[-1][1]) / 1000)}")

        # Print sample of messages
        print("\n" + "=" * 50)
        print("Sample Messages (first 10):")
        print("=" * 50)
        print(f"{'Date':<20} {'Type':<10} {'Contact':<20} {'Message':<50}")
        print("-" * 100)

        for text, apple_date, is_from_me, contact in messages[:10]:
            unix_ms = apple_timestamp_to_unix_ms(apple_date)
            date_str = datetime.fromtimestamp(unix_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
            msg_type = 'Sent' if is_from_me else 'Received'
            contact_name = normalize_contact(contact)
            message_preview = (text or '')[:50]

            print(f"{date_str:<20} {msg_type:<10} {contact_name:<20} {message_preview:<50}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
