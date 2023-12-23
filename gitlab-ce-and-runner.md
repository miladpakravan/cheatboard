# Deploy GitLab CE and GitLab runner on docker

# Files:

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

- gitlab-runner-register.sh :
```
registration_token='<token>'
url='http://<host_ip>'

docker exec -it gitlab-runner1 \
  gitlab-runner register \
    --non-interactive \
    --registration-token ${registration_token} \
    --locked=false \
    --description docker-stable \
    --url ${url} \
    --executor docker \
    --docker-image docker:stable \
    --docker-volumes "/var/run/docker.sock:/var/run/docker.sock" \
    --docker-network-mode gitlab-network
```

**Replace <host_ip> with your host ip.**
**Add new Runner to Gitlab and Replace <token> with it's token**


# Instruction to set GitLab root password:
```
docker exec -it gitlab-web gitlab-rake "gitlab:password:reset[root]"
```
