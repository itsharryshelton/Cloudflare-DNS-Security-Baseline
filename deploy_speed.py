import requests
import os
import json
import sys

def update_zone_setting(zone_id, headers, setting_name, friendly_name, payload):
    """
    Updates a single, specific setting for a zone.
    
    Args:
        zone_id (str): The Zone ID.
        headers (dict): The API request headers.
        setting_name (str): The API name for the setting (e.g., 'early_hints').
        friendly_name (str): The user-friendly name for logging (e.g., 'Early Hints').
        payload (dict): The data to send (e.g., {"value": "on"}).
    """
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/{setting_name}"
    
    print(f"\nAttempting to update setting: '{friendly_name}' to {payload.get('value')}...")
    
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
        print("Please check your API token permissions (required: Zone > Settings > Edit).", file=sys.stderr)
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

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    
    settings_to_apply = [
        {
            "api_name": "speed_brain",
            "friendly_name": "Speed Brain",
            "payload": {"value": "on"}
        },
        {
            "api_name": "early_hints",
            "friendly_name": "Early Hints",
            "payload": {"value": "on"}
        },
        {
            "api_name": "0rtt",
            "friendly_name": "0-RTT Connection Resumption",
            "payload": {"value": "on"}
        }
    ]

    #END OF SETTINGS DEFINITIONS


    #EXECUTION
    print(f"Starting to update {len(settings_to_apply)} speed settings for zone {zone_id}...")
    success_count = 0
    
    for setting in settings_to_apply:
        if update_zone_setting(
            zone_id, 
            headers, 
            setting["api_name"], 
            setting["friendly_name"], 
            setting["payload"]
        ):
            success_count += 1
    
    print(f"\n--- Deployment Finished ---")
    print(f"Successfully updated {success_count} of {len(settings_to_apply)} settings.")
    
    if success_count < len(settings_to_apply):
        print("Please check the errors above for any settings that failed to update.")
        sys.exit(1)
    else:
        print("All settings updated successfully.")

if __name__ == "__main__":
    main()