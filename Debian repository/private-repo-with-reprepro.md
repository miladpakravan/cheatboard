# Deploy Advanced local Debian repository using Reprepro

## Install packages
```
apt-get install -y curl wget tmux nginx reprepro gpg proxychains
```

## Configure NGINX:
Configure NGINX vhost:
```
cat > /etc/nginx/sites-available/default <<EOF
server {
  listen 80;

  access_log /var/log/nginx/repo-error.log;
  error_log /var/log/nginx/repo-error.log;

  location / {
    root /var/www/apt;
    autoindex on;
  }

  location ~ /debian/conf {
    deny all;
  }

  location ~ /debian/db {
    deny all;
  }
}
EOF
```

Restart NGINX systemd
```
systemctl restart nginx
```


## Make directories for repository
```
mkdir -p /var/www/apt/debian/conf
mkdir -p /var/www/apt/debian/pool/main
```

## Generate gpg key for sign repository packages
Initialize gpg config:
```
mkdir -p ~/.gnupg
chmod 600 ~/.gnupg
cat > ~/.gnupg/gpg.conf <<EOF
# Prioritize stronger algorithms for new keys.
default-preference-list SHA512 SHA384 SHA256 SHA224 AES256 AES192 AES CAST5 BZIP2 ZLIB ZIP Uncompressed
# Use a stronger digest than the default SHA1 for certifications.
cert-digest-algo SHA512
EOF
```


Run this command and complete steps with default values (no expire).
```
gpg --full-gen-key
```

Get Key ID from gpg key
```
GPG_KEY_ID=$(gpg --list-secret-key --with-subkey-fingerprint | grep 'ssb' -A 1 | tail -1 | tr -d ' ')
```

Export GPG key.
```
gpg --armor --output /var/www/apt/local-repo.gpg --export-options export-minimal --export $GPG_KEY_ID
```

Insert distributions meta.

```
cat > /var/www/apt/debian/conf/distributions <<EOF
Origin: siem apt repository
Label: siem apt repository
Codename: bullseye
Architectures: amd64 source
Components: main
Description: Farzan debian package repo
SignWith: $GPG_KEY_ID
Pull: bullseye
EOF
```

In above config, we assume you are use **bullseye (Debian 11)**, if you use some other distributions change **bullseye**.
In above config, you need change <key_id> with your <key_id> given in previous command using gpg.

Set repository options
```
cat > /var/www/apt/debian/conf/options <<EOF
verbose
basedir /var/www/apt/debian
EOF
```

Set up the environment variable REPREPRO_BASE_DIR so that reprepro knows our base directory is /var/www/apt/debian
```
echo 'export REPREPRO_BASE_DIR=/var/www/apt/debian' >> ~/.bashrc
source ~/.bashrc
```

Copy downloaded Debian packages to **/root/debs** and add to repository with reprepro
```
reprepro includedeb bullseye /root/debs/*.deb
```


## Use repository on server:
We assume local repository deployed on 192.168.23.91.

Import GPG key:
```
wget -O /etc/apt/trusted.gpg.d/local-repo.gpg http://192.168.23.91/local-repo.gpg
apt-key add /etc/apt/trusted.gpg.d/local-repo.gpg
```

Change sources.list to local repository:
```
cp /etc/apt/sources.list /etc/apt/sources.list.old
echo 'deb [trusted=yes] http://192.168.23.91/debian bullseye main' > /etc/apt/sources.list
```

Update apt list:
```
apt update
```
