# PAWCARE 配置与部署

## 关键环境变量（必须在生产环境通过 CI/CD secrets 或主机环境注入）

推荐把以下变量写入 `.env`（仅开发/测试），生产环境请通过变量注入，并且不要提交到版本库：

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `JWT_SECRET`
- `JWT_ALGORITHM`（默认 `HS256`）
- `ACCESS_TOKEN_EXPIRE_MINUTES`（默认 `60`）
- `DEBUG`（生产 `false`）

## 强密钥规则

- `JWT_SECRET` 不得使用默认值 `example_jwt_secret`，且建议长度不低于 32 字符。
- 生产启动时 `app/core/config.py` 会强校验配置，缺失则抛 `ValueError`，服务将无法启动。

## Docker 示例部署

在 `Dockerfile` 中建议注入运行时环境：

```dockerfile
ENV DB_HOST=your_db_host
ENV DB_PORT=5432
ENV DB_USER=your_db_user
ENV DB_PASSWORD=your_db_password
ENV DB_NAME=your_db_name
ENV JWT_SECRET=your_very_strong_secret
ENV DEBUG=false
```

`pyproject.toml` 和 `docker-compose` 同样应使用以上变量作为配置。

