# OBCMS Backup Scripts

Automated backup system for OBCMS staging and production environments.

## Quick Start

### 1. Initial Setup

```bash
# Make scripts executable
chmod +x backup-*.sh cleanup-old-backups.sh verify-backup.sh restore-backup.sh

# Test database backup
./backup-database.sh daily

# Test media backup
./backup-media.sh daily

# Test complete backup
./backup-all.sh daily
```

### 2. Install Cron Schedule

```bash
# Edit crontab template with actual paths
nano backup-crontab.txt

# Install to crontab
crontab -e
# (paste contents from backup-crontab.txt)

# Verify
crontab -l
```

### 3. Monitor Backups

```bash
# Check backup status
./backup-monitor.sh --status

# View detailed report
./backup-monitor.sh --report

# Check for alerts
./backup-monitor.sh --alert
```

## Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `backup-database.sh` | Database backup | `./backup-database.sh [daily\|weekly\|monthly]` |
| `backup-media.sh` | Media files backup | `./backup-media.sh [daily\|weekly\|monthly]` |
| `backup-all.sh` | Complete backup | `./backup-all.sh [daily\|weekly\|monthly]` |
| `cleanup-old-backups.sh` | Retention policy | `./cleanup-old-backups.sh` |
| `verify-backup.sh` | Verify integrity | `./verify-backup.sh <backup-file>` |
| `restore-backup.sh` | Restore backup | `./restore-backup.sh <backup-file>` |
| `backup-monitor.sh` | Monitoring & alerts | `./backup-monitor.sh [--status\|--report\|--alert]` |
| `backup-to-s3.sh` | S3 offsite (optional) | `./backup-to-s3.sh [daily\|weekly\|monthly]` |
| `docker-backup-setup.sh` | Docker setup | `./docker-backup-setup.sh` |

## Retention Policy

- **Daily**: 30 days
- **Weekly**: 90 days (3 months)
- **Monthly**: 365 days (1 year)

## Directory Structure

```
backups/
├── daily/       # Daily backups (30 days)
├── weekly/      # Weekly backups (90 days)
├── monthly/     # Monthly backups (365 days)
└── temp/        # Temporary files
```

## Documentation

See [BACKUP_SYSTEM_DOCUMENTATION.md](../docs/deployment/BACKUP_SYSTEM_DOCUMENTATION.md) for complete documentation.

## Common Tasks

### Manual Backup

```bash
# Full backup (database + media)
./backup-all.sh daily

# Database only
./backup-database.sh daily

# Media only
./backup-media.sh daily
```

### Verify Backup

```bash
# Basic verification
./verify-backup.sh backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz

# With test restore
./verify-backup.sh backups/daily/backup.sql.gz --test-restore
```

### Restore Backup

```bash
# Restore database
./restore-backup.sh backups/daily/obcms_backup_daily_2025-10-20_02-00-00.sql.gz

# Restore media
./restore-backup.sh backups/daily/obcms_media_daily_2025-10-20_02-00-00.tar.gz
```

### Monitoring

```bash
# Quick status check
./backup-monitor.sh --status

# Detailed report
./backup-monitor.sh --report

# Check for alerts
./backup-monitor.sh --alert
```

## Docker Support

```bash
# Setup Docker backups
./docker-backup-setup.sh

# Run Docker backup
./docker-backup.sh daily
```

## S3 Offsite Backup (Optional)

```bash
# Setup AWS CLI
pip install awscli
aws configure

# Upload to S3
./backup-to-s3.sh monthly
```

## Troubleshooting

### Check Logs

```bash
# View backup logs
tail -f ../logs/backup-$(date +%Y-%m).log

# View all logs
ls -lh ../logs/
```

### Common Issues

1. **Permission Denied**: `chmod +x *.sh`
2. **Database Connection**: Check `.env` file
3. **Disk Space**: Run `./cleanup-old-backups.sh`
4. **Cron Not Running**: Check `crontab -l`

## Support

- Full Documentation: [BACKUP_SYSTEM_DOCUMENTATION.md](../docs/deployment/BACKUP_SYSTEM_DOCUMENTATION.md)
- Check logs: `../logs/`
- Test in staging first

---

**Version:** 1.0  
**Last Updated:** 2025-10-20
