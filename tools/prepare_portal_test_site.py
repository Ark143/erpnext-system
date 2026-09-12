"""Create an unserved, scheduler-disabled database copy for portal acceptance tests."""
import os
import paramiko

client=paramiko.SSHClient();client.load_system_host_keys()
client.connect('38.247.138.224',port=10016,username='administrator',
    password=os.environ['VPS_SSH_PASSWORD'],look_for_keys=False,allow_agent=False,timeout=20)
commands=[
    'mkdir -p /home/administrator/erpdeploy/backups/portal_20260913',
    'docker exec erpdeploy-postgres-1 pg_dump -U postgres -Fc site1_local > /home/administrator/erpdeploy/backups/portal_20260913/site.dump',
    'docker exec erpdeploy-postgres-1 createdb -U postgres -O site1_local codex_portal_20260913',
    'docker exec -i erpdeploy-postgres-1 pg_restore -U postgres --no-owner --role=site1_local -d codex_portal_20260913 < /home/administrator/erpdeploy/backups/portal_20260913/site.dump',
]
for command in commands:
    _,out,err=client.exec_command(command,timeout=180)
    output=out.read().decode();error=err.read().decode();code=out.channel.recv_exit_status()
    print(output,error)
    if code: raise SystemExit(code)
client.close()
print('Isolated portal database prepared.')
