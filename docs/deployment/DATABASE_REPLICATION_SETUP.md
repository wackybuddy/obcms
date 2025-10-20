# PostgreSQL Database Replication & PgBouncer Setup Guide

**Status:** Production Ready
**Last Updated:** 2025-10-20
**Environment:** Staging & Production

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [PgBouncer Setup](#pgbouncer-setup)
4. [Database Replication Setup](#database-replication-setup)
5. [Read Replica Configuration](#read-replica-configuration)
6. [Verification & Testing](#verification--testing)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the complete setup of:
- **PgBouncer** for connection pooling (1000 client connections → 25-50 database connections)
- **PostgreSQL Replication** for high availability and read scaling
- **Read Replicas** (1 for staging, 3 for production)

### Benefits

- **Connection Pooling**: Efficient connection management (10:1 ratio)
- **High Availability**: Automatic failover with streaming replication
- **Read Scaling**: Distribute SELECT queries across replicas
- **Performance**: Reduced connection overhead and latency

### Architecture Overview

```
┌─────────────────┐
│  Django App     │
│  (OBCMS)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PgBouncer     │  ← Connection Pool (Port 6432)
│   Pool Mode:    │
│   transaction   │
└────────┬────────┘
         │
    ┌────┴─────┬─────────────┬─────────────┐
    ▼          ▼             ▼             ▼
┌────────┐ ┌────────┐   ┌────────┐   ┌────────┐
│Primary │ │Replica1│   │Replica2│   │Replica3│
│ (RW)   │ │  (RO)  │   │  (RO)  │   │  (RO)  │
└────────┘ └────────┘   └────────┘   └────────┘
     │          ▲             ▲             ▲
     └──────────┴─────────────┴─────────────┘
           Streaming Replication
```

---

## PgBouncer Setup

### Step 1: Generate Password Hashes

PgBouncer uses MD5 hashes in the format: `md5(password + username)`

**Option A: Interactive Script (Recommended)**

```bash
cd /Users/saidamenmambayao/apps/obcms
./scripts/generate-pgbouncer-hashes.sh -i
```

This will prompt you to enter passwords for each user:
- `postgres` - PostgreSQL superuser
- `obcms_app` - Django application user
- `replicator` - Replication user
- `monitoring` - Monitoring/metrics user
- `pgbouncer` - PgBouncer admin user

**Option B: Manual Generation**

```bash
# Format: echo -n "passwordusername" | md5sum
# Example for obcms_app user with password "MySecurePass123"
echo -n "MySecurePass123obcms_app" | md5sum | awk '{print "md5"$1}'
# Output: md5a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Option C: Batch Mode**

Create a passwords file:

```bash
# passwords.txt
postgres:SuperSecurePostgresPass
obcms_app:AppUserSecurePass
replicator:ReplicationSecurePass
monitoring:MonitoringSecurePass
pgbouncer:PgBouncerAdminPass
```

Generate hashes:

```bash
./scripts/generate-pgbouncer-hashes.sh -f passwords.txt > /tmp/hashes.txt
```

**SECURITY WARNING:** Delete passwords.txt immediately after use!

### Step 2: Update PgBouncer Userlist

Edit `config/pgbouncer/userlist.txt`:

```bash
nano config/pgbouncer/userlist.txt
```

Replace the placeholder hashes with your generated hashes:

```
"postgres" "md5YOUR_POSTGRES_HASH"
"obcms_app" "md5YOUR_APP_HASH"
"replicator" "md5YOUR_REPLICATOR_HASH"
"monitoring" "md5YOUR_MONITORING_HASH"
"pgbouncer" "md5YOUR_PGBOUNCER_HASH"
```

### Step 3: Configure PgBouncer

The configuration file `config/pgbouncer/pgbouncer.ini` is pre-configured with optimal settings:

**Key Settings:**
- **Pool Mode:** `transaction` (recommended for Django)
- **Default Pool Size:** 25 (staging) / 50 (production)
- **Max Client Connections:** 1000 (staging) / 2000 (production)
- **Reserve Pool:** 5 connections for emergencies
- **Connection Timeout:** 120 seconds

**For Staging:**
```ini
default_pool_size = 25
max_client_conn = 1000
```

**For Production:**
```ini
default_pool_size = 50
max_client_conn = 2000
```

### Step 4: Deploy PgBouncer

**Using Docker Compose:**

```yaml
# docker-compose.yml
services:
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    container_name: obcms_pgbouncer
    ports:
      - "6432:6432"
    volumes:
      - ./config/pgbouncer/pgbouncer.ini:/etc/pgbouncer/pgbouncer.ini:ro
      - ./config/pgbouncer/userlist.txt:/etc/pgbouncer/userlist.txt:ro
    environment:
      - DATABASES_HOST=db
      - DATABASES_PORT=5432
      - DATABASES_DBNAME=obcms
    restart: unless-stopped
    networks:
      - obcms_network
```

**Start PgBouncer:**

```bash
docker-compose up -d pgbouncer
```

### Step 5: Test PgBouncer Connection

```bash
# Connect via PgBouncer (port 6432)
psql -h localhost -p 6432 -U obcms_app -d obcms

# Connect to PgBouncer admin console
psql -h localhost -p 6432 -U pgbouncer pgbouncer
```

**Admin Commands:**

```sql
-- Show connection pools
SHOW POOLS;

-- Show active clients
SHOW CLIENTS;

-- Show server connections
SHOW SERVERS;

-- Show statistics
SHOW STATS;

-- Show configuration
SHOW CONFIG;
```

---

## Database Replication Setup

### Prerequisites

- PostgreSQL 14+ installed
- Root or postgres user access
- Network connectivity between primary and replicas
- Firewall rules configured (port 5432)

### Step 1: Initialize Primary Database

```bash
# Set environment variables
export DB_PASSWORD='your_secure_app_password'
export REPLICATION_PASSWORD='your_secure_replication_password'
export MONITORING_PASSWORD='your_secure_monitoring_password'

# Run initialization script
sudo ./scripts/init-database.sh staging
```

This script will:
1. Create database users (obcms_app, monitoring, replicator)
2. Create obcms database
3. Configure timezone (Asia/Manila)
4. Install PostgreSQL extensions
5. Grant appropriate permissions
6. Run Django migrations
7. Create initial backup

**Verify initialization:**

```bash
# Test connection
psql -h localhost -p 5432 -U obcms_app -d obcms

# Check database size
psql -h localhost -p 5432 -U obcms_app -d obcms -c "SELECT pg_size_pretty(pg_database_size('obcms'));"
```

### Step 2: Configure Primary for Replication

```bash
# Set replication password
export REPLICATION_PASSWORD='your_secure_replication_password'

# Run replication setup
sudo ./scripts/setup-postgres-replication.sh staging
```

This script will:
1. Backup existing postgresql.conf and pg_hba.conf
2. Create replication user with proper privileges
3. Configure WAL settings (wal_level = replica)
4. Set max_wal_senders and wal_keep_size
5. Create replication slots (1 for staging, 3 for production)
6. Update pg_hba.conf for replication connections
7. Reload PostgreSQL configuration

**Verify replication setup:**

```bash
# Check replication settings
psql -U postgres -c "SHOW wal_level; SHOW max_wal_senders;"

# Check replication user
psql -U postgres -c "SELECT usename, userepl FROM pg_user WHERE usename = 'replicator';"

# Check replication slots
psql -U postgres -c "SELECT * FROM pg_replication_slots;"
```

---

## Read Replica Configuration

### Staging Environment (1 Replica)

**On Replica Server:**

```bash
# Set environment variables
export REPLICATION_PASSWORD='your_secure_replication_password'

# Run replica setup
sudo ./scripts/setup-replica.sh 1 PRIMARY_HOST_IP
```

Replace `PRIMARY_HOST_IP` with your primary server IP (e.g., 10.0.1.10).

### Production Environment (3 Replicas)

Repeat for each replica:

```bash
# Replica 1
sudo ./scripts/setup-replica.sh 1 PRIMARY_HOST_IP

# Replica 2
sudo ./scripts/setup-replica.sh 2 PRIMARY_HOST_IP

# Replica 3
sudo ./scripts/setup-replica.sh 3 PRIMARY_HOST_IP
```

### What the Setup Script Does

1. Stops PostgreSQL service
2. Backs up existing data directory
3. Tests connection to primary server
4. Creates base backup using pg_basebackup
5. Configures replica settings (hot_standby, etc.)
6. Creates standby.signal file
7. Sets correct file permissions
8. Starts PostgreSQL service
9. Verifies replication status

### Verify Replica Status

**On Replica Server:**

```bash
# Check if in recovery mode (should return 't')
psql -U postgres -c "SELECT pg_is_in_recovery();"

# Check replication status
psql -U postgres -x -c "SELECT * FROM pg_stat_wal_receiver;"

# Check replication lag
psql -U postgres -c "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();"
```

**On Primary Server:**

```bash
# View connected replicas
psql -U postgres -c "SELECT * FROM pg_stat_replication;"

# Check replication slots
psql -U postgres -c "SELECT * FROM pg_replication_slots;"

# Check replication lag
psql -U postgres -c "SELECT client_addr, state, sync_state, replay_lag FROM pg_stat_replication;"
```

---

## Verification & Testing

### Connection Pooling Test

```bash
# Test PgBouncer connection
psql -h localhost -p 6432 -U obcms_app -d obcms -c "SELECT 'PgBouncer working!' as status;"

# Check pool statistics
psql -h localhost -p 6432 -U pgbouncer pgbouncer -c "SHOW POOLS;"
```

### Replication Test

**On Primary:**

```sql
-- Create test table
CREATE TABLE replication_test (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert test data
INSERT INTO replication_test (message) VALUES ('Test from primary');
```

**On Replica (wait 1-2 seconds):**

```sql
-- Verify data replicated
SELECT * FROM replication_test;
```

**Expected Result:** You should see the test data on the replica.

### Load Testing

```bash
# Generate connection load
for i in {1..100}; do
    psql -h localhost -p 6432 -U obcms_app -d obcms -c "SELECT 1;" &
done

# Check pool status
psql -h localhost -p 6432 -U pgbouncer pgbouncer -c "SHOW POOLS;"
```

---

## Monitoring & Maintenance

### Key Metrics to Monitor

**PgBouncer Metrics:**

```sql
-- Connection pool status
SHOW POOLS;

-- Active clients
SHOW CLIENTS;

-- Server connections
SHOW SERVERS;

-- Statistics (queries per second, etc.)
SHOW STATS;
```

**Replication Metrics:**

```sql
-- On Primary: Replication lag
SELECT
    client_addr,
    state,
    sync_state,
    replay_lag,
    write_lag,
    flush_lag
FROM pg_stat_replication;

-- On Replica: Recovery status
SELECT pg_is_in_recovery();

-- On Replica: Replication lag
SELECT
    CASE
        WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() THEN 0
        ELSE EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp())
    END AS lag_seconds;
```

### Prometheus Metrics

Add to `config/prometheus/postgres_exporter.yml`:

```yaml
# PostgreSQL metrics
- job_name: 'postgres_primary'
  static_configs:
    - targets: ['db:5432']
      labels:
        role: 'primary'

- job_name: 'postgres_replica1'
  static_configs:
    - targets: ['db-replica1:5432']
      labels:
        role: 'replica'

# PgBouncer metrics
- job_name: 'pgbouncer'
  static_configs:
    - targets: ['pgbouncer:9127']
```

### Grafana Dashboards

Import dashboard ID: `9628` (PostgreSQL Database)
Import dashboard ID: `12320` (PgBouncer)

### Maintenance Tasks

**Weekly:**
- Check replication lag
- Review PgBouncer statistics
- Monitor connection pool utilization

**Monthly:**
- Vacuum analyze database
- Review and optimize slow queries
- Test failover procedures
- Backup verification

**Quarterly:**
- Review capacity planning
- Update PostgreSQL minor version
- Test disaster recovery

---

## Troubleshooting

### PgBouncer Issues

**Problem:** Cannot connect to PgBouncer

```bash
# Check if PgBouncer is running
docker ps | grep pgbouncer

# Check PgBouncer logs
docker logs obcms_pgbouncer

# Test direct PostgreSQL connection
psql -h localhost -p 5432 -U obcms_app -d obcms
```

**Problem:** "md5 auth failed"

- Verify userlist.txt has correct MD5 hashes
- Ensure format: `"username" "md5hash"`
- Regenerate hashes using generate-pgbouncer-hashes.sh

**Problem:** "no more connections allowed"

```sql
-- Check current pool usage
SHOW POOLS;

-- Increase pool size if needed (in pgbouncer.ini)
default_pool_size = 50  -- increase from 25
```

### Replication Issues

**Problem:** Replica not connecting to primary

```bash
# On replica: Check logs
journalctl -u postgresql -n 100

# Verify pg_hba.conf on primary allows replication
grep replication /var/lib/postgresql/14/main/pg_hba.conf

# Test replication connection from replica
psql "host=PRIMARY_IP port=5432 user=replicator password=PASSWORD replication=database"
```

**Problem:** High replication lag

```sql
-- Check WAL sender status on primary
SELECT * FROM pg_stat_replication;

-- Check if replica is keeping up
SELECT pg_is_wal_replay_paused();

-- Increase wal_keep_size if needed
ALTER SYSTEM SET wal_keep_size = '2GB';
SELECT pg_reload_conf();
```

**Problem:** Replication slot inactive

```sql
-- On primary: Check slot status
SELECT * FROM pg_replication_slots;

-- If slot is inactive and replica is down, may need to drop and recreate
-- WARNING: Only do this if you're sure replica is being rebuilt
SELECT pg_drop_replication_slot('replica_1_slot');
SELECT pg_create_physical_replication_slot('replica_1_slot');
```

### Connection Issues

**Problem:** "FATAL: too many connections"

This should be prevented by PgBouncer, but if it occurs:

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Find and kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '10 minutes';
```

**Problem:** Slow queries

```sql
-- Enable pg_stat_statements (already done in init script)
-- View slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

## Quick Reference Commands

### PgBouncer

```bash
# Connect to admin console
psql -h localhost -p 6432 -U pgbouncer pgbouncer

# Reload configuration
RELOAD;

# Pause all queries
PAUSE;

# Resume queries
RESUME;

# Show pools
SHOW POOLS;

# Show stats
SHOW STATS;
```

### Replication

```bash
# On Primary: View replication status
psql -U postgres -c "SELECT * FROM pg_stat_replication;"

# On Replica: Check recovery status
psql -U postgres -c "SELECT pg_is_in_recovery();"

# Check replication lag (seconds)
psql -U postgres -c "SELECT EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp()) AS lag_seconds;"
```

### Maintenance

```bash
# Vacuum analyze
vacuumdb -U obcms_app -d obcms --analyze --verbose

# Backup database
pg_dump -U obcms_app obcms | gzip > obcms_backup_$(date +%Y%m%d).sql.gz

# Restore database
gunzip -c obcms_backup_20251020.sql.gz | psql -U obcms_app obcms
```

---

## Security Checklist

- [ ] Strong passwords for all database users (minimum 16 characters)
- [ ] PgBouncer userlist.txt has correct permissions (600)
- [ ] pg_hba.conf restricts replication to specific IPs
- [ ] SSL/TLS enabled for production (client_tls_sslmode = require)
- [ ] Monitoring user has read-only privileges
- [ ] Credentials stored in .env file (not in git)
- [ ] Regular security updates applied
- [ ] Backup encryption enabled
- [ ] Audit logging configured
- [ ] Firewall rules restrict database access

---

## Next Steps

After completing this setup:

1. **Update Django Settings:**
   - Configure DATABASE_URL to use PgBouncer (port 6432)
   - Implement database routing for read replicas
   - Test connection pooling

2. **Configure Monitoring:**
   - Set up Prometheus exporters
   - Import Grafana dashboards
   - Configure alerts for replication lag

3. **Test Failover:**
   - Document failover procedures
   - Practice failover in staging
   - Set up automated health checks

4. **Optimize Performance:**
   - Review slow query log
   - Add indexes as needed
   - Configure connection pooling per application

5. **Documentation:**
   - Document custom configurations
   - Create runbooks for common issues
   - Train team on operational procedures

---

## Resources

- [PostgreSQL Replication Documentation](https://www.postgresql.org/docs/current/high-availability.html)
- [PgBouncer Documentation](https://www.pgbouncer.org/usage.html)
- [Django Database Optimization](https://docs.djangoproject.com/en/4.2/topics/db/optimization/)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-20
**Maintained By:** OBCMS Infrastructure Team
