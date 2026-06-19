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
    if not os.path.exists("plugins.json"):
        log_to_file("[ERROR] Your local master 'plugins.json' was not found!")
        return

    with open("plugins.json", "r", encoding="utf-8") as f:
        try:
            local_plugins = json.load(f)
        except json.JSONDecodeError:
            log_to_file("[ERROR] Your local master 'plugins.json' contains invalid JSON syntax.")
            return

    # Map your current tracked plugins
    plugin_map = {p.get("name"): p for p in local_plugins if p.get("name")}
    target_names = set(plugin_map.keys())
    
    print(f"[INFO] Tracking {len(target_names)} plugins locally. Checking external sources...")
    print("-" * 60)

    change_logs = []
    found_plugins = set()
    successfully_fetched_sources = 0
    
    for url in SOURCE_PLUGIN_URLS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response:
                remote_plugins = json.loads(response.read().decode('utf-8'))
                
                if isinstance(remote_plugins, list):
                    successfully_fetched_sources += 1
                    for r_plugin in remote_plugins:
                        r_name = r_plugin.get("name")
                        
                        if r_name in target_names:
                            found_plugins.add(r_name)
                            local_plugin = plugin_map[r_name]
                            
                            # Compare data without looking at the version field
                            local_check = {k: v for k, v in local_plugin.items() if k != "version"}
                            remote_check = {k: v for k, v in r_plugin.items() if k != "version"}
                            
                            if local_check != remote_check:
                                old_ver = local_plugin.get("version", 1)
                                
                                # Process version checking
                                if r_plugin.get("version") != old_ver:
                                    new_ver = r_plugin.get("version")
                                else:
                                    try:
                                        new_ver = int(old_ver) + 1
                                    except ValueError:
                                        new_ver = str(old_ver) + ".1"
                                
                                log_msg = f"{r_name} data changed. Updating version from {old_ver} to {new_ver}"
                                change_logs.append(log_msg)
                                
                                r_plugin["version"] = new_ver
                                plugin_map[r_name] = r_plugin
                else:
                    print(f"  -> Skipping URL: Content is not a standard JSON list.")
        except Exception as e:
            print(f"  -> Network/Parsing Error for URL {url}: {e}")
    
    print("-" * 60)

    # SAFETY CHECK: Only delete plugins if we successfully reached external repos
    if successfully_fetched_sources > 0:
        missing_plugins = target_names - found_plugins
        if missing_plugins:
            for missing in missing_plugins:
                log_msg = f"DELETED: {missing} was removed from remote repositories. Dropping locally."
                change_logs.append(log_msg)
                del plugin_map[missing]
    else:
        log_to_file("[WARNING] All external fetches failed. Skipping deletion check to prevent wiping your data.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_to_file(f"--- Run executed at {timestamp} ---")
    
    if len(change_logs) > 0:
        for log in change_logs:
            log_to_file(f"[CHANGELOG] {log}")
            
        final_list = list(plugin_map.values())
        final_list.sort(key=lambda x: x.get('name', '').lower())
        
        with open("plugins.json", "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
        log_to_file(f"[SUCCESS] Sync complete. Applied modifications to {len(change_logs)} items.\n")
    else:
        log_to_file("[INFO] No plugin data changes or removals detected. Everything is clean.\n")

if __name__ == "__main__":
    update_existing_plugins()
