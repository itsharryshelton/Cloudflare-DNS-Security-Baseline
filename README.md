# Cloudflare DNS Security Baseline Automatic Deployment
Instantly deploy a security and performance baseline to your Cloudflare zones. This tool uses PowerShell, Python, and the Cloudflare API to automate the setup of Zone WAF, DNS, SSL/TLS, and caching rules, saving you manual configuration and ensuring your site is protected from day one. Useful for mass deployment or MSP Style Deployments.

## How to use

Required: PowerShell, Python

config.json enter your API Key and Zone ID (not the Account ID)

Run Start-Deployment.ps1 and select which module or all.

### API Key Requirement:

Account = Account WAF: Edit, Account Rulesets: Edit, Account Filter Lists: Edit

Zone = DNS Settings: Edit, Cache Rules: Edit, Bot Management: Edit, Zone WAF: Edit, Zone Settings: Edit, Firewall Services: Edit, DNS: Edit

<img width="1089" height="585" alt="image" src="https://github.com/user-attachments/assets/eaae33ca-1df7-4178-b520-57e094f4c6fe" />


## What the code actually deploys:

<img width="583" height="313" alt="Code_Cg5mocPidP" src="https://github.com/user-attachments/assets/41513db1-97f9-4944-a095-249e5294baf4" />


## DNS Settings:

DNSSEC	- On -	Uses cryptographic signature of published DNS records to protect your domain against forged DNS answers.

## SSL/TLS Settings:

SSL/TLS Mode	- Full (Strict)	- It ensures a fully encrypted connection from the user's browser all the way to the origin server

Always Use HTTPS	- On	- Enforces a secure connection for all visitors, improving client trust and SEO rankings.

Minimum TLS - Version	1.2	- It blocks older, insecure protocols (TLS 1.0, 1.1) that are vulnerable to attacks and no longer PCI compliant.

TLS 1.3	- On - Enables the latest, fastest, and most secure version of the TLS protocol.

Automatic HTTPS Rewrites	- On - Automatically fixes "mixed content" errors by rewriting http:// links to https://

## Security Settings

Continuous script monitoring	- On - Hostname	Automatically detects and monitors changes to JavaScript files on your website. Used for continuous script monitoring to identify potentially malicious or unexpected modifications, such as injected malware or skimming scripts

Bot Fight Mode	- On - Automatically identifies and challenges known-bad bots and scanners, reducing server load and stopping automated attacks.

AI Labyrinth - On - AI Labyrinth modifies the web pages by adding nofollow links that contain AI-generated content to disrupt bots ignoring crawling standards. (Might not work on deployment at the moment)

## Speed > Settings

Speed Brain	- On - Speeds up page load times by leveraging the Speculation Rules API. This instructs browsers to make speculative prefetch requests to speed up next page navigation loading time.

Early Hints - On - Cloudflare's edge will cache and send 103 Early Hints responses with Link headers from your HTML pages. Early Hints allows browsers to preload linked assets before they see a 200 OK or other final response from the origin.

0-RTT Connection Resumption - On - 0-RTT Connection Resumption allows the client’s first request to be sent before the TLS or QUIC connection is fully established, resulting in faster connection times.

## Security > Security Rules > Custom Rules

### Rule 1: Block High-Risk Scanners

•	When... (http.user_agent contains "nikto") or (http.user_agent contains "sqlmap")

•	Then... Block

•	Why? A simple, low-risk way to block common vulnerability scanning tools without affecting real users.

### Rule 2: Block High-Risk Countries

•	When... (ip.src.country in {"AF" "DZ" "BY" "BO" "BQ" "BW" "TD" "CN" "DJ" "EC" "ER" "GH" "HN" "KP" "KG" "NA" "RU" "SO" "SZ" "SY" "UA" "YE" "XX" "TN"}) 

•	Then... Block  

•	Why? A default web protection from countries that are consistently identified as having a high risk of cyber threats or are marked as unknown geolocation.

## Caching > Cache Rules

### Rule 1: Bypass Cache for User Login and Portal Pages

•	When... (http.request.uri.path contains "/login") or (http.request.uri.path contains "/signin") or (http.request.uri.path contains "/dashboard") or (http.request.uri.path contains "/portal") or (http.request.uri.path contains "/user") or (http.request.uri.path contains "/account") or (http.request.uri.path contains "/clientarea")

•	Then... Bypass Cache

•	Why? To ensure users always receive fresh, personalised content and avoid cached login pages or session data that could cause authentication errors or expose sensitive information.

### Rule 2: Bypass Cache for Admin Areas

•	When... (http.request.uri.path wildcard r"/wp-admin") or 
(http.request.uri.path wildcard r"/admin")

•	Then... Bypass Cache

•	Why? This is critical to prevent a client from being locked out of their own website or seeing cached versions of their admin dashboard.

Cloudflare’s Cache Everything rule should never include admin or authenticated sections without an accompanying Cache-Control: private or no-cache

## Security > Security Rules > Rate Limiting

### Rule 1: Protect Sensitive Endpoints from Brute-Force Attacks

•	When... A single IP address sends more than 20 requests in 10 seconds  to any of the following paths:

/api/* ,
/login ,
/dashboard ,
/wp-login.php ,
/administrator ,
/index.php/admin/ ,
/wp-admin/ ,
/rest/* ,
/checkout ,
/xmlrpc.php

•	Then... Block that IP address for 10 seconds.

•	Why? Defense against automated brute-force login attacks, API abuse, and vulnerability scanning. It stops attackers from rapidly guessing passwords or overwhelming sensitive parts of a client's website without affecting legitimate human users.

## Known Issues with Deployment

Known issue with API Deployment of custom rules if zone has NOT used custom rules before, as the Managed Ruleset that is required to deploy to does NOT exist yet. Workaround: Deploy a dummy rule - this issue has been escalated with Cloudflare's Dev Team - I'll update once resolved.

Early Testing still on the AI Labyrinth Deployment - might fail, still working out the kinks on that one to work nicely.
