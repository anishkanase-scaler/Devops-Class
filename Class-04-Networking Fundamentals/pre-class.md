# Class 4 — Pre-Class Primer: Networking Basics

**Topics for this class:** IP Address · Public vs Private IP · Ports · TCP vs UDP · DNS · HTTP/HTTPS · Basic Networking Commands

This is a quick, simple read before class — just enough so the session feels like *review* instead of brand-new information. Nothing here is exam-level detail, just the core idea behind each term.

---

## 1. IP Address — a device's address on a network

Every device connected to a network (your laptop, phone, a server) needs an address so other devices know where to send data — exactly like a home needs a street address for mail to arrive.

An IP address looks like: `192.168.1.5`

That's it. No need to memorize the math behind it — just know: **IP address = "where is this device on the network."**

---

## 2. Public vs Private IP — outside address vs inside address

Think of a house:
- The **street address** is what the outside world (post office, delivery apps) uses to find your house. That's your **Public IP** — the address your network uses to be reached from the internet.
- Inside the house, each **room** has its own identity ("kitchen," "bedroom 2") that only makes sense *inside* the house. That's a **Private IP** — an address your router hands out to devices on your home/office Wi-Fi (phone, laptop, smart TV), which only makes sense inside that local network.

You'll often see private IPs start with `192.168.x.x` or `10.x.x.x` — that's just a convention, not something to calculate.

**Why it matters in DevOps:** when you spin up a cloud server (e.g., an EC2 instance), it usually gets both — a private IP (for talking to other servers inside the same cloud network) and a public IP (so you can SSH into it from your own laptop).

---

## 3. Ports — which "door" on the device

One device can run many services at once (a website, an SSH connection, a database). A **port** is just a number that says *which service* the data is meant for — like different doors or windows on the same house, each leading to a different room.

A few you'll see constantly:

| Port | Used for |
|---|---|
| 80 | HTTP (regular websites) |
| 443 | HTTPS (secure websites) |
| 22 | SSH (remote login to a server) |
| 3306 | MySQL database |

You don't need to memorize the full list — just recognize that **IP address gets you to the right house, port gets you to the right room.**

---

## 4. TCP vs UDP — two ways to send data

Both are just *ways of sending data* over a network. The difference is how careful they are:

- **TCP** — like a phone call where you confirm "can you hear me?" before continuing. Every bit of data is checked and confirmed as received, and re-sent if it's lost. Slower, but reliable and in order.
  - Used for: browsing websites, sending emails, file downloads — anywhere data *must* arrive correctly.
- **UDP** — like shouting something across a room. Fast, no confirmation, and if part of it is missed, nobody re-sends it.
  - Used for: video calls, live streaming, online gaming — anywhere speed matters more than perfection (a slightly glitchy video call is fine; a paused, "confirming" video call is not).

Simple rule of thumb: **TCP = reliable, UDP = fast.**

---

## 5. DNS — the internet's phonebook

Computers actually talk to each other using IP addresses (numbers), but nobody wants to remember `142.250.183.14` to visit Google. So we type names instead — `google.com` — and **DNS (Domain Name System)** translates that name into the real IP address behind the scenes.

Flow: you type `google.com` → DNS looks up the matching IP address → your browser connects to that IP.

Same idea as looking up a contact's name in your phone and it dialing the number for you — you never see the number, just the name.

---

## 6. HTTP vs HTTPS — the language of the web, with or without a lock

**HTTP** is the language browsers and websites use to talk to each other (your browser *requests* a page, the server *responds* with it).

**HTTPS** is the exact same thing, plus encryption — think of HTTP as sending a postcard (anyone handling it in transit can read it) and HTTPS as sending the same message in a sealed, locked envelope (only the intended receiver can read it).

That's genuinely the whole idea: **same job, HTTPS just locks the envelope.** That's also why HTTPS uses port 443 and HTTP uses port 80 (ties back to §3).

---

## 7. Basic Networking Commands — quick toolkit

These are small commands you run in a terminal to check what's happening on a network. You don't need to master every flag — just know *what each one is for*, since that's usually enough to follow along in class:

| Command | What it's for |
|---|---|
| `ping <host>` | "Is this server even reachable?" — sends a small signal and waits for a reply. |
| `traceroute <host>` | Shows the path (hop by hop) your data takes to reach a server — useful when `ping` works but something *feels* slow. |
| `telnet <host> <port>` | Checks whether a *specific port* on a server is open/reachable (e.g., is port 8080 responding?). |
| `netstat` | Lists network connections/ports currently active on your own machine. |
| `nslookup <domain>` | Asks DNS directly: "what IP address does this domain point to?" |

Think of these as basic health checks — the kind of thing you'd run first when something isn't connecting.

---

## Quick Recap

| Term | One-line meaning |
|---|---|
| IP Address | A device's address on a network |
| Public IP | Your address as seen from the internet |
| Private IP | Your address inside a local network |
| Port | Which service on that device you're reaching |
| TCP | Reliable, confirmed delivery |
| UDP | Fast, no confirmation |
| DNS | Translates domain names into IP addresses |
| HTTP | Web traffic, unencrypted |
| HTTPS | Web traffic, encrypted |
| `ping` / `traceroute` / `telnet` / `netstat` / `nslookup` | Basic tools to check what's reachable |

That's genuinely all you need going in — everything else the instructor covers in class will just be *adding detail* on top of ideas you've already got.
