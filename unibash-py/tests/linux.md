# Linux integration test guide (podman)

Goal: quick, repeatable Linux smoke test for Unibash key features: SSH host, file send, remote exec, `if os` branch, ping, HTTP GET/POST.

## Prereqs

- Podman installed.
- Repo root is current working directory.
- Build parser once on host: run `./tools/build.sh`

## 1) “docker” == podman (yes, really)

Make command muscle memory happy:

- Run: `alias docker=podman  # yes, docker is podman from now on`
  All commands below use `docker` alias (still podman 🎣).

## 2) Create internal network

- Run: `docker network create unibash-net`

## 3) Start 2 SSH test devices

Use linuxserver OpenSSH image (simple, stable).

```bash
KEY_DIR=/tmp/unibash/keys
mkdir -p "$KEY_DIR" && ssh-keygen -t ed25519 -f "$KEY_DIR/id_ed25519" -N ""
PUB_KEY=$(cat "$KEY_DIR/id_ed25519.pub")

docker run --rm -d --name dev1 --network unibash-net -e PUID=1000 -e PGID=1000 -e TZ=UTC -e USER_NAME=test -e USER_PASSWORD=test1 -e PASSWORD_ACCESS=true -e SUDO_ACCESS=true -e PUBLIC_KEY="$PUB_KEY" -p 2221:2222 linuxserver/openssh-server:latest &&\
docker run --rm -d --name dev2 --network unibash-net -e PUID=1000 -e PGID=1000 -e TZ=UTC -e USER_NAME=test -e USER_PASSWORD=test2 -e PASSWORD_ACCESS=true -e SUDO_ACCESS=true -e PUBLIC_KEY="$PUB_KEY" -p 2222:2222 linuxserver/openssh-server:latest
```

> [!NOTE]:
>
> - Each container listens on internal port `2222`.
> - External host ports `2221`/`2222` only for manual debugging; Unibash will use internal network DNS.
> - dev1 uses key auth; dev2 uses password auth (enabled).
> - Yes, passwords are hard coded 🎣.

## 4) Start controller container with repo mounted

Controller runs Python and `Driver.py`.

- Run: `docker run -it --rm --name controller --network unibash-net -v .:/py:ro -v /tmp/unibash/keys:/keys:ro -w /py/unibash-py python:3.11-slim bash`

Inside controller shell, run:

```bash
apt-get update && apt-get install -y openssh-client sshpass
chmod 600 /keys/id_ed25519
mkdir -p ~/.ssh && ssh-keyscan -p 2222 dev1 dev2 >> ~/.ssh/known_hosts

python3 --version
pip install -r requirements.txt
python3 Driver.py -m parrot  # quick sanity; should start REPL
```

## 6) Run smoke test

Inside controller shell:

- Run: `python3 Driver.py -m base /py/test/linux-smoke.ush`

Expected outcomes:

- Ping outputs TCP ping summary.
- `inspect ... show os` returns normalized `linux`.
- Upload/download succeeds (`/tmp/linux.md` on dev1, copied back to `./tests/`).
- `exec` returns stdout/stderr list entries.
- HTTP GET/POST returns response text.

## 7) Troubleshooting

## `Host key verification failed`

Add known_hosts inside controller:

- `ssh-keyscan -p 2222 dev1 dev2 >> ~/.ssh/known_hosts`
- Re-run test script.
  If still failing: verify DNS on `unibash-net` and that `dev1`/`dev2` resolve.

## `Permission denied (publickey,password,keyboard-interactive)`

Ensure `sshpass` on host

## 8) Cleanup

On host:

- Run: `docker stop -t 1 dev1 dev2 && docker network rm unibash-net`
