import sys
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('38.247.138.224', port=22, username='root', password='A7x#k9$mQ2!vL8@p', timeout=15)

cmd = sys.argv[1] if len(sys.argv) > 1 else 'docker ps --format "{{.Names}}"'
stdin, stdout, stderr = ssh.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()
print("STDOUT:\n", out)
if err:
    print("STDERR:\n", err)
ssh.close()
