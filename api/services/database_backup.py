"""
Database Backup and Security Service
Automated backup, encryption, and security features for database management
"""

import os
import subprocess
import asyncio
import gzip
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from cryptography.fernet import Fernet
from sqlalchemy import text
from pydantic import BaseModel

from core.database_manager import get_db_manager
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    SCHEMA_ONLY = "schema_only"
    DATA_ONLY = "data_only"


class BackupStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackupInfo:
    """Database backup information"""

    id: str
    backup_type: BackupType
    file_path: str
    file_size: int
    status: BackupStatus
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    checksum: Optional[str]
    encrypted: bool


class DatabaseBackupService:
    """Automated database backup and recovery system"""

    def __init__(self):
        self.backup_dir = Path(getattr(settings, "BACKUP_DIR", "./backups"))
        self.backup_dir.mkdir(exist_ok=True)

        # Encryption setup
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)

        # Backup configuration
        self.max_backups = getattr(settings, "MAX_BACKUPS", 30)
        self.compression_enabled = getattr(settings, "BACKUP_COMPRESSION", True)
        self.encryption_enabled = getattr(settings, "BACKUP_ENCRYPTION", True)

        self.backup_history: List[BackupInfo] = []

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for backups"""
        key_file = self.backup_dir / ".backup_key"

        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            key_file.chmod(0o600)  # Restrict permissions
            logger.info("Created new backup encryption key")
            return key

    async def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        custom_name: Optional[str] = None,
    ) -> BackupInfo:
        """Create a database backup"""
        timestamp = datetime.utcnow()
        backup_id = f"{backup_type.value}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        if custom_name:
            backup_id = f"{custom_name}_{backup_id}"

        file_name = f"{backup_id}.sql"
        if self.compression_enabled:
            file_name += ".gz"
        if self.encryption_enabled:
            file_name += ".enc"

        file_path = self.backup_dir / file_name

        backup_info = BackupInfo(
            id=backup_id,
            backup_type=backup_type,
            file_path=str(file_path),
            file_size=0,
            status=BackupStatus.PENDING,
            created_at=timestamp,
            completed_at=None,
            error_message=None,
            checksum=None,
            encrypted=self.encryption_enabled,
        )

        self.backup_history.append(backup_info)

        try:
            backup_info.status = BackupStatus.IN_PROGRESS

            # Create database dump
            dump_content = await self._create_database_dump(backup_type)

            # Process backup file (compression, encryption)
            final_content = await self._process_backup_content(dump_content)

            # Write to file
            file_path.write_bytes(final_content)

            # Calculate file size and checksum
            backup_info.file_size = file_path.stat().st_size
            backup_info.checksum = self._calculate_checksum(final_content)
            backup_info.status = BackupStatus.COMPLETED
            backup_info.completed_at = datetime.utcnow()

            logger.info(f"Backup created successfully: {backup_id}")

            # Cleanup old backups
            await self._cleanup_old_backups()

        except Exception as e:
            backup_info.status = BackupStatus.FAILED
            backup_info.error_message = str(e)
            logger.error(f"Backup creation failed: {e}")

            # Remove partial backup file
            if file_path.exists():
                file_path.unlink()

        return backup_info

    async def _create_database_dump(self, backup_type: BackupType) -> bytes:
        """Create database dump using pg_dump"""
        try:
            db_config = {
                "host": settings.DATABASE_HOST,
                "port": settings.DATABASE_PORT,
                "database": settings.DATABASE_NAME,
                "username": settings.DATABASE_USER,
                "password": settings.DATABASE_PASSWORD,
            }

            # Build pg_dump command
            cmd = [
                "pg_dump",
                f"--host={db_config['host']}",
                f"--port={db_config['port']}",
                f"--username={db_config['username']}",
                f"--dbname={db_config['database']}",
                "--no-password",
                "--verbose",
                "--clean",
                "--if-exists",
            ]

            # Add backup type specific options
            if backup_type == BackupType.SCHEMA_ONLY:
                cmd.append("--schema-only")
            elif backup_type == BackupType.DATA_ONLY:
                cmd.append("--data-only")

            # Set environment for password
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config["password"]

            # Execute pg_dump
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8") if stderr else "Unknown error"
                raise Exception(f"pg_dump failed: {error_msg}")

            return stdout

        except Exception as e:
            logger.error(f"Database dump creation failed: {e}")
            raise

    async def _process_backup_content(self, content: bytes) -> bytes:
        """Process backup content with compression and encryption"""
        processed_content = content

        # Apply compression
        if self.compression_enabled:
            processed_content = gzip.compress(processed_content)
            logger.debug("Backup compressed")

        # Apply encryption
        if self.encryption_enabled:
            processed_content = self.cipher_suite.encrypt(processed_content)
            logger.debug("Backup encrypted")

        return processed_content

    def _calculate_checksum(self, content: bytes) -> str:
        """Calculate SHA-256 checksum of backup content"""
        return hashlib.sha256(content).hexdigest()

    async def restore_backup(self, backup_id: str) -> bool:
        """Restore database from backup"""
        backup_info = self._find_backup(backup_id)
        if not backup_info:
            raise ValueError(f"Backup not found: {backup_id}")

        if backup_info.status != BackupStatus.COMPLETED:
            raise ValueError(f"Backup is not in completed status: {backup_info.status}")

        try:
            # Read and process backup file
            backup_path = Path(backup_info.file_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")

            file_content = backup_path.read_bytes()

            # Verify checksum
            if backup_info.checksum:
                current_checksum = self._calculate_checksum(file_content)
                if current_checksum != backup_info.checksum:
                    raise ValueError("Backup file checksum verification failed")

            # Decrypt and decompress
            processed_content = await self._restore_backup_content(file_content)

            # Execute SQL restore
            await self._execute_restore(processed_content)

            logger.info(f"Database restored successfully from backup: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            raise

    async def _restore_backup_content(self, content: bytes) -> str:
        """Restore backup content by reversing encryption and compression"""
        processed_content = content

        # Reverse encryption
        if self.encryption_enabled:
            processed_content = self.cipher_suite.decrypt(processed_content)
            logger.debug("Backup decrypted")

        # Reverse compression
        if self.compression_enabled:
            processed_content = gzip.decompress(processed_content)
            logger.debug("Backup decompressed")

        return processed_content.decode("utf-8")

    async def _execute_restore(self, sql_content: str):
        """Execute SQL content to restore database"""
        db_manager = await get_db_manager()

        # Split SQL content into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        async with db_manager.get_session() as session:
            for statement in statements:
                if statement:
                    await session.execute(text(statement))

    def _find_backup(self, backup_id: str) -> Optional[BackupInfo]:
        """Find backup by ID"""
        for backup in self.backup_history:
            if backup.id == backup_id:
                return backup
        return None

    async def _cleanup_old_backups(self):
        """Remove old backups beyond retention limit"""
        if len(self.backup_history) <= self.max_backups:
            return

        # Sort by creation date and keep only recent ones
        sorted_backups = sorted(self.backup_history, key=lambda x: x.created_at)
        old_backups = sorted_backups[: -self.max_backups]

        for backup in old_backups:
            try:
                backup_path = Path(backup.file_path)
                if backup_path.exists():
                    backup_path.unlink()
                    logger.debug(f"Removed old backup: {backup.id}")
            except Exception as e:
                logger.warning(f"Failed to remove old backup {backup.id}: {e}")

        # Update backup history
        self.backup_history = sorted_backups[-self.max_backups :]

    async def list_backups(self) -> List[BackupInfo]:
        """List all available backups"""
        return sorted(self.backup_history, key=lambda x: x.created_at, reverse=True)

    async def get_backup_info(self, backup_id: str) -> Optional[BackupInfo]:
        """Get detailed backup information"""
        return self._find_backup(backup_id)

    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a specific backup"""
        backup_info = self._find_backup(backup_id)
        if not backup_info:
            return False

        try:
            backup_path = Path(backup_info.file_path)
            if backup_path.exists():
                backup_path.unlink()

            self.backup_history.remove(backup_info)
            logger.info(f"Backup deleted: {backup_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False

    async def schedule_automated_backups(self):
        """Schedule automated backup creation"""
        # This would integrate with a task scheduler like Celery
        logger.info("Automated backup scheduling would be implemented here")

        # Example: Create daily full backup
        # await self.create_backup(BackupType.FULL, "daily_auto")


class DatabaseSecurity:
    """Database security and compliance management"""

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    async def audit_user_access(
        self, user_id: str, action: str, table: str, details: Dict[str, Any] = None
    ):
        """Log user access for audit trail"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "table": table,
            "details": details or {},
            "ip_address": details.get("ip_address") if details else None,
        }

        self.audit_log.append(audit_entry)

        # Store in database audit table
        db_manager = await get_db_manager()
        async with db_manager.get_session() as session:
            await session.execute(
                text(
                    """
                INSERT INTO user_activity 
                (user_id, action, table_name, details, created_at)
                VALUES (:user_id, :action, :table_name, :details, :created_at)
            """
                ),
                {
                    "user_id": user_id,
                    "action": action,
                    "table_name": table,
                    "details": json.dumps(audit_entry["details"]),
                    "created_at": datetime.utcnow(),
                },
            )

    async def check_sensitive_data_access(self, query: str, user_id: str) -> bool:
        """Check if query accesses sensitive data and log appropriately"""
        sensitive_patterns = [
            "password",
            "email",
            "phone",
            "ssn",
            "credit_card",
            "api_key",
            "token",
            "secret",
        ]

        query_lower = query.lower()
        for pattern in sensitive_patterns:
            if pattern in query_lower:
                await self.audit_user_access(
                    user_id,
                    "SENSITIVE_DATA_ACCESS",
                    "multiple",
                    {"query_pattern": pattern, "query_snippet": query[:100]},
                )
                return True

        return False

    async def anonymize_sensitive_data(self, table: str, column: str) -> bool:
        """Anonymize sensitive data in specified table/column"""
        try:
            db_manager = await get_db_manager()

            # Generate anonymization query based on data type
            anonymize_query = f"""
                UPDATE {table} 
                SET {column} = 'ANONYMIZED_' || substr(md5(random()::text), 1, 8)
                WHERE {column} IS NOT NULL
            """

            async with db_manager.get_session() as session:
                result = await session.execute(text(anonymize_query))
                affected_rows = result.rowcount

                logger.info(f"Anonymized {affected_rows} rows in {table}.{column}")

                # Log the anonymization action
                await self.audit_user_access(
                    "SYSTEM",
                    "DATA_ANONYMIZATION",
                    table,
                    {"column": column, "affected_rows": affected_rows},
                )

                return True

        except Exception as e:
            logger.error(f"Data anonymization failed for {table}.{column}: {e}")
            return False

    async def get_audit_report(
        self, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Generate audit report for specified date range"""
        return [
            entry
            for entry in self.audit_log
            if start_date <= datetime.fromisoformat(entry["timestamp"]) <= end_date
        ]


# Global service instances
backup_service = DatabaseBackupService()
security_service = DatabaseSecurity()
