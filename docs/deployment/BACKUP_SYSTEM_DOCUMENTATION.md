# OBCMS Backup System Documentation

Complete automated backup solution for OBCMS staging and production environments.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Backup Scripts](#backup-scripts)
4. [Retention Policy](#retention-policy)
5. [Scheduling](#scheduling)
6. [Verification & Testing](#verification--testing)
7. [Restore Procedures](#restore-procedures)
8. [Monitoring](#monitoring)
9. [Docker Setup](#docker-setup)
10. [Offsite Backup (S3)](#offsite-backup-s3)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### Features

- **Automated Backups**: Database and media files
- **Tiered Retention**: 30/90/365 day rotation
- **Transaction-Safe**: Clean PostgreSQL dumps
- **Integrity Verification**: Automated checks
- **Restore Testing**: Non-destructive validation
- **Monitoring & Alerts**: Health checks and reports
- **Docker Support**: Volume-based backups
- **Offsite Storage**: Optional S3 integration

### Backup Schedule

| Type | Frequency | Retention | Time |
|------|-----------|-----------|------|
| **Daily** | Every day | 30 days | 2:00 AM |
| **Weekly** | Sunday | 90 days (3 months) | 3:00 AM |
| **Monthly** | 1st of month | 365 days (1 year) | 4:00 AM |

### Directory Structure

```
/path/to/obcms/
├── backups/
│   ├── daily/              # Daily backups (30 days)
│   ├── weekly/             # Weekly backups (90 days)
│   ├── monthly/            # Monthly backups (365 days)
│   ├── temp/               # Temporary files
│   └── pre-restore/        # Safety backups before restore
├── scripts/
│   ├── backup-database.sh         # Database backup
│   ├── backup-media.sh            # Media files backup
│   ├── backup-all.sh              # Complete backup
│   ├── cleanup-old-backups.sh     # Retention policy
│   ├── verify-backup.sh           # Verification
│   ├── restore-backup.sh          # Restore procedures
│   ├── backup-monitor.sh          # Monitoring & alerts
│   ├── backup-to-s3.sh            # S3 offsite (optional)
│   ├── backup-crontab.txt         # Cron configuration
│   └── docker-backup-setup.sh     # Docker setup
└── logs/
    ├── backup-YYYY-MM.log         # Backup logs
    ├── restore-YYYY-MM.log        # Restore logs
    ├── verify-YYYY-MM.log         # Verification logs
    └── monitor-YYYY-MM.log        # Monitor logs
```

---

## Installation

### Prerequisites

**Required:**
- PostgreSQL client tools (`pg_dump`, `psql`)
- `gzip`, `tar`, `bc` utilities
- Bash 4.0+

**Optional:**
- Docker (for containerized backups)
- AWS CLI (for S3 offsite backups)

### Installation Steps

1. **Verify Prerequisites:**

   ```bash
   # Check PostgreSQL client
   pg_dump --version
   psql --version
   
   # Check utilities
   which gzip tar bc
   ```

2. **Set Up Environment Variables:**

   Add to `.env` file:

   ```env
   # Database Configuration
   DB_NAME=obcms_db
   DB_USER=obcms_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Create Backup Directories:**

   ```bash
   cd /path/to/obcms
   mkdir -p backups/{daily,weekly,monthly,temp,pre-restore}
   mkdir -p logs
   ```

4. **Make Scripts Executable:**

   ```bash
   chmod +x scripts/backup-*.sh
   chmod +x scripts/cleanup-old-backups.sh
   chmod +x scripts/verify-backup.sh
   chmod +x scripts/restore-backup.sh
   ```

5. **Test Manual Backup:**

   ```bash
   # Test database backup
   ./scripts/backup-database.sh daily
   
   # Test media backup
   ./scripts/backup-media.sh daily
   
   # Test complete backup
   ./scripts/backup-all.sh daily
   ```

---

## Backup Scripts

### 1. Database Backup (`backup-database.sh`)

Creates transaction-safe PostgreSQL dumps with compression.

**Usage:**

```bash
./scripts/backup-database.sh [daily|weekly|monthly]
```

**Features:**
- Transaction-safe dump options (`--clean`, `--if-exists`)
- gzip compression
- Automatic verification
- Timestamped filenames

**Output:**
```
backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz
```

### 2. Media Backup (`backup-media.sh`)

Archives media files (uploads, documents, images).

**Usage:**

```bash
./scripts/backup-media.sh [daily|weekly|monthly]
```

**Features:**
- tar.gz compression
- Excludes cache files (`.pyc`, `__pycache__`)
- Preserves directory structure

**Output:**
```
backups/daily/obcms_media_daily_2025-10-20_02-00-00.tar.gz
```

### 3. Complete Backup (`backup-all.sh`)

Orchestrates full backup (database + media + cleanup).

**Usage:**

```bash
./scripts/backup-all.sh [daily|weekly|monthly]
```

**Workflow:**
1. Database backup
2. Media backup
3. Retention cleanup
4. Generate report

---

## Retention Policy

### Policy Rules

| Backup Type | Retention Period | Implementation |
|-------------|------------------|----------------|
| Daily | 30 days | Automated cleanup |
| Weekly | 90 days (3 months) | Automated cleanup |
| Monthly | 365 days (1 year) | Automated cleanup |

### Cleanup Script (`cleanup-old-backups.sh`)

**Usage:**

```bash
./scripts/cleanup-old-backups.sh
```

**Features:**
- Tiered retention enforcement
- Disk space monitoring
- Health checks
- Detailed logging

**Runs Automatically:**
- Daily at 5:00 AM (via cron)

---

## Scheduling

### Crontab Installation

1. **Edit Crontab Template:**

   ```bash
   nano scripts/backup-crontab.txt
   ```

   Replace `/path/to/obcms` with actual path.

2. **Install Crontab:**

   ```bash
   crontab -e
   ```

   Copy and paste the cron entries from `backup-crontab.txt`.

3. **Verify Installation:**

   ```bash
   crontab -l
   ```

### Cron Schedule Summary

```cron
# Daily backup (2:00 AM)
0 2 * * * cd /path/to/obcms && ./scripts/backup-all.sh daily

# Weekly backup (Sunday 3:00 AM)
0 3 * * 0 cd /path/to/obcms && ./scripts/backup-all.sh weekly

# Monthly backup (1st at 4:00 AM)
0 4 1 * * cd /path/to/obcms && ./scripts/backup-all.sh monthly

# Cleanup (5:00 AM)
0 5 * * * cd /path/to/obcms && ./scripts/cleanup-old-backups.sh

# Monitoring (every 6 hours)
0 */6 * * * cd /path/to/obcms && ./scripts/backup-monitor.sh --alert

# Weekly report (Monday 9:00 AM)
0 9 * * 1 cd /path/to/obcms && ./scripts/backup-monitor.sh --report
```

### Checking Cron Logs

```bash
# View cron execution logs
tail -f /tmp/backup-cron.log

# View backup logs
tail -f /path/to/obcms/logs/backup-$(date +%Y-%m).log
```

---

## Verification & Testing

### Verify Backup (`verify-backup.sh`)

**Usage:**

```bash
# Basic verification
./scripts/verify-backup.sh backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz

# With test restore
./scripts/verify-backup.sh backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz --test-restore
```

**Checks:**
- File exists
- File size validation (> 100KB)
- gzip integrity
- SQL structure validation
- Optional: Test restore to temporary database

### Automated Verification

Verification runs automatically after each backup. Check logs:

```bash
tail -f logs/verify-$(date +%Y-%m).log
```

---

## Restore Procedures

### Safety First

**WARNING:** Restore operations OVERWRITE existing data!

**Before Restoring:**
1. Stop application server
2. Create pre-restore backup
3. Verify backup integrity
4. Test in staging first

### Restore Database

```bash
./scripts/restore-backup.sh backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz
```

**Interactive Mode:**
- Prompts for confirmation
- Creates pre-restore backup
- Drops and recreates database
- Restores from backup
- Verifies restoration

**Force Mode (skip confirmation):**

```bash
./scripts/restore-backup.sh backup.sql.gz --force
```

### Restore Media Files

```bash
./scripts/restore-backup.sh backups/daily/obcms_media_daily_2025-10-20_02-00-00.tar.gz
```

**Process:**
- Backs up existing media
- Extracts new media files
- Verifies file count

### Post-Restore Steps

```bash
cd src

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser (if needed)
python manage.py createsuperuser

# Test application
python manage.py check
```

---

## Monitoring

### Backup Monitor (`backup-monitor.sh`)

**Usage:**

```bash
# Status report
./scripts/backup-monitor.sh --status

# Detailed report
./scripts/backup-monitor.sh --report

# Check alerts
./scripts/backup-monitor.sh --alert
```

### Health Metrics

- **Backup Age**: Alerts if backup > 48 hours old
- **Backup Size**: Warns if backup < 100KB
- **Disk Space**: Alerts if < 5GB free
- **Backup Counts**: Tracks retention compliance

### Status Report Example

```
╔══════════════════════════════════════════════════════════════╗
║           OBCMS Backup Monitoring Report                     ║
╚══════════════════════════════════════════════════════════════╝

Generated: 2025-10-20 10:00:00
Health Status: HEALTHY

Backup Age (hours since last backup):
  Daily:    12
  Weekly:   168
  Monthly:  720

Backup Counts:
  Daily:    30 backups
  Weekly:   12 backups
  Monthly:  12 backups

Storage:
  Total Used:     5.2 GB
  Free Space:     45.8 GB
```

### Email Notifications (Optional)

Add to crontab:

```cron
MAILTO=admin@example.com

0 */6 * * * cd /path/to/obcms && ./scripts/backup-monitor.sh --alert
```

---

## Docker Setup

### Prerequisites

- Docker and Docker Compose installed
- OBCMS running in Docker

### Setup Docker Backups

1. **Run Setup Script:**

   ```bash
   ./scripts/docker-backup-setup.sh
   ```

2. **Generated Files:**
   - `docker-compose.backup.yml`
   - `docker-backup-entrypoint.sh`
   - `docker-backup.sh`

3. **Test Docker Backup:**

   ```bash
   ./docker-backup.sh daily
   ```

### Docker Backup Volume

**Volume Name:** `obcms_backups`

**View Backups:**

```bash
docker run --rm -v obcms_backups:/backups alpine ls -lh /backups/daily
```

**Copy Backup to Host:**

```bash
docker run --rm \
  -v obcms_backups:/backups \
  -v $(pwd):/host \
  alpine \
  cp /backups/daily/backup-file.sql.gz /host/
```

**Schedule Docker Backups:**

Add to crontab:

```cron
0 2 * * * cd /path/to/obcms && ./docker-backup.sh daily
```

---

## Offsite Backup (S3)

### Prerequisites

1. **Install AWS CLI:**

   ```bash
   pip install awscli
   ```

2. **Configure AWS:**

   ```bash
   aws configure
   ```

3. **Create S3 Bucket:**

   ```bash
   aws s3 mb s3://obcms-backups --region us-west-2
   ```

4. **Set Environment Variables:**

   Add to `.env`:

   ```env
   AWS_S3_BACKUP_BUCKET=obcms-backups
   AWS_REGION=us-west-2
   ```

### Upload Backups to S3

```bash
./scripts/backup-to-s3.sh daily
```

**Features:**
- Server-side encryption (AES256)
- STANDARD_IA storage class (cost-effective)
- Automatic upload of all backups

### S3 Storage Structure

```
s3://obcms-backups/
├── daily/
│   ├── obcms_backup_daily_2025-10-20_02-00-00.sql.gz
│   └── obcms_media_daily_2025-10-20_02-00-00.tar.gz
├── weekly/
└── monthly/
```

### S3 Lifecycle Policy (Cost Optimization)

Create lifecycle rule to move old backups to Glacier:

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket obcms-backups \
  --lifecycle-configuration file://s3-lifecycle.json
```

**s3-lifecycle.json:**

```json
{
  "Rules": [
    {
      "Id": "MoveOldBackupsToGlacier",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
```

### Schedule S3 Upload

Add to crontab (after local backup):

```cron
# Upload monthly backups to S3
30 4 1 * * cd /path/to/obcms && ./scripts/backup-to-s3.sh monthly
```

---

## Troubleshooting

### Common Issues

#### 1. Permission Denied

**Problem:**
```
-bash: ./scripts/backup-database.sh: Permission denied
```

**Solution:**
```bash
chmod +x scripts/*.sh
```

#### 2. Database Connection Failed

**Problem:**
```
[ERROR] Database credentials not found in .env file
```

**Solution:**
- Verify `.env` file exists
- Check DB_NAME, DB_USER, DB_PASSWORD variables
- Test connection: `psql -h $DB_HOST -U $DB_USER -d $DB_NAME`

#### 3. Backup File Too Small

**Problem:**
```
[ERROR] Backup file is too small (50 KB). Possible corruption.
```

**Solution:**
- Check database has data: `psql -U $DB_USER -d $DB_NAME -c "\dt"`
- Review backup logs: `tail -f logs/backup-*.log`
- Test manual pg_dump

#### 4. Disk Space Full

**Problem:**
```
[WARNING] Low disk space: 2.5 GB available
```

**Solution:**
- Check disk usage: `df -h`
- Clean old backups: `./scripts/cleanup-old-backups.sh`
- Adjust retention policy
- Move old backups to S3

#### 5. Cron Job Not Running

**Problem:**
- Backups not running automatically

**Solution:**
```bash
# Check crontab is installed
crontab -l

# Check cron service is running
sudo systemctl status cron    # Ubuntu/Debian
sudo systemctl status crond   # CentOS/RHEL

# Check cron logs
tail -f /var/log/syslog | grep CRON
```

#### 6. Restore Failed

**Problem:**
```
[ERROR] Failed to restore database
```

**Solution:**
- Verify backup integrity: `./scripts/verify-backup.sh backup.sql.gz`
- Check PostgreSQL is running: `systemctl status postgresql`
- Review restore logs: `tail -f logs/restore-*.log`
- Try manual restore: `gunzip -c backup.sql.gz | psql -U $DB_USER -d $DB_NAME`

### Debug Mode

Enable debug mode for detailed output:

```bash
set -x  # Enable debug mode
./scripts/backup-database.sh daily
set +x  # Disable debug mode
```

### Log Files

All operations are logged:

```bash
# View all backup logs
tail -f logs/backup-*.log

# View restore logs
tail -f logs/restore-*.log

# View verification logs
tail -f logs/verify-*.log

# View monitoring logs
tail -f logs/monitor-*.log
```

---

## Best Practices

### 1. Test Regularly

- **Monthly**: Test restore procedure in staging
- **Quarterly**: Full disaster recovery drill
- **After Changes**: Test backups after major system updates

### 2. Monitor Proactively

- Check backup logs daily
- Review monitoring reports weekly
- Set up email alerts for failures

### 3. Secure Backups

- Encrypt backup files (already done via S3)
- Restrict access to backup directories
- Use secure credentials in `.env`

### 4. Document Changes

- Document custom retention policies
- Record restore procedures
- Maintain runbook for emergencies

### 5. Offsite Storage

- Always maintain offsite backups (S3)
- Test S3 restore procedures
- Monitor S3 costs

---

## Quick Reference

### Daily Operations

```bash
# Manual backup
./scripts/backup-all.sh daily

# Check backup status
./scripts/backup-monitor.sh --status

# Verify latest backup
./scripts/verify-backup.sh backups/daily/latest-backup.sql.gz

# View logs
tail -f logs/backup-$(date +%Y-%m).log
```

### Emergency Restore

```bash
# 1. Stop application
sudo systemctl stop obcms

# 2. Restore database
./scripts/restore-backup.sh backups/daily/backup.sql.gz

# 3. Restore media
./scripts/restore-backup.sh backups/daily/media.tar.gz

# 4. Run migrations
cd src && python manage.py migrate

# 5. Start application
sudo systemctl start obcms
```

### Maintenance

```bash
# Weekly cleanup
./scripts/cleanup-old-backups.sh

# Generate health report
./scripts/backup-monitor.sh --report

# Upload to S3
./scripts/backup-to-s3.sh monthly
```

---

## Support

For issues or questions:

1. Check logs in `/path/to/obcms/logs/`
2. Review this documentation
3. Test in staging environment first
4. Contact system administrator

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-20  
**Maintained By:** OBCMS DevOps Team
