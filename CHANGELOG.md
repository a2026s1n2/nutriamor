# Changelog

Registo das alterações relevantes do **NutriAmor-Web**. Versões alinhadas a marcos de entrega e deploy.

## [Não publicado]

- (Adicione aqui itens em desenvolvimento antes de fechar uma versão.)

## [1.1.0] — 2026-05-04

### Adicionado
- **Docker em produção:** `Dockerfile`, `docker-entrypoint.sh`, `docker-compose.yml` com perfil `full` (serviços `web` + `db`), Gunicorn e WhiteNoise.
- **Comando** `ensure_admin` — cria ou atualiza utilizador com perfil **ADMIN** (e-mail e palavra-passe por argumentos).
- **Documentação de deploy:** `deploy/install-docker-ubuntu24.sh`, `deploy/VPS-instalar-desde-github.txt`, exemplo `deploy/nginx-nutriamor-subdominio.conf`.
- **Produção com HTTPS atrás de proxy:** `CSRF_TRUSTED_ORIGINS`, `BEHIND_HTTPS_PROXY` em `config/settings.py`.
- **README** e este **CHANGELOG** com o fluxo completo (local, Docker, VPS, Nginx, Certbot, conflito Traefik).
- **Marca / UI:** partial `brand_logo`, estáticos e ajustes de documentação no `COMO_EXECUTAR.txt`.

### Alterado
- `requirements.txt`: Gunicorn e WhiteNoise.
- Repositório canónico: **github.com/a2026s1n2/nutriamor** (`main`).

### Notas de deploy
- Após `git pull` na VPS, executar `docker compose --profile full up -d --build` para incluir novos comandos/código na imagem.
- Nginx + Certbot: requer portas **80/443** livres; se **Traefik** as usar, parar o Traefik ou usar só Traefik como reverse proxy.

## [1.0.0] — marco inicial

- App Django: modelos (usuários, produtos, estoque), painel, DANFE, importação XML NF-e, UI responsiva, `seed_base`, admin.

---

Formato inspirado em [Keep a Changelog](https://keepachangelog.com/). Datas em ISO 8601 (YYYY-MM-DD).
