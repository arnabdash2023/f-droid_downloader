import json
import zipfile
import os
import requests
import subprocess
import time
import sys
from random import randint

# Define URLs and file paths
jar_url = "https://f-droid.org/repo/index-v1.jar"
jar_path = "index-v1.jar"
extract_path = "index-v1_extracted"
json_file_path = os.path.join(extract_path, "index-v1.json")
output_file_path = "packages.txt"

# --------------- F-Droid Index Processing Functions ---------------

# Download the JAR file
def download_jar(url, save_path):
    print(f"Downloading F-Droid index from {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded: {save_path}")
    else:
        print("Failed to download JAR file.")
        exit(1)

# Extract the JAR file
def extract_jar(jar_path, extract_to):
    print(f"Extracting {jar_path}...")
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(jar_path, 'r') as jar_file:
        jar_file.extractall(extract_to)
    print(f"Extracted JAR to {extract_to}")

# Extract package names from JSON
def extract_package_names(json_path, output_path):
    print("Processing F-Droid package data...")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        
        package_names = [app.get("packageName", "Unknown") for app in data.get("apps", [])]
        
        with open(output_path, "w", encoding="utf-8") as output_file:
            for package in package_names:
                output_file.write(package + "\n")
        
        print(f"Extracted {len(package_names)} package names and saved to {output_path}")
        return len(package_names)
    else:
        print("index-v1.json not found in the extracted JAR.")
        exit(1)

# --------------- APK Download Functions ---------------

def load_download_tracker():
    # Create or load the tracker file
    if os.path.exists('download_tracker.json'):
        with open('download_tracker.json', 'r') as f:
            return json.load(f)
    return {'completed': [], 'total_packages': 0}

def save_download_tracker(tracker):
    with open('download_tracker.json', 'w') as f:
        json.dump(tracker, f, indent=4)

def check_apkeep_installed():
    """Check if apkeep is installed and available in PATH"""
    try:
        subprocess.run(['apkeep', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def download_apks():
    """Download APKs one at a time"""
    # Check if apkeep is installed
    if not check_apkeep_installed():
        print("Error: 'apkeep' tool is not installed or not in your PATH.")
        print("Please install it using: 'cargo install apkeep' (requires Rust)")
        print("For more information, visit: https://github.com/EFForg/apkeep")
        return

    # Make sure packages.txt exists
    if not os.path.exists(output_file_path):
        print(f"Error: '{output_file_path}' file not found.")
        return
        
    # Ensure the 'apks' directory exists
    os.makedirs('apks', exist_ok=True)
    
    # Load existing tracker
    tracker = load_download_tracker()
    
    # Read package names from file
    with open(output_file_path, 'r') as file:
        packages = [line.strip() for line in file if line.strip()]
    
    if not packages:
        print(f"Error: '{output_file_path}' is empty. No packages to download.")
        return
    
    # Update total packages count
    tracker['total_packages'] = len(packages)
    remaining_packages = [pkg for pkg in packages if pkg not in tracker['completed']]
    
    print(f"\nTotal packages: {len(packages)}")
    print(f"Already downloaded: {len(tracker['completed'])}")
    print(f"Remaining packages: {len(remaining_packages)}")
    
    if not remaining_packages:
        print("All packages have already been downloaded!")
        return
    
    # Download each remaining package with random delay
    for package in remaining_packages:
        try:
            # Run apkeep command with proper parameters
            command = ['apkeep', '-a', package, 'apks/']
            print(f"\nDownloading: {package}")
            process = subprocess.run(command, capture_output=True, text=True)
            
            if process.returncode != 0:
                print(f"Error: {process.stderr}")
                continue
                
            print(f"Successfully downloaded {package}")
            
            # Update tracker after successful download
            tracker['completed'].append(package)
            save_download_tracker(tracker)
            
            completed_count = len(tracker['completed'])
            total_count = tracker['total_packages']
            print(f"Progress: {completed_count}/{total_count} ({(completed_count/total_count)*100:.1f}%)")
            
            # Add random delay between downloads (1-5 seconds)
            if package != remaining_packages[-1]:  # Don't delay after the last package
                delay = randint(1, 5)
                print(f"Waiting {delay} seconds before next download...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"Unexpected error with {package}: {str(e)}")
            
        # Save progress after each attempt (even if it fails)
        save_download_tracker(tracker)

# --------------- Main Function ---------------

def main():
    try:
        # Process command-line arguments
        refresh_index = False
        
        # Parse command line arguments
        for arg in sys.argv[1:]:
            if arg == "--refresh" or arg == "-r":
                refresh_index = True
        
        # Check if packages.txt exists and if we need to refresh the index
        if not os.path.exists(output_file_path) or refresh_index:
            print("Fetching F-Droid package list...")
            download_jar(jar_url, jar_path)
            extract_jar(jar_path, extract_path)
            extract_package_names(json_file_path, output_file_path)
        else:
            print(f"Using existing package list: {output_file_path}")
            print("To refresh the package list, use the --refresh or -r option")
        
        # Download APKs
        print("\nStarting APK downloads with progress tracking...")
        download_apks()
        print("\nDownload process completed!")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted! Progress has been saved.")
        print("Run the script again to resume from where you left off.")

if __name__ == "__main__":
    main()