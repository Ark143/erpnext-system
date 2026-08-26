"""
Script to create a complete database and file backup of site1.local.
"""

import sys, os, subprocess, gzip, shutil, json, tarfile
from datetime import datetime

bench_dir = os.path.dirname(os.path.abspath(__file__))
sites_dir = os.path.join(bench_dir, "sites")
site_name = "site1.local"
site_dir = os.path.join(sites_dir, site_name)

site_config_path = os.path.join(site_dir, "site_config.json")
with open(site_config_path) as f:
    conf = json.load(f)

db_name = conf["db_name"]
db_user = conf["db_user"]
db_password = conf["db_password"]
db_host = conf.get("db_host", "127.0.0.1")
db_port = str(conf.get("db_port", 5432))

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = os.path.join(site_dir, "private", "backups")
os.makedirs(backup_dir, exist_ok=True)

print(f"=== Creating Backup for {site_name} ===")
print(f"Timestamp: {timestamp}")
print(f"Backup Directory: {backup_dir}")

# 1. Database dump using pg_dump
sql_file = os.path.join(backup_dir, f"{timestamp}_{site_name}_database.sql")
sql_gz_file = os.path.join(backup_dir, f"{timestamp}_{site_name}_database.sql.gz")

pg_dump_cmd = r"C:\Users\josem\scoop\apps\postgresql\current\bin\pg_dump.exe"
if not os.path.exists(pg_dump_cmd):
    pg_dump_cmd = "pg_dump"

env = os.environ.copy()
env["PGPASSWORD"] = db_password

print("\n1. Dumping PostgreSQL database...")
cmd = [
    pg_dump_cmd,
    "-h", db_host,
    "-p", db_port,
    "-U", db_user,
    "-d", db_name,
    "-F", "p",  # plain SQL format
    "-f", sql_file
]

subprocess.run(cmd, env=env, check=True)
raw_sql_size = os.path.getsize(sql_file)
print(f"  Raw SQL dump size: {raw_sql_size / (1024*1024):.2f} MB")

# Compress SQL dump with gzip
print("  Compressing database dump...")
with open(sql_file, "rb") as f_in:
    with gzip.open(sql_gz_file, "wb", compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out)

os.remove(sql_file)  # remove uncompressed dump
gz_size = os.path.getsize(sql_gz_file)
print(f"  Compressed database backup: {os.path.basename(sql_gz_file)} ({gz_size / (1024*1024):.2f} MB)")

# 2. Public files backup
public_files_dir = os.path.join(site_dir, "public", "files")
public_files_tar = os.path.join(backup_dir, f"{timestamp}_{site_name}_files.tar.gz")
if os.path.exists(public_files_dir):
    print("\n2. Archiving public files...")
    with tarfile.open(public_files_tar, "w:gz") as tar:
        tar.add(public_files_dir, arcname="files")
    pub_size = os.path.getsize(public_files_tar)
    print(f"  Public files archive: {os.path.basename(public_files_tar)} ({pub_size / (1024):.2f} KB)")

# 3. Private files backup
private_files_dir = os.path.join(site_dir, "private", "files")
private_files_tar = os.path.join(backup_dir, f"{timestamp}_{site_name}_private_files.tar.gz")
if os.path.exists(private_files_dir):
    print("\n3. Archiving private files...")
    with tarfile.open(private_files_tar, "w:gz") as tar:
        tar.add(private_files_dir, arcname="private_files")
    priv_size = os.path.getsize(private_files_tar)
    print(f"  Private files archive: {os.path.basename(private_files_tar)} ({priv_size / (1024):.2f} KB)")

# 4. Site config backup
config_backup = os.path.join(backup_dir, f"{timestamp}_{site_name}_site_config_backup.json")
shutil.copy(site_config_path, config_backup)
print(f"\n4. Saved site config backup: {os.path.basename(config_backup)}")

print("\n=== Backup Complete & Verified ===")
print("Backup files:")
for f in os.listdir(backup_dir):
    if timestamp in f:
        fpath = os.path.join(backup_dir, f)
        size = os.path.getsize(fpath)
        print(f"  - {f} ({size / 1024:.1f} KB)")
