#!/usr/bin/env python3
"""
Banking Database Backup Script
Backs up PostgreSQL database to AWS S3
"""

import os
import subprocess
import boto3
from datetime import datetime
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Configuration
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5433')

# Get S3 bucket name from Terraform output
# You'll set this after running terraform
S3_BUCKET = os.getenv('S3_BACKUP_BUCKET')
AWS_PROFILE = os.getenv('AWS_BACKUP_PROFILE', 'banking-backup')

# Local backup directory
BACKUP_DIR = os.path.join(os.path.dirname(__file__), '../db_backups')
os.makedirs(BACKUP_DIR, exist_ok=True)


def create_backup():
    """Create PostgreSQL dump file using Docker container's pg_dump"""
    timestamp = datetime.now().strftime('%Y%m%d')
    backup_filename = f'{timestamp}_banking_db.backup'
    backup_file = os.path.join(BACKUP_DIR, backup_filename)

    # Path inside container (mapped to ../db_backups on host)
    container_backup_path = f'/backups/{backup_filename}'

    print(f"Creating backup: {backup_file}")

    try:
        # Run pg_dump inside the Docker container
        # Container has PostgreSQL 17.x which matches the server version
        cmd = [
            'docker', 'exec',
            '-e', f'PGPASSWORD={POSTGRES_PASSWORD}',
            'banking_db',  # Container name
            'pg_dump',
            '-U', POSTGRES_USER,
            '-d', POSTGRES_DB,
            '-F', 'c',  # Custom format (compressed)
            '-f', container_backup_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error creating backup: {result.stderr}")
            sys.exit(1)

        print(f"✅ Backup created successfully: {backup_file}")
        return backup_file

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def upload_to_s3(backup_file):
    """Upload backup file to S3"""
    if not S3_BUCKET:
        print("⚠️  S3_BACKUP_BUCKET not set, skipping upload")
        print("   Set it in .env or export S3_BACKUP_BUCKET=your-bucket-name")
        return

    try:
        # Create boto3 session with profile
        session = boto3.Session(profile_name=AWS_PROFILE)
        s3 = session.client('s3')

        # Upload file
        filename = os.path.basename(backup_file)
        s3_key = f"backups/{filename}"

        print(f"Uploading to S3: s3://{S3_BUCKET}/{s3_key}")

        with open(backup_file, 'rb') as f:
            s3.upload_fileobj(f, S3_BUCKET, s3_key)

        print(f"✅ Uploaded successfully to S3")

        # Optional: Delete local backup after successful upload
        # os.remove(backup_file)
        # print(f"🗑️  Removed local backup: {backup_file}")

    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        sys.exit(1)


def cleanup_old_backups(keep_days=7):
    """Delete local backups older than keep_days"""
    import time

    cutoff_time = time.time() - (keep_days * 86400)

    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith('_banking_db.backup'):
            filepath = os.path.join(BACKUP_DIR, filename)
            file_time = os.path.getmtime(filepath)

            if file_time < cutoff_time:
                os.remove(filepath)
                print(f"🗑️  Deleted old backup: {filename}")


def main():
    print("=" * 60)
    print("Banking Database Backup")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Create backup
    backup_file = create_backup()

    # 2. Upload to S3 (always upload - storage is cheap and versioning handles duplicates)
    upload_to_s3(backup_file)

    # # 3. Cleanup old local backups
    # cleanup_old_backups(keep_days=7)

    print("=" * 60)
    print("✅ Backup process completed")
    print("=" * 60)


if __name__ == '__main__':
    main()