# Virus Scanning Implementation Guide
**Date:** October 1, 2025
**Status:** Recommended for Production
**Priority:** Medium

---

## Overview

While OBCMS currently implements file extension and MIME type validation for uploaded files, adding virus scanning provides an additional security layer against malware, especially for archive files (ZIP, RAR, 7z) which can contain malicious content.

---

## Current File Upload Security

### Implemented Protections ✅

1. **File Extension Whitelist**
   - Only allows specific file types (PDF, DOCX, images, etc.)
   - Blocks executable files (.exe, .sh, .bat, etc.)

2. **MIME Type Validation**
   - Validates actual file content (not just extension)
   - Detects executables disguised as documents
   - Uses `python-magic` library

3. **File Size Limit**
   - Maximum 50MB per upload
   - Prevents resource exhaustion attacks

### Remaining Risk ⚠️

**Archive Files (ZIP, RAR, 7z):**
- Can contain malware inside
- MIME validation only checks archive format, not contents
- Malicious scripts could be extracted and executed

---

## Recommended Solution: ClamAV Integration

### Why ClamAV?

- ✅ Open-source and free
- ✅ Actively maintained virus database
- ✅ Lightweight and fast
- ✅ Docker-friendly
- ✅ Python integration available
- ✅ Widely used in production systems

---

## Implementation Options

### Option 1: Docker Sidecar Container (Recommended)

**Architecture:**
```
┌─────────────────┐      ┌──────────────────┐
│  OBCMS (Django) │─────▶│  ClamAV Daemon   │
│   Container     │      │   Container      │
└─────────────────┘      └──────────────────┘
         │                        │
         └────────────────────────┘
              Docker Network
```

**Benefits:**
- ✅ Isolated service
- ✅ Easy to scale
- ✅ No impact on Django container
- ✅ Automatic virus database updates

**Docker Compose Configuration:**

```yaml
# Add to docker-compose.prod.yml
services:
  web:
    # ... existing Django service ...
    depends_on:
      - db
      - redis
      - clamav
    environment:
      - CLAMAV_HOST=clamav
      - CLAMAV_PORT=3310

  clamav:
    image: clamav/clamav:latest
    container_name: obcms_clamav
    restart: unless-stopped
    volumes:
      - clamav_data:/var/lib/clamav
    ports:
      - "3310:3310"
    healthcheck:
      test: ["CMD", "/usr/local/bin/clamdcheck.sh"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 120s  # ClamAV needs time to download virus definitions

volumes:
  clamav_data:
```

---

### Option 2: In-Process Scanning

**For:** Small deployments, single-server setups
**Against:** Increases memory usage, slower startup

```dockerfile
# Add to Dockerfile
RUN apt-get update && apt-get install -y \
    clamav \
    clamav-daemon \
    && rm -rf /var/lib/apt/lists/*

# Update virus definitions
RUN freshclam
```

---

## Django Implementation

### 1. Install Python ClamAV Client

```bash
# Add to requirements/base.txt
clamd>=1.0.2
```

### 2. Create Virus Scanner Service

```python
# src/common/services/virus_scanner.py
"""
Virus scanning service using ClamAV.
"""
import logging
from django.conf import settings
import clamd

logger = logging.getLogger(__name__)


class VirusScanner:
    """Interface to ClamAV virus scanning daemon."""

    def __init__(self):
        """Initialize connection to ClamAV daemon."""
        self.enabled = getattr(settings, 'VIRUS_SCANNING_ENABLED', False)

        if not self.enabled:
            logger.info("Virus scanning is disabled")
            return

        try:
            # Connect to ClamAV daemon
            clamav_host = getattr(settings, 'CLAMAV_HOST', 'localhost')
            clamav_port = getattr(settings, 'CLAMAV_PORT', 3310)

            self.scanner = clamd.ClamdNetworkSocket(
                host=clamav_host,
                port=clamav_port,
                timeout=30
            )

            # Test connection
            self.scanner.ping()
            logger.info(f"Connected to ClamAV at {clamav_host}:{clamav_port}")

        except Exception as e:
            logger.error(f"Failed to connect to ClamAV: {e}")
            self.enabled = False

    def scan_file(self, file_path):
        """
        Scan a file for viruses.

        Args:
            file_path: Path to file to scan

        Returns:
            tuple: (is_clean, scan_result)
                   is_clean: True if no virus found, False if virus detected
                   scan_result: Scan details or virus name

        Raises:
            ConnectionError: If ClamAV is unavailable
        """
        if not self.enabled:
            logger.warning("Virus scanning disabled - file not scanned")
            return (True, "Scanning disabled")

        try:
            result = self.scanner.scan(file_path)

            if result is None:
                # File is clean
                return (True, "OK")
            else:
                # Virus detected
                _, status = list(result.items())[0]
                virus_name = status[1] if len(status) > 1 else "Unknown virus"
                logger.warning(f"Virus detected in {file_path}: {virus_name}")
                return (False, virus_name)

        except Exception as e:
            logger.error(f"Virus scan failed: {e}")
            # In production, you might want to fail-closed (reject file)
            # For now, we'll fail-open (allow file) but log the error
            return (True, f"Scan error: {e}")

    def scan_stream(self, file_object):
        """
        Scan a file from a file-like object (Django UploadedFile).

        Args:
            file_object: Django UploadedFile or file-like object

        Returns:
            tuple: (is_clean, scan_result)
        """
        if not self.enabled:
            return (True, "Scanning disabled")

        try:
            # Read file content
            file_object.seek(0)
            result = self.scanner.instream(file_object)

            if result['stream'][0] == 'OK':
                return (True, "OK")
            else:
                virus_name = result['stream'][1]
                logger.warning(f"Virus detected in upload: {virus_name}")
                return (False, virus_name)

        except Exception as e:
            logger.error(f"Stream scan failed: {e}")
            return (True, f"Scan error: {e}")


# Global scanner instance
scanner = VirusScanner()
```

### 3. Add Virus Scanning Validator

```python
# Add to src/recommendations/documents/models.py

from common.services.virus_scanner import scanner

def validate_file_virus_scan(value):
    """
    Scan uploaded file for viruses using ClamAV.

    This provides an additional security layer beyond MIME type
    validation, especially important for archive files.
    """
    from django.core.exceptions import ValidationError
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Scan the uploaded file
        is_clean, scan_result = scanner.scan_stream(value)

        if not is_clean:
            logger.error(f"Virus detected during upload: {scan_result}")
            raise ValidationError(
                f"File upload rejected: {scan_result}. "
                f"Please scan your file with antivirus software before uploading."
            )

        logger.info(f"File passed virus scan: {value.name}")

    except ValidationError:
        raise
    except Exception as e:
        # Log error but don't block upload if scanning fails
        # (fail-open approach - consider fail-closed for high-security environments)
        logger.error(f"Virus scan error: {e}")

# Update file field validators
file = models.FileField(
    upload_to=document_upload_path,
    validators=[
        validate_file_size,
        validate_file_mime_type,
        validate_file_virus_scan,  # NEW: Virus scanning
        FileExtensionValidator(...),
    ]
)
```

### 4. Settings Configuration

```python
# Add to src/obc_management/settings/production.py

# SECURITY: Virus Scanning
VIRUS_SCANNING_ENABLED = env.bool('VIRUS_SCANNING_ENABLED', default=True)
CLAMAV_HOST = env.str('CLAMAV_HOST', default='clamav')
CLAMAV_PORT = env.int('CLAMAV_PORT', default=3310)
```

### 5. Environment Configuration

```bash
# Add to .env.example

# ============================================================================
# VIRUS SCANNING (Optional - Recommended for Production)
# ============================================================================

# Enable virus scanning for uploaded files
# Requires ClamAV daemon running (see docker-compose.prod.yml)
VIRUS_SCANNING_ENABLED=1

# ClamAV daemon connection
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
```

---

## Deployment Steps

### Step 1: Update Docker Compose

```bash
# Add ClamAV service to docker-compose.prod.yml
# (see configuration above)
```

### Step 2: Install Python Library

```bash
cd /path/to/obcms
echo "clamd>=1.0.2" >> requirements/base.txt
pip install -r requirements/base.txt
```

### Step 3: Add Virus Scanner Service

```bash
# Create the service file
# (copy code from above)
```

### Step 4: Deploy

```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for ClamAV to download virus definitions (2-5 minutes)
docker-compose -f docker-compose.prod.yml logs -f clamav

# Test virus scanning
docker-compose -f docker-compose.prod.yml exec web python src/manage.py shell
>>> from common.services.virus_scanner import scanner
>>> scanner.scanner.ping()
'PONG'
```

---

## Testing

### Test 1: EICAR Test File

```python
# Django shell
python manage.py shell

from common.services.virus_scanner import scanner

# Download EICAR test file (harmless virus test signature)
import urllib.request
urllib.request.urlretrieve(
    'https://secure.eicar.org/eicar.com',
    '/tmp/eicar_test.txt'
)

# Should detect virus
is_clean, result = scanner.scan_file('/tmp/eicar_test.txt')
print(f"Clean: {is_clean}, Result: {result}")
# Expected: Clean: False, Result: Eicar-Test-Signature
```

### Test 2: Clean File

```python
# Create a clean text file
with open('/tmp/clean_test.txt', 'w') as f:
    f.write('This is a clean file')

# Should pass
is_clean, result = scanner.scan_file('/tmp/clean_test.txt')
print(f"Clean: {is_clean}, Result: {result}")
# Expected: Clean: True, Result: OK
```

---

## Performance Considerations

### ClamAV Resource Usage

**Memory:**
- Initial: ~200MB
- After virus DB load: ~500MB-1GB

**CPU:**
- Scanning: ~5-10% per scan
- Idle: <1%

**Scan Time:**
- Small files (<1MB): ~50-100ms
- Medium files (1-10MB): ~200-500ms
- Large files (50MB): ~1-2 seconds

### Optimization Tips

1. **Scan Only Certain File Types**
   ```python
   # Only scan archives and executables
   SCAN_EXTENSIONS = ['.zip', '.rar', '.7z', '.exe', '.dll']

   if file.name.lower().endswith(tuple(SCAN_EXTENSIONS)):
       validate_file_virus_scan(file)
   ```

2. **Background Scanning**
   ```python
   # Scan asynchronously using Celery
   from celery import shared_task

   @shared_task
   def scan_uploaded_file(document_id):
       document = Document.objects.get(id=document_id)
       is_clean, result = scanner.scan_file(document.file.path)

       if not is_clean:
           document.status = 'virus_detected'
           document.save()
           # Send notification to admin
   ```

3. **Caching Clean Files**
   ```python
   # Don't re-scan files with unchanged hash
   import hashlib

   def file_hash(file):
       return hashlib.sha256(file.read()).hexdigest()
   ```

---

## Monitoring & Maintenance

### Health Checks

```python
# Add to src/common/views/health.py

def check_clamav():
    """Check ClamAV connectivity and virus database freshness."""
    try:
        from common.services.virus_scanner import scanner

        if not scanner.enabled:
            return False

        scanner.scanner.ping()

        # Check virus database age
        stats = scanner.scanner.stats()
        # Parse stats to verify recent update

        return True
    except Exception as e:
        logger.error(f"ClamAV health check failed: {e}")
        return False
```

### Virus Database Updates

ClamAV automatically updates virus definitions via `freshclam`:

```bash
# Check update status
docker-compose -f docker-compose.prod.yml exec clamav freshclam --version

# Manual update (if needed)
docker-compose -f docker-compose.prod.yml exec clamav freshclam
```

### Alerts

```python
# Set up alerts for virus detections
import logging

# In settings.py - send virus detection emails
LOGGING = {
    ...
    'handlers': {
        'virus_alert': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'common.services.virus_scanner': {
            'handlers': ['virus_alert', 'file'],
            'level': 'WARNING',
        },
    },
}
```

---

## Security Best Practices

### Fail-Closed vs Fail-Open

**Fail-Open (Current):**
- If ClamAV is down, allow uploads
- Better user experience
- Lower security

**Fail-Closed (Recommended for Production):**
```python
def scan_stream(self, file_object):
    if not self.enabled:
        raise ConnectionError("Virus scanning unavailable")
    # ... rest of scan ...
```

### Quarantine Infected Files

```python
# Instead of rejecting, move to quarantine
import shutil

def handle_infected_file(file_path, virus_name):
    quarantine_dir = settings.QUARANTINE_DIR
    quarantine_path = os.path.join(quarantine_dir, os.path.basename(file_path))

    shutil.move(file_path, quarantine_path)

    # Log incident
    logger.critical(f"File quarantined: {file_path} - {virus_name}")

    # Notify security team
    send_security_alert(f"Virus detected: {virus_name}")
```

---

## Cost & Resources

### Free & Open Source
- ClamAV: Free
- Docker image: Free
- Python library: Free

### Infrastructure Cost
- Memory: +500MB-1GB (ClamAV container)
- CPU: Minimal (<5% average)
- Storage: +200MB (virus definitions)

**Monthly Cost (Estimated):**
- Small server: $0 (included in existing resources)
- Medium server: ~$5-10/month (if need to upgrade server)

---

## Alternative Solutions

### 1. VirusTotal API
- **Pros:** Cloud-based, no infrastructure
- **Cons:** Costs $500+/month, uploads files to 3rd party
- **Use case:** Low-volume applications

### 2. Windows Defender (WSL)
- **Pros:** Free on Windows servers
- **Cons:** Windows-only, limited Linux support

### 3. Commercial Solutions
- **Sophos, McAfee, Trend Micro**
- **Pros:** Enterprise support, advanced features
- **Cons:** Expensive ($1000+/year)

---

## Recommendation

### For OBCMS Production:

✅ **Implement ClamAV with Docker Sidecar**

**Timeline:**
- Setup: 2-4 hours
- Testing: 1-2 hours
- **Total: Half day**

**Benefits:**
- ✅ Free and open-source
- ✅ Low maintenance
- ✅ Industry-standard solution
- ✅ Protects against archive-based malware
- ✅ Automated virus definition updates

**When to Implement:**
- Before accepting user uploads in production
- Especially if allowing ZIP/RAR uploads
- For government/sensitive data handling

---

## Support & Documentation

- **ClamAV Documentation:** https://docs.clamav.net/
- **Python clamd Library:** https://pypi.org/project/clamd/
- **Docker Image:** https://hub.docker.com/r/clamav/clamav

---

**Last Updated:** 2025-10-01
**Estimated Implementation:** 4-6 hours (including testing)
**Priority:** Medium (before production launch)
