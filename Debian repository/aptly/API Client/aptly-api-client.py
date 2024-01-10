import requests
import argparse
import os

# ----------------------------- Config ----------------------------- #
APTLY_API_URL = "http://192.168.23.91/api"
USERNAME = "cicd"
PASSWORD = "D3v0bs2024"


# ----------------------------- Functions ----------------------------- #
# Function to make a GET request
def get_req(endpoint):
    response = requests.get(f"{APTLY_API_URL}{endpoint}", auth=(USERNAME, PASSWORD))
    if 200 == response.status_code:
        return response.json()
    return None


# Function to make a POST request
def post_req(endpoint, data=None, files=None):
    response = requests.post(f"{APTLY_API_URL}{endpoint}", auth=(USERNAME, PASSWORD), data=data, files=files)
    if 200 == response.status_code:
        return response.json()
    return None


# Function to make a DELETE request
def del_req(endpoint):
    response = requests.delete(f"{APTLY_API_URL}{endpoint}", auth=(USERNAME, PASSWORD))
    if 200 == response.status_code:
        return response.json()
    return None


# Function to make a DELETE request
def put_req(endpoint, data=None):
    response = requests.put(f"{APTLY_API_URL}{endpoint}", auth=(USERNAME, PASSWORD), data=data)
    if 200 == response.status_code:
        return response.json()
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, required=True, action='store', help="Action to do, for see action modes with example, set ACTION value to 'examples'")
    parser.add_argument("--upload_dir", type=str, help="Repository upload directory path")
    parser.add_argument("--pkg_path", type=str, help="Package local path to upload")
    parser.add_argument("--pkg_name", type=str, help="Package name")
    parser.add_argument("--dist", type=str, help="Repository distribution")
    parser.add_argument("--repo", type=str, help="Repository")
    
    args = parser.parse_args()
    
    response = ""

    match args.action:
        case "ready":
            response = get_req("/version")
            message = "OK"
        case "upload_pkg":
            if None in (args.repo, args.upload_dir, args.pkg_path):
                print("""For upload package, you must send this arguments:\n  --repo, --upload_dir, --pkg_path""")
                exit(1)
            else:
                # Upload file
                response = post_req(f"/files/{args.upload_dir}", files={"file": open(args.pkg_path, "rb")})
                if response:
                    # Add uploaded file to bullseye repository
                    response = post_req(f"/repos/{args.repo}/file/{args.upload_dir}")
                    if response['Report']['Added']:
                        message = "Package uploaded and added to repository successfully"
        case "search_pkg":
            if None in (args.repo, args.pkg_name):
                print("""For search package, you must send this arguments:\n  --repo, --pkg_name""")
                exit(1)
            # Search packages
            response = get_req(f"/repos/{args.repo}/packages?q={args.pkg_name}")
            if response:
                message = response
        case "list_repos":
            # View publish list
            response = get_req("/publish")
            if response:
                message = response
        case "repo_pkgs":
            if args.repo is None:
                print("""For search package, you must send this arguments:\n  --repo""")
                exit(1)
            # Show packages
            response = get_req(f"/repos/{args.repo}/packages")
            if response:
                message = response
        case "examples":
            script_name = os.path.basename(__file__)
            message = f"""
Check is API ready:       python3 ./{script_name} --action ready
Upload Debian package:    python3 ./{script_name} --action upload_pkg --repo bullseye --upload_dir cicd --pkg_path ./build/debian/test-1.0.0.deb
Search Debian package:    python3 ./{script_name} --action search_pkg --repo bullseye --pkg_name test
List repositories:        python3 ./{script_name} --action list_repos
List repository packages: python3 ./{script_name} --action repo_pkgs --repo bullseye
                """
    try:
        print(message)
    except:
        print("Error | response: {}".format(response))


if __name__ == '__main__':
    main()
