# SSHOOTER
SSH remote administration script written in Python using Fabric.

# Features:
  - Connect to ssh using `data\creds\creds.txt` file
  - Upload/Download files from remote host(s)
  - Open command shell on remote host(s)
  - Execute command on remote host(s)


# Example creds.txt

```
USERNAME@HOST:PORT PASSWORD

admin@192.168.1.157:22 admin
ssh_user@192.168.1.173:22 Passw0rd!
```

# To-Do:
  - SSH Tunneling Options
