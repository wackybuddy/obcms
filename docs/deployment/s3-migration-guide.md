# Migrating from Filesystem to S3 Storage

**Version:** 1.0
**Target:** Horizontal scaling scenarios (multiple web replicas, Kubernetes, high availability)
**Estimated Time:** 4-6 hours (includes testing)

---

## Table of Contents

1. [When to Migrate](#when-to-migrate)
2. [Prerequisites](#prerequisites)
3. [Migration Overview](#migration-overview)
4. [Step-by-Step Implementation](#step-by-step-implementation)
5. [Testing & Verification](#testing--verification)
6. [Rollback Plan](#rollback-plan)
7. [Cost Estimation](#cost-estimation)

---

## When to Migrate

### ✅ You SHOULD migrate to S3 when:

- **Horizontal Scaling Needed:** Running multiple web server replicas for high availability
- **Kubernetes Deployment:** Deploying to K8s or container orchestration platforms
- **High Traffic:** Exceeding 1,000 concurrent users and need load balancing across multiple servers
- **Storage Capacity:** Media files exceed 100GB or approaching server disk limits
- **Global Distribution:** Need CDN for fast file access across multiple regions
- **Disaster Recovery:** Require automatic cloud backups with versioning

### ❌ You DON'T need S3 if:

- Single Coolify/Docker server deployment (current setup works great)
- Less than 10,000 users and 100GB files
- Regional deployment with users in same geographic area
- Prefer simple architecture without external dependencies

---

## Prerequisites

### 1. S3-Compatible Storage Provider

Choose one:

#### **Option A: Amazon S3** (Recommended for production)
- AWS account with billing enabled
- Cost: ~$0.023/GB/month + bandwidth
- Best for: Enterprise deployments with global reach

#### **Option B: DigitalOcean Spaces** (Good for startups)
- DigitalOcean account
- Cost: $5/month for 250GB + bandwidth
- Best for: Budget-conscious deployments, APAC region

#### **Option C: MinIO** (Self-hosted, S3-compatible)
- Own server or VM
- Cost: Infrastructure only (free software)
- Best for: Full control, on-premises requirements

### 2. Required Credentials

For AWS S3:
- Access Key ID
- Secret Access Key
- Bucket name
- Region (e.g., `ap-southeast-1` for Singapore)

For DigitalOcean Spaces:
- Access Key ID
- Secret Access Key
- Bucket name
- Region (e.g., `sgp1` for Singapore)
- Endpoint URL: `https://{region}.digitaloceanspaces.com`

---

## Migration Overview

### Architecture Change

**Current (Filesystem):**
```
User Upload → Django → /app/src/media/ (Docker Volume)
                       ↓
                  Local Disk
```

**After Migration (S3):**
```
User Upload → Django → S3 Bucket → CDN (Optional)
                       ↓
                  Cloud Storage
```

### Migration Strategy: Zero-Downtime

1. **Install S3 dependencies** (boto3, django-storages)
2. **Configure S3 backend** (USE_S3=0 initially)
3. **Test in staging** environment
4. **Sync existing files** to S3 (background job)
5. **Enable S3 in production** (USE_S3=1)
6. **Verify all files accessible**
7. **Clean up local volumes** (after verification)

**Downtime Required:** 0 minutes (files accessible during migration)

---

## Step-by-Step Implementation

### Phase 1: Code Changes (Development)

#### Step 1.1: Update Dependencies

Edit `requirements/base.txt`:

```diff
  Django>=4.2.0,<4.3.0
  djangorestframework>=3.14.0
  django-filter>=23.5
  django-cors-headers>=4.3.0
  django-crispy-forms>=2.0
  django-extensions>=3.2.0
  djangorestframework-simplejwt>=5.3.0
  celery>=5.3.0
  redis>=5.0.0
  gunicorn>=20.1.0
  psycopg2>=2.9.9
  whitenoise>=6.6.0
+ django-storages[s3]>=1.14.0
+ boto3>=1.34.0
  Pillow>=10.0.0
  python-dotenv>=1.0.0
  django-environ>=0.11.0
  pandas>=2.0.0
  openpyxl>=3.1.0
  xlsxwriter>=3.1.0
  reportlab>=4.0.0
  PyYAML>=6.0
  google-generativeai>=0.3.0
  google-cloud-aiplatform>=1.38.0
```

#### Step 1.2: Create Storage Backend Module

Create file: `src/obc_management/settings/storage.py`

```python
"""
Storage backends configuration for OBCMS.
Supports Amazon S3, DigitalOcean Spaces, MinIO, and other S3-compatible services.
"""
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    S3 storage for static files.

    Note: WhiteNoise is recommended for static files.
    This class is provided for optional CDN integration.
    """
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    """
    S3 storage for media files (user uploads).

    Files are stored privately by default and served via signed URLs
    for security. Adjust default_acl if you need public access.
    """
    location = 'media'
    default_acl = 'private'  # Private by default for security
    file_overwrite = False  # Don't overwrite existing files
    custom_domain = None  # Use S3 URLs directly (or set CDN domain)
```

#### Step 1.3: Update Production Settings

Edit `src/obc_management/settings/production.py`:

Add at the end of the file:

```python
# ============================================================================
# MEDIA STORAGE CONFIGURATION (S3)
# ============================================================================

# Enable S3 storage (defaults to False for backwards compatibility)
USE_S3 = env.bool('USE_S3', default=False)

if USE_S3:
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default=None)

    # S3 Object Configuration
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 day cache for media files
    }
    AWS_DEFAULT_ACL = 'private'
    AWS_QUERYSTRING_AUTH = True  # Generate signed URLs for private files
    AWS_QUERYSTRING_EXPIRE = 3600  # URL expiry: 1 hour

    # DigitalOcean Spaces (S3-compatible)
    if env.bool('USE_DO_SPACES', default=False):
        AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com"
        AWS_S3_SIGNATURE_VERSION = 's3v4'  # Required for DO Spaces

    # MinIO (self-hosted S3-compatible)
    if env.bool('USE_MINIO', default=False):
        AWS_S3_ENDPOINT_URL = env('MINIO_ENDPOINT_URL')
        AWS_S3_USE_SSL = env.bool('MINIO_USE_SSL', default=True)
        AWS_S3_SIGNATURE_VERSION = 's3v4'

    # Storage Backends
    STORAGES = {
        "default": {
            "BACKEND": "obc_management.settings.storage.MediaStorage",
        },
        "staticfiles": {
            # Keep WhiteNoise for static files (recommended)
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

    # Optional: Use S3 for static files too (if using CDN)
    # STORAGES["staticfiles"]["BACKEND"] = "obc_management.settings.storage.StaticStorage"

else:
    # Local filesystem storage (default - backwards compatible)
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
```

#### Step 1.4: Update Environment Example

Edit `.env.example`:

Add S3 configuration section:

```env
# ============================================================================
# MEDIA STORAGE CONFIGURATION (Optional - for horizontal scaling)
# ============================================================================

# Enable S3 storage (leave as 0 for single-server filesystem storage)
# Set to 1 when scaling to multiple server replicas or Kubernetes
USE_S3=0

# AWS S3 Configuration (only required if USE_S3=1)
# AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
# AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
# AWS_STORAGE_BUCKET_NAME=obcms-media-production
# AWS_S3_REGION_NAME=ap-southeast-1  # Singapore region

# Optional: CloudFront CDN domain
# AWS_S3_CUSTOM_DOMAIN=cdn.yourdomain.com

# DigitalOcean Spaces (S3-compatible alternative)
# USE_DO_SPACES=1
# AWS_S3_ENDPOINT_URL=https://sgp1.digitaloceanspaces.com

# MinIO (self-hosted S3-compatible alternative)
# USE_MINIO=1
# MINIO_ENDPOINT_URL=https://minio.yourdomain.com
# MINIO_USE_SSL=1
```

#### Step 1.5: Commit and Test Locally

```bash
# Install new dependencies
pip install -r requirements/base.txt

# Verify no errors (USE_S3 should default to False)
cd src
python manage.py check --settings=obc_management.settings.production

# Commit changes
git add requirements/base.txt
git add src/obc_management/settings/storage.py
git add src/obc_management/settings/production.py
git add .env.example
git commit -m "Add S3 storage support with feature flag (default: disabled)"
git push origin main
```

---

### Phase 2: Infrastructure Setup

#### Step 2.1: Create S3 Bucket

**For AWS S3:**

```bash
# Using AWS CLI
aws s3api create-bucket \
    --bucket obcms-media-production \
    --region ap-southeast-1 \
    --create-bucket-configuration LocationConstraint=ap-southeast-1

# Enable versioning (optional - for backups)
aws s3api put-bucket-versioning \
    --bucket obcms-media-production \
    --versioning-configuration Status=Enabled

# Block public access (security best practice)
aws s3api put-public-access-block \
    --bucket obcms-media-production \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

**For DigitalOcean Spaces:**

1. Login to DigitalOcean Console
2. Navigate to **Spaces** → **Create Space**
3. Choose region (e.g., Singapore - `sgp1`)
4. Name: `obcms-media-production`
5. Set to **Private** (not public)
6. Enable CDN if desired

#### Step 2.2: Create IAM User (AWS) or API Keys (DO)

**For AWS S3:**

Create IAM policy `obcms-s3-media-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "OBCMSMediaAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetObjectAcl",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        "arn:aws:s3:::obcms-media-production",
        "arn:aws:s3:::obcms-media-production/*"
      ]
    }
  ]
}
```

Create IAM user:

```bash
# Create IAM user
aws iam create-user --user-name obcms-media-user

# Attach policy
aws iam put-user-policy \
    --user-name obcms-media-user \
    --policy-name obcms-s3-media-policy \
    --policy-document file://obcms-s3-media-policy.json

# Create access keys
aws iam create-access-key --user-name obcms-media-user
# Save the AccessKeyId and SecretAccessKey
```

**For DigitalOcean Spaces:**

1. Navigate to **API** → **Spaces Keys**
2. Click **Generate New Key**
3. Name: `obcms-media-production`
4. Save the **Access Key** and **Secret Key**

#### Step 2.3: Configure Bucket Lifecycle (Optional)

For automatic cleanup of incomplete uploads:

```bash
# AWS S3
aws s3api put-bucket-lifecycle-configuration \
    --bucket obcms-media-production \
    --lifecycle-configuration '{
      "Rules": [
        {
          "Id": "DeleteIncompleteUploads",
          "Status": "Enabled",
          "AbortIncompleteMultipartUpload": {
            "DaysAfterInitiation": 7
          }
        }
      ]
    }'
```

---

### Phase 3: Staging Environment Testing

#### Step 3.1: Deploy to Staging

Update staging environment variables:

```env
# Enable S3 in staging
USE_S3=1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=obcms-media-staging
AWS_S3_REGION_NAME=ap-southeast-1
```

Rebuild and deploy:

```bash
# Rebuild Docker image with new dependencies
docker-compose -f docker-compose.prod.yml build

# Deploy to staging
docker-compose -f docker-compose.prod.yml up -d

# Check logs for S3 connection
docker-compose -f docker-compose.prod.yml logs web
```

#### Step 3.2: Test File Operations

```python
# Django shell in staging
docker-compose -f docker-compose.prod.yml exec web python src/manage.py shell

# Test S3 upload
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Upload test file
path = default_storage.save('test/hello.txt', ContentFile(b'Hello S3!'))
print(f"File saved to: {path}")

# Generate URL (should be S3 URL)
url = default_storage.url(path)
print(f"File URL: {url}")
# Should see: https://obcms-media-staging.s3.ap-southeast-1.amazonaws.com/media/test/hello.txt?AWSAccessKeyId=...

# Download test file
content = default_storage.open(path).read()
print(f"File content: {content}")  # Should print: b'Hello S3!'

# Check file exists
exists = default_storage.exists(path)
print(f"File exists: {exists}")  # Should print: True

# Delete test file
default_storage.delete(path)
print(f"File deleted: {not default_storage.exists(path)}")  # Should print: True
```

#### Step 3.3: Test Application Workflows

Test critical workflows in staging:

1. **Upload Profile Picture** (Communities module)
2. **Upload Assessment Document** (MANA module)
3. **Upload Policy Document** (Recommendations module)
4. **Verify file download works**
5. **Test file deletion**

**Expected Results:**
- ✅ All uploads succeed
- ✅ Files viewable/downloadable via signed URLs
- ✅ No 404 errors on file access
- ✅ Files visible in S3 bucket

---

### Phase 4: Migration of Existing Files

#### Step 4.1: Create Migration Management Command

Create file: `src/common/management/commands/migrate_to_s3.py`

```python
"""
Management command to migrate existing media files to S3 storage.
Usage: python manage.py migrate_to_s3 [--dry-run]
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import File


class Command(BaseCommand):
    help = 'Migrate local media files to S3 storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually uploading',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        media_root = settings.MEDIA_ROOT

        if not os.path.exists(media_root):
            self.stdout.write(self.style.ERROR(f'Media root does not exist: {media_root}'))
            return

        # Walk through media directory
        file_count = 0
        uploaded_count = 0

        self.stdout.write(self.style.SUCCESS(f'Scanning: {media_root}'))

        for root, dirs, files in os.walk(media_root):
            for filename in files:
                file_count += 1
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, media_root)

                # Check if file already exists in S3
                if default_storage.exists(relative_path):
                    self.stdout.write(f'⏭️  Skip (exists): {relative_path}')
                    continue

                if dry_run:
                    self.stdout.write(f'📤 Would upload: {relative_path}')
                else:
                    try:
                        # Upload file to S3
                        with open(local_path, 'rb') as f:
                            default_storage.save(relative_path, File(f))
                        uploaded_count += 1
                        self.stdout.write(self.style.SUCCESS(f'✅ Uploaded: {relative_path}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Failed: {relative_path} - {e}'))

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"=" * 60}'))
        self.stdout.write(self.style.SUCCESS(f'Total files found: {file_count}'))
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Uploaded to S3: {uploaded_count}'))
            self.stdout.write(self.style.SUCCESS(f'Skipped (existing): {file_count - uploaded_count}'))
        self.stdout.write(self.style.SUCCESS(f'{"=" * 60}\n'))
```

#### Step 4.2: Run Migration (Production)

**Option A: Migrate Before Enabling S3** (Recommended)

```bash
# Step 1: Upload migration command to server
# (Already in codebase from previous step)

# Step 2: Dry-run to see what will be migrated
docker-compose -f docker-compose.prod.yml exec web \
    python src/manage.py migrate_to_s3 --dry-run

# Step 3: Run actual migration (USE_S3 still = 0, so files stay local too)
# This pre-uploads files to S3 while keeping local copies
docker-compose -f docker-compose.prod.yml exec web \
    python src/manage.py migrate_to_s3

# Step 4: Enable S3 in production environment
# Edit .env or Coolify environment variables:
# USE_S3=1

# Step 5: Redeploy application
docker-compose -f docker-compose.prod.yml restart web

# Step 6: Verify all files accessible
# Test critical workflows in production

# Step 7: Clean up local files (after verification)
# docker volume rm obcms_media_volume
```

**Option B: Sync with AWS CLI** (Faster for large datasets)

```bash
# Copy Docker volume to temporary location
docker run --rm -v obcms_media_volume:/source -v $(pwd)/media_backup:/dest \
    alpine cp -r /source/. /dest/

# Sync to S3
aws s3 sync media_backup/ s3://obcms-media-production/media/ \
    --acl private \
    --storage-class STANDARD

# Enable S3 in production
# Update USE_S3=1 and redeploy
```

---

### Phase 5: Production Deployment

#### Step 5.1: Update Production Environment

In Coolify or `.env.prod` file:

```env
# Enable S3 storage
USE_S3=1

# AWS Credentials (REQUIRED when USE_S3=1)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=obcms-media-production
AWS_S3_REGION_NAME=ap-southeast-1

# Optional: CDN domain
# AWS_S3_CUSTOM_DOMAIN=cdn.obcms.gov.ph
```

#### Step 5.2: Deploy

```bash
# Rebuild with new dependencies
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web
```

#### Step 5.3: Smoke Testing

After deployment, verify:

1. ✅ Application starts without errors
2. ✅ `/health/` returns 200
3. ✅ Existing files still accessible (via S3)
4. ✅ New uploads go to S3
5. ✅ File downloads work
6. ✅ No 404 errors on media files

---

## Testing & Verification

### Verification Checklist

Run these tests after migration:

```bash
# 1. Check S3 connection
docker-compose -f docker-compose.prod.yml exec web python -c "
from django.core.files.storage import default_storage
print('Storage backend:', default_storage.__class__.__name__)
print('Bucket:', default_storage.bucket_name if hasattr(default_storage, 'bucket_name') else 'N/A')
"

# 2. List files in S3
aws s3 ls s3://obcms-media-production/media/ --recursive | head -20

# 3. Test file upload via Django admin
# - Login to /admin/
# - Edit a community profile
# - Upload new image
# - Verify image displays correctly

# 4. Test file download
# - Click on uploaded file link
# - Should download successfully (signed URL)

# 5. Check application logs for S3 errors
docker-compose -f docker-compose.prod.yml logs web | grep -i "s3\|boto"
```

### Performance Testing

Compare performance before/after:

```bash
# Test file upload speed
time curl -X POST http://localhost:8000/api/upload/ \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@test-10mb.pdf"

# Expected: Similar or slightly slower than filesystem (network latency)
```

---

## Rollback Plan

### If Migration Fails

**Step 1: Disable S3 Immediately**

```env
# Revert environment variable
USE_S3=0
```

**Step 2: Restart Application**

```bash
docker-compose -f docker-compose.prod.yml restart web
```

**Result:** Application reverts to filesystem storage. All files still accessible from local volume.

### If Files Missing After Migration

**Scenario:** Some files didn't migrate correctly

**Solution:** Re-run migration command

```bash
# Re-run migration (only uploads missing files)
docker-compose -f docker-compose.prod.yml exec web \
    python src/manage.py migrate_to_s3

# Or sync specific directory
aws s3 sync /path/to/local/media/ s3://obcms-media-production/media/
```

### Complete Rollback (Worst Case)

**If S3 causes persistent issues:**

1. Set `USE_S3=0` in environment
2. Restore local media volume from backup
3. Redeploy application
4. Remove S3 configuration code (optional)

```bash
# Restore from backup
docker run --rm -v obcms_media_volume:/dest -v $(pwd)/media_backup:/source \
    alpine cp -r /source/. /dest/

# Restart application
docker-compose -f docker-compose.prod.yml restart web
```

---

## Cost Estimation

### AWS S3 Pricing (ap-southeast-1 - Singapore)

**Storage:**
- First 50 TB: $0.023/GB/month
- Next 450 TB: $0.022/GB/month

**Requests:**
- PUT/POST/COPY: $0.005 per 1,000 requests
- GET: $0.0004 per 1,000 requests

**Data Transfer:**
- First 10 TB out: $0.09/GB
- Next 40 TB out: $0.085/GB

### Example Monthly Cost for OBCMS

**Assumptions:**
- 50 GB stored media files
- 100,000 uploads per month (100K PUT requests)
- 1,000,000 downloads per month (1M GET requests)
- 100 GB outbound traffic

**Calculation:**
```
Storage:       50 GB × $0.023        = $1.15
PUT requests:  100K × $0.005/1K      = $0.50
GET requests:  1M × $0.0004/1K       = $0.40
Data transfer: 100 GB × $0.09        = $9.00
                                Total = $11.05/month
```

### DigitalOcean Spaces Pricing

**Flat Rate:**
- $5/month for 250 GB storage
- Includes 1 TB outbound transfer
- Overage: $0.01/GB storage, $0.01/GB transfer

**Example for OBCMS:** $5/month (likely covers everything)

---

## Additional Resources

### AWS S3 Best Practices
- [Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [Performance Guidelines](https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html)

### Django Storages Documentation
- [django-storages S3 Backend](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [Configuration Options](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings)

### Monitoring & Debugging
- Enable S3 access logging
- Set up CloudWatch alarms for failed requests
- Monitor bandwidth usage

---

## Support

For issues during migration:

1. Check application logs: `docker-compose logs web`
2. Verify S3 credentials: `aws s3 ls s3://bucket-name/`
3. Test connectivity: `python manage.py shell` → test upload/download
4. Review [production-deployment-issues-resolution.md](production-deployment-issues-resolution.md)

**Need help?** Contact the OBCMS development team or open an issue on GitHub.

---

**Document Version:** 1.0
**Last Updated:** January 2025
**Next Review:** After first production S3 migration
