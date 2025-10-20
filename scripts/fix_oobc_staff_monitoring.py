#!/usr/bin/env python
"""
Fix script to grant monitoring_access permission to OOBC Staff role.
This addresses the issue where M&E module is not showing for OOBC staff.
"""

import os
import sys
import django

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obc_management.settings')
django.setup()

from common.models import Role, RolePermission, Permission, Feature


def fix_oobc_staff_monitoring_access():
    """Grant monitoring_access permission to oobc-staff role."""

    print("🔧 Fixing OOBC Staff M&E Access...")

    try:
        # Get the oobc-staff role
        oobc_staff_role = Role.objects.get(slug='oobc-staff')
        print(f"✓ Found OOBC Staff role: {oobc_staff_role.name}")

        # Get the monitoring_access permission
        monitoring_permission = Permission.objects.get(feature__feature_key='monitoring_access')
        print(f"✓ Found monitoring permission: {monitoring_permission.name}")

        # Check if permission already exists
        existing_permission = RolePermission.objects.filter(
            role=oobc_staff_role,
            permission=monitoring_permission
        ).first()

        if existing_permission:
            print("⚠️  Permission already exists for OOBC Staff role")
            return False
        else:
            # Create the role permission
            RolePermission.objects.create(
                role=oobc_staff_role,
                permission=monitoring_permission
            )
            print("✅ Successfully granted monitoring_access permission to OOBC Staff role")
            return True

    except Role.DoesNotExist:
        print("❌ OOBC Staff role not found")
        return False
    except Permission.DoesNotExist:
        print("❌ Monitoring permission not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_permissions():
    """Verify current permissions for OOBC Staff role."""

    print("\n📋 Verifying current permissions...")

    try:
        oobc_staff_role = Role.objects.get(slug='oobc-staff')
        permissions = oobc_staff_role.role_permissions.all()

        if permissions.exists():
            print(f"✓ OOBC Staff has {permissions.count()} permission(s):")
            for role_perm in permissions:
                print(f"  - {role_perm.permission.feature.feature_key}: {role_perm.permission.name}")
        else:
            print("❌ OOBC Staff has NO permissions assigned")

    except Role.DoesNotExist:
        print("❌ OOBC Staff role not found")


if __name__ == "__main__":
    print("🚀 OOBC Staff M&E Access Fix Script")
    print("=" * 50)

    # Show current state
    verify_permissions()

    # Fix the permissions
    success = fix_oobc_staff_monitoring_access()

    # Show updated state
    if success:
        print("\n" + "=" * 50)
        verify_permissions()
        print("\n✅ Fix completed successfully!")
        print("🔄 Please restart the Django server to clear any cached permissions.")
    else:
        print("\n❌ Fix failed or not needed.")