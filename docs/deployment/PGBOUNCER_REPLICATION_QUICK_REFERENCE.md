# PgBouncer & Replication Quick Reference Card

Quick reference for common PgBouncer and PostgreSQL replication operations.

---

## 🚀 Initial Setup

### 1. Generate PgBouncer Hashes

```bash
cd /Users/saidamenmambayao/apps/obcms
./scripts/generate-pgbouncer-hashes.sh -i
```

### 2. Initialize Database

```bash
export DB_PASSWORD='your_password'
export MONITORING_PASSWORD='monitoring_password'
export REPLICATION_PASSWORD='replication_password'

sudo ./scripts/init-database.sh staging
```

### 3. Setup Replication on Primary

```bash
export REPLICATION_PASSWORD='replication_password'
sudo ./scripts/setup-postgres-replication.sh staging
```

### 4. Setup Replica Server

```bash
export REPLICATION_PASSWORD='replication_password'
sudo ./scripts/setup-replica.sh 1 PRIMARY_IP
```

---

## 📊 Monitoring Commands

### PgBouncer Status

```bash
# Connect to PgBouncer admin console
psql -h localhost -p 6432 -U pgbouncer pgbouncer

# Show pool status
SHOW POOLS;

# Show client connections
SHOW CLIENTS;

# Show server connections
SHOW SERVERS;

# Show statistics
SHOW STATS;
```

### Replication Status

**On Primary:**

```sql
-- View all replicas
SELECT
    client_addr,
    state,
    sync_state,
    replay_lag
FROM pg_stat_replication;

-- Check replication slots
SELECT slot_name, active, restart_lsn
FROM pg_replication_slots;
```

**On Replica:**

```sql
-- Confirm in recovery mode
SELECT pg_is_in_recovery();  -- Should return 't'

-- Check replication lag (seconds)
SELECT EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp()) AS lag_seconds;

-- Replication receiver status
SELECT * FROM pg_stat_wal_receiver;
```

---

## 🔧 Common Operations

### PgBouncer Control

```sql
-- Reload configuration (no downtime)
RELOAD;

-- Pause all queries
PAUSE;

-- Resume queries
RESUME;

-- Kill specific client
KILL <client_id>;

-- Disconnect all clients
SHUTDOWN;
```

### Connection Testing

```bash
# Test via PgBouncer (port 6432)
psql -h localhost -p 6432 -U obcms_app -d obcms

# Test direct PostgreSQL (port 5432)
psql -h localhost -p 5432 -U obcms_app -d obcms

# Test from Django
python src/manage.py dbshell
```

### Performance Monitoring

```sql
-- Active queries
SELECT pid, usename, state, query, query_start
FROM pg_stat_activity
WHERE state != 'idle';

-- Slow queries (pg_stat_statements)
SELECT
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Connection count by database
SELECT datname, count(*) AS connections
FROM pg_stat_activity
GROUP BY datname
ORDER BY connections DESC;
```

---

## 🛠️ Troubleshooting

### PgBouncer Issues

**"no more connections allowed"**

```sql
-- Check pool usage
SHOW POOLS;

-- Increase pool size in pgbouncer.ini
default_pool_size = 50
```

**"md5 auth failed"**

```bash
# Regenerate hash
./scripts/generate-pgbouncer-hashes.sh -e

# Update userlist.txt with correct hash
nano config/pgbouncer/userlist.txt
```

### Replication Issues

**High replication lag**

```sql
-- On primary: Check WAL sender
SELECT * FROM pg_stat_replication;

-- Check wal_keep_size
SHOW wal_keep_size;

-- Increase if needed
ALTER SYSTEM SET wal_keep_size = '2GB';
SELECT pg_reload_conf();
```

**Replica not connecting**

```bash
# On replica: Check logs
journalctl -u postgresql -n 50

# Test connection from replica to primary
PGPASSWORD='replication_password' psql -h PRIMARY_IP -U replicator -d postgres -c "SELECT 1;"

# Verify pg_hba.conf on primary
grep replication /var/lib/postgresql/14/main/pg_hba.conf
```

---

## 📋 MD5 Hash Generation

### Format

```
MD5 Hash = md5(password + username)
```

### Examples

```bash
# obcms_app user with password "MyPass123"
echo -n "MyPass123obcms_app" | md5sum | awk '{print "md5"$1}'

# monitoring user with password "MonitorPass"
echo -n "MonitorPassmonitoring" | md5sum | awk '{print "md5"$1}'

# On macOS (use md5 instead of md5sum)
echo -n "MyPass123obcms_app" | md5 -r | awk '{print "md5"$1}'
```

### Batch Generation

```bash
# Create passwords file
cat > /tmp/passwords.txt << EOF
postgres:SuperSecurePass123
obcms_app:AppUserPass456
replicator:ReplPass789
monitoring:MonitorPass012
pgbouncer:PgBPass345
EOF

# Generate hashes
./scripts/generate-pgbouncer-hashes.sh -f /tmp/passwords.txt

# Clean up
rm /tmp/passwords.txt
```

---

## 🔒 Security Checklist

```bash
# Check userlist.txt permissions
ls -la config/pgbouncer/userlist.txt  # Should be 600 or 640

# Verify pg_hba.conf restricts replication
sudo cat /var/lib/postgresql/14/main/pg_hba.conf | grep replication

# Test unauthorized access (should fail)
psql -h localhost -p 6432 -U unauthorized_user -d obcms

# Check SSL configuration (production)
psql "sslmode=require host=localhost port=6432 user=obcms_app dbname=obcms"
```

---

## 📦 Backup & Restore

### Backup

```bash
# Full backup
pg_dump -U obcms_app -h localhost -p 5432 obcms | gzip > backup_$(date +%Y%m%d).sql.gz

# Schema only
pg_dump -U obcms_app -h localhost -p 5432 --schema-only obcms > schema_$(date +%Y%m%d).sql

# Data only
pg_dump -U obcms_app -h localhost -p 5432 --data-only obcms > data_$(date +%Y%m%d).sql
```

### Restore

```bash
# Restore full backup
gunzip -c backup_20251020.sql.gz | psql -U obcms_app -h localhost -p 5432 obcms

# Restore to new database
createdb -U postgres obcms_restore
gunzip -c backup_20251020.sql.gz | psql -U obcms_app -h localhost -p 5432 obcms_restore
```

---

## 📈 Capacity Planning

### Current Limits

| Environment | Pool Size | Max Clients | Expected Users | Ratio |
|-------------|-----------|-------------|----------------|-------|
| Staging     | 25        | 1,000       | 50-100         | 40:1  |
| Production  | 50        | 2,000       | 700-1,100      | 40:1  |

### Monitoring Thresholds

```sql
-- Pool utilization (should be < 80%)
SELECT
    pool,
    cl_active,
    cl_waiting,
    sv_active,
    sv_idle,
    ROUND(100.0 * sv_active / (sv_active + sv_idle), 2) AS utilization_pct
FROM (
    -- Query from PgBouncer SHOW POOLS
) AS pools;
```

### Scale Up Decision

Scale up if:
- Pool utilization > 80% consistently
- Client wait time > 5 seconds
- Replication lag > 10 seconds
- Connection queue depth > 50

---

## 🔄 Failover Procedure

### Manual Failover (Primary Failed)

1. **Promote Replica to Primary**

```bash
# On replica server
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/14/main
```

2. **Verify Promotion**

```sql
-- Should return 'f' (no longer in recovery)
SELECT pg_is_in_recovery();
```

3. **Update PgBouncer Configuration**

```ini
# config/pgbouncer/pgbouncer.ini
[databases]
obcms = host=NEW_PRIMARY_IP port=5432 dbname=obcms user=obcms_app
```

4. **Reload PgBouncer**

```sql
RELOAD;
```

5. **Update Django Configuration**

```bash
# Update .env
DATABASE_HOST=NEW_PRIMARY_IP
```

6. **Restart Application**

```bash
docker-compose restart web
```

---

## 📞 Emergency Contacts

### Critical Issues

1. Check logs first: `journalctl -u postgresql -n 100`
2. Verify PgBouncer: `docker logs obcms_pgbouncer`
3. Check replication: `SELECT * FROM pg_stat_replication;`
4. Contact DBA if unresolved

### Common Error Codes

| Error | Meaning | Solution |
|-------|---------|----------|
| `FATAL: no more connections` | Pool exhausted | Increase `default_pool_size` |
| `FATAL: md5 auth failed` | Wrong password hash | Regenerate hash |
| `ERROR: cannot execute ... in read-only transaction` | Write to replica | Route writes to primary |
| `WARNING: replication lag > 60s` | Replica falling behind | Check network, increase `wal_keep_size` |

---

## 📚 File Locations

| File | Path |
|------|------|
| PgBouncer config | `config/pgbouncer/pgbouncer.ini` |
| PgBouncer userlist | `config/pgbouncer/userlist.txt` |
| PostgreSQL config | `/var/lib/postgresql/14/main/postgresql.conf` |
| pg_hba.conf | `/var/lib/postgresql/14/main/pg_hba.conf` |
| PostgreSQL logs | `/var/log/postgresql/postgresql-14-main.log` |
| Init script | `scripts/init-database.sh` |
| Replication script | `scripts/setup-postgres-replication.sh` |
| Replica setup | `scripts/setup-replica.sh` |
| Hash generator | `scripts/generate-pgbouncer-hashes.sh` |

---

## 🔗 Quick Links

- [Full Documentation](DATABASE_REPLICATION_SETUP.md)
- [PostgreSQL Docs](https://www.postgresql.org/docs/current/)
- [PgBouncer Docs](https://www.pgbouncer.org/usage.html)
- [Django Database Docs](https://docs.djangoproject.com/en/4.2/ref/databases/)

---

**Last Updated:** 2025-10-20
**Version:** 1.0
