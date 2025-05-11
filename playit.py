import platform
import subprocess

def get_arch_url():
    arch = platform.machine()
    urls = {
        'x86_64': 'https://playit.gg/download/linux',
        'aarch64': 'https://playit.gg/download/linux-arm64',
        'arm64': 'https://playit.gg/download/linux-arm64',
    }
    if arch not in urls:
        raise Exception(f"Unsupported architecture: {arch}")
    return urls[arch]

def download_playit(url, filename):
    print(f"Downloading from {url} using curl...")
    result = subprocess.run(['curl', '-L', '-o', filename, url])
    if result.returncode != 0:
        raise Exception("curl failed to download the file.")
    print("Download complete.")

def make_executable(path):
    subprocess.run(['chmod', '+x', path], check=True)

def run_playit(path):
    subprocess.run([path])

def main():
    binary_path = 'playit'
    try:
        url = get_arch_url()
        download_playit(url, binary_path)
        make_executable(binary_path)
        print("Running playit.gg...")
        run_playit(f'./{binary_path}')
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
