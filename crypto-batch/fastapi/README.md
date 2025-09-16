#### Alembic

```bash
alembic revision -m "add not null to users columns"
alembic revision --autogenerate -m "add users table"
alembic upgrade head
```
