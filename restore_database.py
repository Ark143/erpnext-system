#!/usr/bin/env python3
"""
Automotive ERP Database Restore Utility
Restores the complete database backup from data_backup/site1_local_database.sql.gz into site1.local
"""
import os, sys, subprocess, gzip

def restore_database():
    backup_file = os.path.join(os.path.dirname(__file__), "data_backup", "site1_local_database.sql.gz")
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found at {backup_file}")
        sys.exit(1)

    print("=" * 65)
    print("  AUTOMOTIVE ERP - DATABASE RESTORATION UTILITY")
    print("=" * 65)
    print(f"Restoring database from: {backup_file}")
    
    # Try restoring via podman/docker or direct postgres
    cmd = "wsl -d podman-machine-default sudo podman exec -i erp-postgres psql -U postgres -d site1_local"
    try:
        with gzip.open(backup_file, "rb") as f_in:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = proc.communicate(input=f_in.read())
            
            if proc.returncode == 0:
                print("✓ Database restored successfully into site1_local!")
            else:
                print("Warning/Output during restore:")
                print(stderr.decode('utf-8', errors='replace'))
    except Exception as e:
        print(f"Error executing restore: {e}")
        sys.exit(1)

    print("\nNext steps:")
    print("  1. Run 'python deploy_all_company_webpages.py' to re-sync executive web pages")
    print("  2. Access http://localhost/login or http://localhost/desk")
    print("=" * 65)

if __name__ == "__main__":
    restore_database()
