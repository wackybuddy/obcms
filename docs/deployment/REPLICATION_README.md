# Database Replication & PgBouncer Setup - README

Quick start guide for setting up PostgreSQL replication and PgBouncer connection pooling for OBCMS.

---

## 📁 Files Overview

### Configuration Files

- **`config/pgbouncer/pgbouncer.ini`** - PgBouncer main configuration (pool size, connections, timeouts)
- **`config/pgbouncer/userlist.txt`** - PgBouncer user authentication (MD5 hashes)

### Scripts

- **`scripts/generate-pgbouncer-hashes.sh`** - Generate MD5 password hashes for PgBouncer
- **`scripts/init-database.sh`** - Initialize PostgreSQL database with users and extensions
- **`scripts/setup-postgres-replication.sh`** - Configure primary server for replication
- **`scripts/setup-replica.sh`** - Set up read replica server

### Documentation

- **`DATABASE_REPLICATION_SETUP.md`** - Complete setup guide (16KB, comprehensive)
- **`PGBOUNCER_REPLICATION_QUICK_REFERENCE.md`** - Quick reference card (8KB, common commands)
- **`REPLICATION_README.md`** - This file (overview)

---

## 🚀 Quick Start

### 1. Generate PgBouncer Password Hashes

```bash
cd /Users/saidamenmambayao/apps/obcms
./scripts/generate-pgbouncer-hashes.sh -i
```

This will prompt for passwords for:
- postgres (superuser)
- obcms_app (Django application)
- replicator (replication user)
- monitoring (metrics user)
- pgbouncer (admin user)

Copy the generated hashes to `config/pgbouncer/userlist.txt`.

### 2. Initialize Database

```bash
export DB_PASSWORD='your_secure_password'
export MONITORING_PASSWORD='monitoring_password'
export REPLICATION_PASSWORD='replication_password'

sudo ./scripts/init-database.sh staging
```

### 3. Setup Primary for Replication

```bash
export REPLICATION_PASSWORD='replication_password'
sudo ./scripts/setup-postgres-replication.sh staging
```

### 4. Setup Replica (if using read replicas)

```bash
# On replica server
export REPLICATION_PASSWORD='replication_password'
sudo ./scripts/setup-replica.sh 1 PRIMARY_HOST_IP
```

---

## 📊 Verification

### Test PgBouncer

```bash
# Connect via PgBouncer
psql -h localhost -p 6432 -U obcms_app -d obcms

# Check pool status
psql -h localhost -p 6432 -U pgbouncer pgbouncer -c "SHOW POOLS;"
```

### Test Replication

**On Primary:**
```sql
SELECT * FROM pg_stat_replication;
```

**On Replica:**
```sql
SELECT pg_is_in_recovery();  -- Should return 't'
```

---

## 📚 Documentation

### For Complete Setup Instructions
→ **[DATABASE_REPLICATION_SETUP.md](DATABASE_REPLICATION_SETUP.md)**

Contains:
- Detailed architecture overview
- Step-by-step setup instructions
- Troubleshooting guide
- Security checklist
- Monitoring & maintenance procedures

### For Quick Commands
→ **[PGBOUNCER_REPLICATION_QUICK_REFERENCE.md](PGBOUNCER_REPLICATION_QUICK_REFERENCE.md)**

Contains:
- Common commands reference
- Monitoring queries
- Troubleshooting quick fixes
- MD5 hash generation examples
- Emergency procedures

---

## 🔧 Architecture

```
Django App (OBCMS)
       ↓
   PgBouncer (Port 6432)
   Pool: 1000 clients → 25 connections
       ↓
   ┌────────────────────────┐
   ↓                        ↓
Primary DB           Read Replica(s)
(Read/Write)         (Read Only)
   ↓ ← ← ← ← ← ← ← ← ← ← ← ┘
   Streaming Replication
```

### Staging Environment
- **PgBouncer Pool:** 25 connections
- **Max Clients:** 1,000
- **Replicas:** 1 read replica
- **Expected Users:** 50-100 concurrent

### Production Environment
- **PgBouncer Pool:** 50 connections
- **Max Clients:** 2,000
- **Replicas:** 3 read replicas
- **Expected Users:** 700-1,100 concurrent (44 MOAs)

---

## 🔒 Security Notes

1. **NEVER commit credentials to git**
   - Use environment variables
   - Store in `.env` file (gitignored)

2. **Use strong passwords**
   - Minimum 16 characters
   - Include uppercase, lowercase, numbers, symbols

3. **Restrict network access**
   - Configure `pg_hba.conf` to allow only specific IPs
   - Use firewall rules

4. **Enable SSL/TLS in production**
   - Uncomment SSL settings in `pgbouncer.ini`
   - Generate SSL certificates

5. **Set correct file permissions**
   ```bash
   chmod 600 config/pgbouncer/userlist.txt
   chmod 640 config/pgbouncer/pgbouncer.ini
   ```

---

## 🛠️ Maintenance Scripts

### Daily Checks

```bash
# Check replication status
psql -U postgres -c "SELECT * FROM pg_stat_replication;"

# Check PgBouncer pools
psql -h localhost -p 6432 -U pgbouncer pgbouncer -c "SHOW POOLS;"
```

### Weekly Tasks

```bash
# Vacuum analyze database
vacuumdb -U obcms_app -d obcms --analyze --verbose

# Backup database
pg_dump -U obcms_app obcms | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Monthly Tasks

```bash
# Review slow queries
psql -U obcms_app -d obcms -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Test failover procedures (staging only)
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/14/main
```

---

## 📞 Support

### Common Issues

| Issue | Quick Fix | Full Documentation |
|-------|-----------|-------------------|
| Cannot connect to PgBouncer | Check userlist.txt hashes | [Setup Guide](DATABASE_REPLICATION_SETUP.md#pgbouncer-issues) |
| Replica not connecting | Verify pg_hba.conf on primary | [Setup Guide](DATABASE_REPLICATION_SETUP.md#replication-issues) |
| High replication lag | Increase wal_keep_size | [Quick Reference](PGBOUNCER_REPLICATION_QUICK_REFERENCE.md#troubleshooting) |
| Pool exhausted | Increase default_pool_size | [Quick Reference](PGBOUNCER_REPLICATION_QUICK_REFERENCE.md#common-operations) |

### Logs

```bash
# PostgreSQL logs
journalctl -u postgresql -n 100

# PgBouncer logs (Docker)
docker logs obcms_pgbouncer

# Django logs
tail -f src/logs/django.log
```

---

## 📋 Checklist

### Initial Setup

- [ ] Generate PgBouncer password hashes
- [ ] Update userlist.txt with hashes
- [ ] Run init-database.sh
- [ ] Run setup-postgres-replication.sh
- [ ] Setup read replica(s) with setup-replica.sh
- [ ] Update Django DATABASE_URL to use PgBouncer
- [ ] Test connections through PgBouncer
- [ ] Verify replication status
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Document credentials securely

### Production Deployment

- [ ] Use strong passwords (16+ characters)
- [ ] Enable SSL/TLS for PgBouncer
- [ ] Configure firewall rules
- [ ] Set correct file permissions
- [ ] Test failover procedures
- [ ] Set up automated backups
- [ ] Configure monitoring alerts
- [ ] Document runbooks
- [ ] Train operations team
- [ ] Perform load testing

---

## 🔗 Related Documentation

- [PostgreSQL Migration Summary](POSTGRESQL_MIGRATION_SUMMARY.md)
- [Staging Environment Guide](../env/staging-complete.md)
- [Coolify Deployment Guide](deployment-coolify.md)

---

**Last Updated:** 2025-10-20
**Version:** 1.0
**Status:** Production Ready
