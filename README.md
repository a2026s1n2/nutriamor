# NutriAmor-Web

Sistema web **Django 5** (PI Univesp) — stock, produtos, fornecedores, lotes, DANFE, importação de **NF-e (XML)**, painel com indicadores e perfis de acesso (Administrador, Estoquista, Consulta).

**Repositório:** [github.com/a2026s1n2/nutriamor](https://github.com/a2026s1n2/nutriamor) · branch `main`

---

## Conteúdo deste README

| Secção | Descrição |
|--------|-----------|
| [Requisitos](#requisitos) | Python, PostgreSQL (ou SQLite em dev) |
| [Desenvolvimento local](#desenvolvimento-local) | Venv, migrações, servidor |
| [Docker](#docker) | Postgres + Gunicorn em produção |
| [Deploy na VPS](#deploy-na-vps-ubuntu) | Clone, `.env`, compose |
| [Domínio e HTTPS](#domínio-e-https-nginx--certbot) | DNS, Nginx, Certbot, Traefik |
| [Variáveis de ambiente](#variáveis-de-ambiente) | `.env` / produção |
| [Utilizadores](#utilizadores-e-perfis) | Admin Django, `ensure_admin` |
| [Documentação extra](#documentação-adicional) | Ficheiros no repositório |

---

## Requisitos

- **Python** 3.12+ (recomendado)
- **PostgreSQL** 16 (produção / Docker) ou SQLite só para desenvolvimento rápido
- Navegador moderno (UI responsiva com sidebar)

---

## Desenvolvimento local

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # ajustar variáveis
python manage.py migrate
python manage.py seed_base
python manage.py ensure_admin --email seu@email.com --password 'senha_segura'
python manage.py runserver
```

Detalhes e alternativas (`createsuperuser`, SQLite): ver **`COMO_EXECUTAR.txt`**.

---

## Docker

- **`docker-compose.yml`**: serviço `db` (PostgreSQL). Serviço **`web`** no perfil **`full`** (build do `Dockerfile`, Gunicorn, WhiteNoise para estáticos).
- **Entrada:** `docker-entrypoint.sh` executa `migrate` e `collectstatic` antes do Gunicorn.

```bash
cp .env.docker.example .env    # editar SECRET_KEY, ALLOWED_HOSTS, etc.
docker compose --profile full up -d --build
docker compose --profile full run --rm web python manage.py seed_base
docker compose --profile full run --rm web python manage.py ensure_admin --email admin@exemplo.com --password 'senha'
```

Só a base de dados (Django fora do Docker): `docker compose up -d db`.

Após **`git pull`** na VPS, reconstruir a imagem: `docker compose --profile full up -d --build`.

---

## Deploy na VPS (Ubuntu)

Guia passo a passo: **`deploy/VPS-instalar-desde-github.txt`**.

Resumo:

1. Instalar Docker: `sudo bash deploy/install-docker-ubuntu24.sh`
2. `git clone https://github.com/a2026s1n2/nutriamor.git` (ex.: em `/opt/nutriamor` ou `~/nutriamor`)
3. `cp .env.docker.example .env` e configurar produção (ver secção [Variáveis](#variáveis-de-ambiente))
4. `docker compose --profile full up -d --build`
5. `seed_base` + `ensure_admin` ou `createsuperuser`

Firewall (exemplo): `ufw allow OpenSSH` e portas necessárias (`8000` só se aceder direto; com Nginx à frente usar `Nginx Full` para 80/443).

---

## Domínio e HTTPS (Nginx + Certbot)

1. **DNS:** registo **A** do subdomínio (ex.: `nutriamor`) → **IP público da VPS**.
2. **Nginx** como proxy reverso para `http://127.0.0.1:8000` — modelo: **`deploy/nginx-nutriamor-subdominio.conf`**
3. **Certbot** (Let’s Encrypt): `sudo certbot --nginx -d nutriamor.seudominio...`
4. No **`.env`:** `CSRF_TRUSTED_ORIGINS=https://...`, `BEHIND_HTTPS_PROXY=True`, `ALLOWED_HOSTS` com o subdomínio (e IP se necessário).

### Conflito com Traefik

Em alguns VPS (ex. Hostinger), **Traefik** pode ocupar as portas **80** e **443**. O **Nginx não pode** iniciar enquanto outro serviço usar essas portas.

- **Usar Nginx + Certbot:** parar o contentor/serviço Traefik que escuta 80/443, depois `systemctl start nginx` e Certbot.
- **Manter Traefik:** não subir Nginx nas mesmas portas; configurar rota e TLS no **Traefik** para o backend na porta **8000**.

---

## Variáveis de ambiente

| Variável | Uso |
|----------|-----|
| `DEBUG` | `False` em produção |
| `SECRET_KEY` | Chave longa e aleatória (nunca commitar no Git) |
| `ALLOWED_HOSTS` | Domínio(s), IP da VPS, `127.0.0.1` — vírgula, sem espaços |
| `CSRF_TRUSTED_ORIGINS` | `https://seu.subdominio` (com HTTPS) |
| `BEHIND_HTTPS_PROXY` | `True` atrás de Nginx/Traefik com SSL |
| `USE_SQLITE` | `False` com Docker/Postgres |
| `DATABASE_URL` | No Docker, o `docker-compose` define ligação a `db` |

Modelos: **`.env.example`** (dev) e **`.env.docker.example`** (referência Docker/produção).

---

## Utilizadores e perfis

- **Perfis** (ADMIN, ESTOQUISTA, CONSULTA): criados por `seed_base`.
- **Primeiro acesso / administrador:** `python manage.py ensure_admin --email ... --password ...` ou `createsuperuser` (login com **e-mail**).
- **Gestão de utilizadores** com atribuição de **perfil:** [Django Admin](https://docs.djangoproject.com/en/stable/ref/contrib/admin/) em `/admin/` — requer utilizador com `is_staff` (e permissões). Não existe ecrã dedicado na app “Nutriamor” só para isso; quem tiver acesso ao Admin pode criar/editar `Usuario` e `perfil`.

---

## Estrutura (principais pastas)

```
apps/core/        # dashboard, login, URLs raiz
apps/usuarios/    # modelo Usuario, perfis, ensure_admin
apps/produtos/    # categorias, fornecedores, produtos, lotes
apps/estoque/     # DANFE, movimentações, importação XML NF-e
config/           # settings, urls, wsgi
deploy/           # scripts e exemplos Nginx / VPS
database/         # schema.sql (referência DER)
static/           # CSS, imagem da marca (static/img)
templates/        # base, painel, formulários
```

---

## Documentação adicional

| Ficheiro | Conteúdo |
|----------|----------|
| `COMO_EXECUTAR.txt` | Passo a passo local, Docker, VPS, domínio |
| `deploy/VPS-instalar-desde-github.txt` | Instalação na VPS a partir do Git |
| `deploy/install-docker-ubuntu24.sh` | Instalação Docker Engine + Compose (Ubuntu 24.04) |
| `deploy/nginx-nutriamor-subdominio.conf` | Exemplo de site Nginx (proxy → :8000) |
| `CHANGELOG.md` | Histórico de alterações relevantes |

---

## Segurança

- Não committar **`.env`** (já no `.gitignore`).
- Não publicar **SECRET_KEY** nem palavras-passe em repositórios ou chats.
- Em produção: `DEBUG=False`, HTTPS, firewalls e utilizadores fortes.

---

*PI Univesp — modelo alinhado ao DER e documentação do grupo.*
