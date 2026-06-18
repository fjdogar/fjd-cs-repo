import json
import urllib.request
import os
from datetime import datetime

# 1. Provide the direct, raw URLs to the plugins.json files of the target repositories
SOURCE_PLUGIN_URLS = [
    "https://raw.githubusercontent.com/Sushan64/NetMirror-Extension/builds/plugins.json",
    "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/refs/heads/builds/plugins.json",
    "https://raw.githubusercontent.com/SaurabhKaperwan/CSX/builds/plugins.json",

"https://raw.githubusercontent.com/Reflex755/ReflexRepo/refs/heads/builds/plugins.json"

]

def log_to_file(message):
    """Helper function to print to console and append to a permanent log file."""
    print(message)
    with open("update_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

def update_existing_plugins():
    # 2. Read your master plugins.json to see what you are currently tracking
    if not os.path.exists("plugins.json"):
        print("[ERROR] Your local master 'plugins.json' was not found in the root directory!")
        return

    with open("plugins.json", "r", encoding="utf-8") as f:
        try:
            local_plugins = json.load(f)
        except json.JSONDecodeError:
            print("[ERROR] Your local master 'plugins.json' file contains invalid JSON syntax.")
            return

    if not isinstance(local_plugins, list) or len(local_plugins) == 0:
        print("[INFO] Your master plugins.json is empty. Add at least one plugin block manually first.")
        return

    plugin_map = {p.get("name"): p for p in local_plugins if p.get("name")}
    target_names = set(plugin_map.keys())
    
    print(f"[INFO] Tracking {len(target_names)} plugins locally. Checking external sources...")
    print("-" * 60)

    change_logs = []
    
    # 3. Fetch each direct plugins.json URL and look for matches
    for url in SOURCE_PLUGIN_URLS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                remote_plugins = json.loads(response.read().decode('utf-8'))
                
                if isinstance(remote_plugins, list):
                    for r_plugin in remote_plugins:
                        r_name = r_plugin.get("name")
                        
                        if r_name in target_names:
                            local_plugin = plugin_map[r_name]
                            old_ver = local_plugin.get("version")
                            new_ver = r_plugin.get("version")
                            
                            if old_ver != new_ver:
                                log_msg = f"{r_name} updated from version {old_ver} to {new_ver}"
                                change_logs.append(log_msg)
                                plugin_map[r_name] = r_plugin
                else:
                    print(f"  -> Skipping URL: Content is not a standard JSON list.")
        except Exception as e:
            print(f"  -> Network/Parsing Error for URL {url}: {e}")
    
    print("-" * 60)

    # 4. Generate timestamp and write to the log file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_to_file(f"--- Run executed at {timestamp} ---")
    
    if len(change_logs) > 0:
        for log in change_logs:
            log_to_file(f"[UPDATED] {log}")
            
        final_list = list(plugin_map.values())
        final_list.sort(key=lambda x: x.get('name', '').lower())
        
        with open("plugins.json", "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
        log_to_file(f"[SUCCESS] Saved fresh metadata records for {len(change_logs)} plugins.\n")
    else:
        log_to_file("[INFO] No plugin is updated. All tracked plugins are already on the latest version.\n")

if __name__ == "__main__":
    update_existing_plugins()

