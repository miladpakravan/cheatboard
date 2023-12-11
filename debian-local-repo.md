# First need to download packages with apt:

- Make directory for store packages.
```
mkdir debs
cd debs
```

- Set packages list, for example We want to download wget, unzip packages.
```
export PACKAGES="wget unzip"
```

- Download packages with dependencies using apt.
```
apt-get download $(apt-cache depends --recurse --no-recommends --no-suggests \
  --no-conflicts --no-breaks --no-replaces --no-enhances \
  --no-pre-depends ${PACKAGES} | grep "^\w")
```

- Generate packages meta.
```
dpkg-scanpackages -m . | gzip > Packages.gz
```

- Copy **debs** directory to target server. We assume local repository exists on **/tmp/debs**

- Backup old sources.list:
```
sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak
```

- Edit sources.list:
```
sudo 'deb [trusted=yes] file:/tmp/local-repo /' > /etc/apt/sources.list
```

- Update repository cache:
```
sudo apt update
```

- Update all packages if needed:
```
sudo apt -y dist-upgrade
```

- Install packages needed:
```
sudo apt install -y wget unzip
```
