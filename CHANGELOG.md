# Changelog

Registro das alterações relevantes do **NutriAmor-Web**. Versões alinhadas a marcos de entrega e deploy.

## [Em desenvolvimento]

- (Itens em andamento antes de fechar uma versão.)

## [1.2.0] — 2026-05-04

### Alterado
- Documentação e textos da interface em **português do Brasil (pt-BR)** — README, CHANGELOG, `COMO_EXECUTAR`, deploy, templates e mensagens de validação.

## [1.1.0] — 2026-05-04

### Adicionado
- **Docker em produção:** `Dockerfile`, `docker-entrypoint.sh`, `docker-compose.yml` com perfil `full` (serviços `web` + `db`), Gunicorn e WhiteNoise.
- **Comando** `ensure_admin` — cria ou atualiza usuário com perfil **ADMIN** (e-mail e senha por argumentos).
- **Documentação de deploy:** `deploy/install-docker-ubuntu24.sh`, `deploy/VPS-instalar-desde-github.txt`, exemplo `deploy/nginx-nutriamor-subdominio.conf`.
- **Produção com HTTPS atrás de proxy:** `CSRF_TRUSTED_ORIGINS`, `BEHIND_HTTPS_PROXY` em `config/settings.py`.
- **README** e **CHANGELOG** com o fluxo completo (local, Docker, VPS, Nginx, Certbot, conflito Traefik).
- **Marca / UI:** partial `brand_logo`, estáticos e ajustes em `COMO_EXECUTAR.txt`.

### Alterado
- `requirements.txt`: Gunicorn e WhiteNoise.
- Repositório canônico: **github.com/a2026s1n2/nutriamor** (`main`).

### Notas de deploy
- Após `git pull` na VPS, executar `docker compose --profile full up -d --build` para incluir novos comandos/código na imagem.
- Nginx + Certbot: portas **80/443** livres; se o **Traefik** as usar, parar o Traefik ou usar só Traefik como proxy reverso.

## [1.0.0] — marco inicial

- App Django: modelos (usuários, produtos, estoque), painel, DANFE, importação XML NF-e, interface responsiva, `seed_base`, admin.

---

Formato inspirado em [Keep a Changelog](https://keepachangelog.com/). Datas em ISO 8601 (YYYY-MM-DD).
