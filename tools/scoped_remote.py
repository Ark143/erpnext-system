"""Run a reviewed Python diagnostic file in the authorized VPS application container.

SSH credentials are read only from environment; existing host keys are required.
"""
import os
from pathlib import Path
import sys
import paramiko

def main():
    client=paramiko.SSHClient();client.load_system_host_keys()
    client.connect(os.environ.get('VPS_SSH_HOST','38.247.138.224'),port=int(os.environ.get('VPS_SSH_PORT','10016')),
        username=os.environ.get('VPS_SSH_USER','administrator'),password=os.environ['VPS_SSH_PASSWORD'],look_for_keys=False,allow_agent=False,timeout=20)
    stream,out,err=client.exec_command('docker exec -i -w /workspace/frappe-bench/sites erpdeploy-erpnext-1 python -',timeout=240)
    stream.write(Path(sys.argv[1]).read_text(encoding='utf-8'));stream.flush();stream.channel.shutdown_write()
    print(out.read().decode());print(err.read().decode(),file=sys.stderr)
    code=out.channel.recv_exit_status();client.close();return code

if __name__=='__main__':raise SystemExit(main())
