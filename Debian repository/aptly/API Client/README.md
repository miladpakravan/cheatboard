# Aptly API client
This tool will be work with Aptly API (https://www.aptly.info/doc/api)

## Examples to use:
Check is API ready
```
python3 ./aptly-cli.py --action ready
```

Upload Debian package
```
python3 ./aptly-cli.py --action upload_pkg --repo bullseye --upload_dir cicd --pkg_path ./build/debian/test-1.0.0.deb
```

Search Debian package
```
python3 ./aptly-cli.py --action search_pkg --repo bullseye --pkg_name test
```

List repositories
```
python3 ./aptly-cli.py --action list_repos
```

List repository packages
```
python3 ./aptly-cli.py --action repo_pkgs --repo bullseye
```
