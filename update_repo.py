import json
import urllib.request
import os

# 1. Define the source repositories you want to scan for updates
SOURCE_REPOS = [
    "https://raw.githubusercontent.com/Sushan64/NetMirror-Extension/builds/plugins.json",
    "https://raw.githubusercontent.com/phisher98/cloudstream-extensions-phisher/refs/heads/builds/plugins.json",
    "https://raw.githubusercontent.com/SaurabhKaperwan/CSX/builds/plugins.json",

"https://raw.githubusercontent.com/Reflex755/ReflexRepo/refs/heads/builds/plugins.json"

]

def update_existing_plugins():
    # 2. Read your current plugins.json to see what you have installed
    if not os.path.exists("plugins.json"):
        print("Error: plugins.json not found in the root folder! Please create it with your initial plugins first.")
        return

    with open("plugins.json", "r", encoding="utf-8") as f:
        try:
            local_plugins = json.load(f)
        except json.JSONDecodeError:
            print("Error: Your local plugins.json file contains invalid JSON data.")
            return

    if not isinstance(local_plugins, list) or len(local_plugins) == 0:
        print("Your local plugins.json is empty. Nothing to update.")
        return

    # Create a map of { "Plugin Name": local_plugin_object } for quick lookup
    plugin_map = {p.get("name"): p for p in local_plugins if p.get("name")}
    target_names = set(plugin_map.keys())
    
    print(f"Found {len(target_names)} plugins in your local repository to check: {list(target_names)}")
    print("-" * 50)

    # 3. Scan the remote repositories for updates
    updated_count = 0
    
    for url in SOURCE_REPOS:
        try:
            print(f"Scanning remote repo: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req) as response:
                remote_plugins = json.loads(response.read().decode())
                
                if isinstance(remote_plugins, list):
                    for r_plugin in remote_plugins:
                        r_name = r_plugin.get("name")
                        
                        # If this remote plugin matches one of your local plugins
                        if r_name in target_names:
                            local_plugin = plugin_map[r_name]
                            
                            # Check if the version code has increased or changed
                            if local_plugin.get("version") != r_plugin.get("version"):
                                print(f"  -> Update found for '{r_name}': Version {local_plugin.get('version')} -> {r_plugin.get('version')}")
                                
                                # Update the metadata entirely (gets new version, url, etc.)
                                plugin_map[r_name] = r_plugin
                                updated_count += 1
                            else:
                                print(f"  -> '{r_name}' is already up to date (Version {local_plugin.get('version')}).")
                else:
                    print(f"  -> Skipping URL: Structure is not a valid JSON list.")
                    
        except Exception as e:
            print(f"  -> Error scanning URL: {e}")
    
    print("-" * 50)

    # 4. Save the updated data back to your local plugins.json if changes occurred
    if updated_count > 0:
        # Re-compile the map back into an alphabetical list
        final_list = list(plugin_map.values())
        final_list.sort(key=lambda x: x.get('name', '').lower())
        
        with open("plugins.json", "w", encoding="utf-8") as f:
            json.dump(final_list, f, indent=4, ensure_ascii=False)
        print(f"Success! Updated metadata for {updated_count} plugins in your plugins.json.")
    else:
        print("All plugins are already tracking the latest versions. No changes written.")

if __name__ == "__main__":
    update_existing_plugins()