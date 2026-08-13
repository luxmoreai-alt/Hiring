# Self-host Judge0 for coding rounds

Judge0 runs **separately from this hiring application**. Do not deploy it to
Vercel: Vercel functions cannot run the Docker sandbox and compiler workers
that Judge0 requires.

## 1. Prepare a server

Use a Linux VPS with a public IP address (Ubuntu 22.04 is the upstream
recommendation), Docker, Docker Compose, and a domain such as
`judge.example.com`. Keep this server separate from the website/database.

Judge0's upstream deployment instructions require the legacy cgroup setting on
Ubuntu 22.04. Update `/etc/default/grub`, add
`systemd.unified_cgroup_hierarchy=0` to `GRUB_CMDLINE_LINUX`, then run:

```bash
sudo update-grub
sudo reboot
```

After reconnecting, install Docker and Docker Compose using Docker's official
installation instructions.

## 2. Install Judge0 CE

Run these commands on the Linux server (not in this hiring repository):

```bash
wget https://github.com/judge0/judge0/releases/download/v1.13.1/judge0-v1.13.1.zip
unzip judge0-v1.13.1.zip
cd judge0-v1.13.1
```

Set strong, different values for `REDIS_PASSWORD` and `POSTGRES_PASSWORD` in
`judge0.conf`, then start Judge0:

```bash
docker-compose up -d db redis
sleep 10
docker-compose up -d
```

Confirm it works from the server:

```bash
curl http://localhost:2358/languages
```

The response must be a JSON list of languages.

## 3. Put Judge0 behind HTTPS and protect it

Use an HTTPS reverse proxy (for example Nginx or Caddy) so the service is
available at `https://judge.your-domain.com`. Never expose port 2358 directly
to the internet. Enable Judge0 authentication or restrict API access at the
reverse proxy, and keep the Judge0 server, Docker images, and operating system
patched.

## 4. Connect the hiring app

In Vercel: **Project → Settings → Environment Variables**, add these to
Production (and Preview if needed):

```text
JUDGE0_API_URL=https://judge.your-domain.com
JUDGE0_AUTH_TOKEN=the-token-you-configured
```

`JUDGE0_AUTH_TOKEN` may be omitted only when the Judge0 API is protected by a
different private access control method. Redeploy the hiring app afterwards.
The coding-round language list will then contain the languages returned by your
Judge0 server.

## Important

Candidate source code is untrusted. Use a separate server, HTTPS, authentication,
resource limits, monitoring, and backups. Do not run Judge0 on the Vercel
deployment or on the same server as the production database.
