#!/bin/bash
# Test PostgreSQL Backup Restore

BACKUP_FILE="/backups/banking_backup_20251102_153342.backup"
TEST_DB="banking_test"

echo "=== Creating test database ==="
docker exec banking_db psql -U brandonlau -d postgres -c "DROP DATABASE IF EXISTS ${TEST_DB};"
docker exec banking_db psql -U brandonlau -d postgres -c "CREATE DATABASE ${TEST_DB};"

echo ""
echo "=== Restoring backup to test database ==="
docker exec banking_db pg_restore -U brandonlau -d ${TEST_DB} --clean --if-exists ${BACKUP_FILE}

echo ""
echo "=== Verifying tables exist ==="
docker exec banking_db psql -U brandonlau -d ${TEST_DB} -c "\dt"

echo ""
echo "=== Comparing row counts ==="
echo "Production database:"
docker exec banking_db psql -U brandonlau -d banking_db -t -c "SELECT COUNT(*) FROM transactions;"
echo "Test database (from backup):"
docker exec banking_db psql -U brandonlau -d ${TEST_DB} -t -c "SELECT COUNT(*) FROM transactions;"

echo ""
echo "=== Cleanup ==="
docker exec banking_db psql -U brandonlau -d postgres -c "DROP DATABASE ${TEST_DB};"

echo ""
echo "✅ Backup test complete! If row counts match, your backup is good."
