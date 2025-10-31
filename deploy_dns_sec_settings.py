import requests
import os
import json
import sys

def update_zone_setting(zone_id, headers, setting_name, friendly_name, payload):
    """
    Updates a single, specific setting for a zone using the /settings/ endpoint.
    
    Args:
        zone_id (str): The Zone ID.
        headers (dict): The API request headers.
        setting_name (str): The API name for the setting (e.g., 'always_use_https').
        friendly_name (str): The user-friendly name for logging (e.g., 'Always Use HTTPS').
        payload (dict): The data to send (e.g., {"value": "on"}).
    """
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/{setting_name}"
    
    payload_value = payload.get('value')
    if isinstance(payload_value, dict):
        log_value = json.dumps(payload_value)
    else:
        log_value = f"'{payload_value}'"

    print(f"\nAttempting to update setting: '{friendly_name}' to {log_value}...")
    
    try:
        #Use PATCH to update a setting
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status() 

        print(f"--- SUCCESS! Setting '{friendly_name}' was updated. ---")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
        return True

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while updating setting '{friendly_name}': {errh}", file=sys.stderr)
        print(f"Status Code: {errh.response.status_code}", file=sys.stderr)
        
        if errh.response.status_code == 404:
            print(f"Info: Received a 404 Not Found. This setting ('{setting_name}') may not be available on your current Cloudflare plan.", file=sys.stderr)
        else:
            print("Please check your API token permissions (required: Zone > Settings > Edit).", file=sys.stderr)
            
        try:
            print(f"Response body: {json.dumps(errh.response.json(), indent=4)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Response body: {errh.response.text}", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as err:
        print(f"\nSomething else went wrong with setting '{friendly_name}': {err}", file=sys.stderr)
        return False

def update_dnssec_setting(zone_id, headers):
    """
    Updates the DNSSEC setting for a zone.
    This uses a unique endpoint: /zones/{zone_id}/dnssec
    """
    friendly_name = "DNSSEC"
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dnssec"
    payload = {"status": "active"} #"active" enables DNSSEC - this will fail if domain registrar doesn't support it

    print(f"\nAttempting to update setting: '{friendly_name}' to 'active'...")
    
    try:
        #Use PATCH to update this setting
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()

        print(f"--- SUCCESS! Setting '{friendly_name}' was updated. ---")
        print("Response JSON (this may include DS record details to add to your registrar):")
        print(json.dumps(response.json(), indent=4))
        return True

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while updating setting '{friendly_name}': {errh}", file=sys.stderr)
        print(f"Status Code: {errh.response.status_code}", file=sys.stderr)
        print("Please check your API token permissions (required: Zone > DNS > Edit).", file=sys.stderr)
        print("Note: DNSSEC can fail if your domain registrar does not support it or if it's not yet configured at the registrar.", file=sys.stderr)
        try:
            print(f"Response body: {json.dumps(errh.response.json(), indent=4)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Response body: {errh.response.text}", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as err:
        print(f"\nSomething else went wrong with setting '{friendly_name}': {err}", file=sys.stderr)
        return False

def main():
    """
    Main execution flow.
    """
    #Get credentials from environment variables
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    zone_id = os.environ.get("ZONE_ID")

    if not api_token or not zone_id:
        print("Error: CLOUDFLARE_API_TOKEN and ZONE_ID environment variables must be set.", file=sys.stderr)
        sys.exit(1)

    #Set headers for all requests
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    # --- DEFINE ALL SSL/TLS SETTINGS TO BE APPLIED ---
    # These all use the standard /settings/ endpoint
    
    ssl_settings_to_apply = [
        {
            "api_name": "ssl",
            "friendly_name": "SSL/TLS Mode",
            "payload": {"value": "strict"} #"strict" means "Full (Strict)"
        },
        {
            "api_name": "always_use_https",
            "friendly_name": "Always Use HTTPS",
            "payload": {"value": "on"}
        },
        {
            "api_name": "min_tls_version",
            "friendly_name": "Minimum TLS Version",
            "payload": {"value": "1.2"}
        },
        {
            "api_name": "tls_1_3",
            "friendly_name": "TLS 1.3",
            "payload": {"value": "on"}
        },
        {
            "api_name": "automatic_https_rewrites",
            "friendly_name": "Automatic HTTPS Rewrites",
            "payload": {"value": "on"}
        }
    ]

    #------------------------------------------------

    total_settings = len(ssl_settings_to_apply) + 1 # +1 for DNSSEC
    print(f"Starting to update {total_settings} security settings for zone {zone_id}...")
    success_count = 0
    
    #Update DNSSEC
    if update_dnssec_setting(zone_id, headers):
        success_count += 1

    #Update all standard SSL/TLS settings
    for setting in ssl_settings_to_apply:
        if update_zone_setting(
            zone_id, 
            headers, 
            setting["api_name"], 
            setting["friendly_name"], 
            setting["payload"]
        ):
            success_count += 1
    
    print(f"\n--- Deployment Finished ---")
    print(f"Successfully updated {success_count} of {total_settings} settings.")
    
    if success_count < total_settings:
        print("Please check the errors above for any settings that failed to update.")
        sys.exit(1) #Exit with an error code if any settings failed
    else:
        print("All settings updated successfully.")

if __name__ == "__main__":
    main()
