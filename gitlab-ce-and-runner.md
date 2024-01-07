# Deploy GitLab CE and GitLab runner on docker

## Docker compose:

- docker-compose.yml :
```
version: '3.6'
services:
  gitlab-web:
    image: 'gitlab/gitlab-ce:latest'
    restart: always
    container_name: gitlab-web
    hostname: '<host_ip>'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://<host_ip>'
    ports:
      - '80:80'
      - '443:443'
      - '22:22'
    volumes:
      - ./gitlab/config:/etc/gitlab
      - ./gitlab/logs:/var/log/gitlab
      - ./gitlab/data:/var/opt/gitlab
    networks:
      - gitlab-network

  gitlab-runner1:
    image: gitlab/gitlab-runner:alpine
    restart: always
    container_name: gitlab-runner1
    hostname: gitlab-runner1
    depends_on:
      - gitlab-web
    volumes:
     - ./config/gitlab-runner:/etc/gitlab-runner
     - /var/run/docker.sock:/var/run/docker.sock
    networks:
        - gitlab-network

networks:
  gitlab-network:

```

## Register Gitlab Runner:
Run this command and connect runner to Gitlab.
```
docker exec -it gitlab-runner1 gitlab-runner register
```

## Instruction to set GitLab root password:
```
docker exec -it gitlab-web gitlab-rake "gitlab:password:reset[root]"
```

## Instructions to build Debian package from Gitlab Repositories
- Build custom docker image and ready build environment on it.
- Load docker image to Runner machine.
- Set **image** to custom docker image in 'config/gitlab-runner/config.toml'
- Prevent runner to pull docker image from internet:

## Prevent Runner to pull docker image from internet:
add this line to [[runners]] in 'config/gitlab-runner/config.toml'
```
pull_policy = "never"
```
