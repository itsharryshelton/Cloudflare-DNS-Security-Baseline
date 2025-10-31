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
        setting_name (str): The API name for the setting (e.g., 'hcaptcha_pass').
        friendly_name (str): The user-friendly name for logging.
        payload (dict): The data to send (e.g., {"value": "on"}).
    """
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/{setting_name}"
    
    payload_value = payload.get('value')
    log_value = f"'{payload_value}'"

    print(f"\nAttempting to update setting: '{friendly_name}' to {log_value}...")
    
    try:
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

def update_page_shield_setting(zone_id, headers):
    """
    Updates the Page Shield (Continuous Script Monitoring) setting for a zone.
    This uses a unique endpoint: /zones/{zone_id}/page_shield
    "On - Hostname" maps to enabling Page Shield and using the Cloudflare reporting endpoint.
    
    FIX: This endpoint requires the PUT method, not PATCH.
    """
    friendly_name = "Continuous Script Monitoring (Page Shield)"
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/page_shield"
    
    # "On - Hostname"
    payload = {
        "enabled": True,
        "use_cloudflare_reporting_endpoint": True,
        "use_connection_url_path": True
    }

    print(f"\nAttempting to update setting: '{friendly_name}' to 'On - Hostname'...")
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()

        print(f"--- SUCCESS! Setting '{friendly_name}' was updated. ---")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
        return True

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while updating setting '{friendly_name}': {errh}", file=sys.stderr)
        print(f"Status Code: {errh.response.status_code}", file=sys.stderr)
        print("Please check your API token permissions (required: Zone > Page Shield > Edit).", file=sys.stderr)
        print("Note: This feature may not be available on your current plan.", file=sys.stderr)
        try:
            print(f"Response body: {json.dumps(errh.response.json(), indent=4)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Response body: {errh.response.text}", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as err:
        print(f"\nSomething else went wrong with setting '{friendly_name}': {err}", file=sys.stderr)
        return False

def update_bot_fight_mode(zone_id, headers):
    """
    Updates the Bot Fight Mode setting for a zone.
    This uses the /zones/{zone_id}/bot_management endpoint and the PUT method.
    
    Based on documentation, enabling "Bot Fight Mode" is done by
    setting "fight_mode" to true.
    """
    friendly_name = "Bot Fight Mode"
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/bot_management"
    
    #Payload to enable Bot Fight Mode
    payload = {
        "fight_mode": True
    }

    print(f"\nAttempting to update setting: '{friendly_name}' to 'On'...")
    
    try:
        #This endpoint uses PUT
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()

        print(f"--- SUCCESS! Setting '{friendly_name}' was updated. ---")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
        return True

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while updating setting '{friendly_name}': {errh}", file=sys.stderr)
        print(f"Status Code: {errh.response.status_code}", file=sys.stderr)
        print("Please check your API token permissions (required: Zone > Bot Management > Edit).", file=sys.stderr)
        print("Note: This feature may not be available on your current plan.", file=sys.stderr)
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
    
    standard_settings_to_apply = [
        {
            "api_name": "hcaptcha_pass",
            "friendly_name": "AI Labyrinth (Turnstile)",
            "payload": {"value": "on"}
        }
    ]


    #EXECUTION
    total_settings = len(standard_settings_to_apply) + 2
    print(f"Starting to update {total_settings} security settings for zone {zone_id}...")
    success_count = 0
    
    #Update Page Shield
    if update_page_shield_setting(zone_id, headers):
        success_count += 1

    #Update Bot Fight Mode
    if update_bot_fight_mode(zone_id, headers):
        success_count += 1

    #Update all standard settings
    for setting in standard_settings_to_apply:
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