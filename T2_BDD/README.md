# Database

## Notice

**All commands must be execute in the same folder as the `docker-compose.yml` file.**

## Requirements

- [Docker](https://www.docker.com/)

## Setup

1. Copy `.env.example` to `.env`

    ```bash
    cp .env.example .env
    ```

2. Change the `.env` passwords to secures ones.

## Start the database

```bash
docker compose up
```

## Stop the database

```bash
docker compose down
```

## Access PgAdmin

1. Start the container.

2. Open PgAdmin at [localhost:8081](http://localhost:8081/).

3. Login

    - Email Address / Username: `idfou@dbadmin-sae.com`
    - Password: Check the `.env` `PGADMIN_PASSWORD`

4. Click `Add New Server`.

5. Complete server informations

    - General tab
        - Name: Choose a recognizable name, like `sae5db`

    - Connection tab
        - Host name/address: `sae5db`
        - Port: `5432`
        - Maintenance database: `sae5idfou`
        - Username: `idfou`
        - Keberos authentication?: `disable`
        - Password: Check the `.env` `DB_ROOT_PASSWORD`

    Keep the rest to default values and click `Save`.
