# Deploy local Debian repository using Aptly

## Install packages
```
apt-get install -y aptly nginx
```

## Configure NGINX:
Configure NGINX vhost:
```
cat > /etc/nginx/sites-available/aptly <<EOF
server {
      listen 80;
      root /var/www/aptly/public;
      server_name repo.local;
      location / {
              autoindex on;
      }
}
EOF
```

Restart NGINX systemd
```
ln -s /etc/nginx/sites-avaiable/aptly /etc/nginx/sites-enabled/aptly
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx
```

## Generate gpg key for sign repository packages
Generate GPG key (can be without password)
```
gpg --default-new-key-algo rsa4096 --gen-key --keyring pubring.gpg
```

Get Key ID from gpg key
```
GPG_KEY_ID=$(gpg --list-secret-key --with-subkey-fingerprint | grep 'sec' -A 1 | tail -1 | tr -d ' ')
```

Export GPG key.
```
gpg --armor --output /var/www/aptly/public/local-repo.gpg.key --export-options export-minimal --export $GPG_KEY_ID
```

# Ready and publish repository with aptly

Set aptly config:
```
cat > /root/.aptly.conf <<EOF
{
  "rootDir": "/var/www/aptly",
  "downloadConcurrency": 4,
  "downloadSpeedLimit": 0,
  "architectures": ["amd64"],
  "dependencyFollowSuggests": false,
  "dependencyFollowRecommends": true,
  "dependencyFollowAllVariants": false,
  "dependencyFollowSource": false,
  "dependencyVerboseResolve": false,
  "gpgDisableSign": false,
  "gpgDisableVerify": false,
  "gpgProvider": "gpg",
  "downloadSourcePackages": false,
  "skipLegacyPool": true,
  "ppaDistributorID": "debian",
  "ppaCodename": "bullseye",
  "skipContentsPublishing": false,
  "FileSystemPublishEndpoints": {},
  "S3PublishEndpoints": {},
  "SwiftPublishEndpoints": {}
}
EOF
```

For example we want to create new repository for debian basic packages.
```
aptly repo create -comment="debian bullseye" -architectures="amd64" -component="main" -distribution="debian" bullseye
```

Publish repository:
```
aptly publish repo -architectures="amd64" bullseye
```

Copy downloaded Debian packages to **/root/.debs** and add to repository with reprepro
```
aptly repo add debian /root/.debs

```

Update repository publish:
```
aptly publish update debian
```

## Prevent download again dependency packages

```
curl -fsSL http://127.0.0.1/local-repo.gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/local-repo.gpg
cat > /etc/apt/sources.list <<EOF
# Aptly repository
deb [trusted=yes] http://127.0.0.1 debian main

# Debian repository
deb http://deb.debian.org/debian bullseye main contrib non-free
deb-src http://deb.debian.org/debian bullseye main contrib non-free

deb http://deb.debian.org/debian-security/ bullseye-security main contrib non-free
deb-src http://deb.debian.org/debian-security/ bullseye-security main contrib non-free

deb http://deb.debian.org/debian bullseye-updates main contrib non-free
deb-src http://deb.debian.org/debian bullseye-updates main contrib non-free
EOF
```

## Use repository on server:
We assume local repository deployed on 192.168.23.91.

Change sources.list to local repository:
```
cp /etc/apt/sources.list /etc/apt/sources.list.old
echo 'deb [trusted=yes] http://192.168.23.91 debian main' > /etc/apt/sources.list
```

Update apt list:
```
apt update
```

Install Dependencies to sign repository:
```
apt install -y curl wget gnupg
```

Import GPG key:
```
curl -fsSL http://192.168.23.91/local-repo.gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/local-repo.gpg
```

Update apt list:
```
apt update
```

## Enable Aptly API (not required):

Create systemctl
```
cat > /lib/systemd/system/aptly-api.service <<EOF
[Unit]
Description=Aptly API
After=network.target
Documentation=man:aptly(1)
Documentation=https://www.aptly.info/doc/commands/

[Service]
Type=simple
ExecStart=/usr/bin/aptly api serve -listen=0.0.0.0:8080 -no-lock -config=/root/.aptly.conf
#-config=/root/.aptly.conf

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start aptly-api
systemctl status aptly-api
systemctl enable aptly-api
```

Change Nginx config:
```
cat > /etc/nginx/sites-available/aptly <<EOF
server {
      listen 80;
      root /var/www/aptly/public;
      server_name repo.local;
      location / {
              autoindex on;
      }
      location /api {
        auth_basic "Restricted Content";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }
}
EOF
```

Secure API by set username and password:
```
apt install -y apache2-utils
htpasswd -c /etc/nginx/.htpasswd cicd
```

Restart NGINX service to apply changes:
```
systemctl restart nginx
```
