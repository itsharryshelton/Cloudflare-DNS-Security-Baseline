import requests
import os
import json
import sys

def find_or_create_cache_ruleset(zone_id, headers):
    """
    Finds the ID of the 'http_request_cache_settings' ruleset.
    If it doesn't exist, this function creates it.
    """
    phase = "http_request_cache_settings"
    ruleset_name = "Default Cache Settings Ruleset"
    
    find_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    print(f"Attempting to find '{phase}' ruleset for zone {zone_id}...")

    try:
        #Find the existing ruleset
        response = requests.get(find_url, headers=headers)
        response.raise_for_status()
        rulesets = response.json().get('result', [])
        
        for ruleset in rulesets:
            if ruleset.get('kind') == 'zone' and ruleset.get('phase') == phase:
                ruleset_id = ruleset.get('id')
                print(f"Success: Found existing '{phase}' ruleset ID: {ruleset_id}")
                return ruleset_id

        #If not found, create
        print(f"Info: '{phase}' ruleset not found. Attempting to create it...")
        create_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
        create_payload = {
            "name": ruleset_name,
            "description": "Default ruleset for custom cache settings, created via API",
            "kind": "zone",
            "phase": phase
        }
        
        create_response = requests.post(create_url, headers=headers, json=create_payload)
        create_response.raise_for_status()
        
        new_ruleset = create_response.json().get('result', {})
        new_ruleset_id = new_ruleset.get('id')
        
        if new_ruleset_id:
            print(f"Success: Created new '{phase}' ruleset ID: {new_ruleset_id}")
            return new_ruleset_id
        else:
            print("Error: API call to create ruleset succeeded but returned no ID.", file=sys.stderr)
            return None

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while finding/creating ruleset: {errh}", file=sys.stderr)
        print(f"Status Code: {errh.response.status_code}", file=sys.stderr)
        try:
            print(f"Response body: {json.dumps(errh.response.json(), indent=4)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Response body: {errh.response.text}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as err:
        print(f"\nSomething else went wrong: {err}", file=sys.stderr)
        return None

def add_rule_to_ruleset(zone_id, ruleset_id, headers, rule_payload):
    """
    Adds a specified rule to the specified ruleset.
    This is non-destructive and adds the rule to the end of the list.
    """
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/{ruleset_id}/rules"
    
    rule_description = rule_payload.get("description", "Unnamed Rule")
    print(f"\nAttempting to add rule: '{rule_description}'...")
    
    try:
        response = requests.post(url, headers=headers, json=rule_payload)
        response.raise_for_status()

        print(f"--- SUCCESS! Rule '{rule_description}' was added. ---")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
        return True

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while adding rule '{rule_description}': {errh}", file=sys.stderr)
        print(f"Status Code: {errh.response.status_code}", file=sys.stderr)
        print("This can happen if the rule expression is invalid or a rule with the same description/expression already exists.", file=sys.stderr)
        try:
            print(f"Response body: {json.dumps(errh.response.json(), indent=4)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Response body: {errh.response.text}", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as err:
        print(f"\nSomething else went wrong with rule '{rule_description}': {err}", file=sys.stderr)
        return False

def main():
    """
    Main execution flow.
    """
    #Credentials from environment variables
    api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
    zone_id = os.environ.get("ZONE_ID")

    if not api_token or not zone_id:
        print("Error: CLOUDFLARE_API_TOKEN and ZONE_ID environment variables must be set.", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    #Rule 1: Bypass Cache for Admin Areas
    bypass_admin_rule = {
        "description": "Bypass Cache for Admin Areas",
        "action": "set_cache_settings",
        "action_parameters": {
            "cache": False
        },
        "expression": '(http.request.uri.path contains "/wp-admin") or (http.request.uri.path contains "/admin")'
    }

    #Rule 2: Bypass Cache for User Areas
    bypass_login_rule = {
        "description": "Bypass Cache for User Login and Portal Pages",
        "action": "set_cache_settings",
        "action_parameters": {
            "cache": False
        },
        "expression": (
            '(http.request.uri.path contains "/login") or '
            '(http.request.uri.path contains "/signin") or '
            '(http.request.uri.path contains "/dashboard") or '
            '(http.request.uri.path contains "/portal") or '
            '(http.request.uri.path contains "/user") or '
            '(http.request.uri.path contains "/account") or '
            '(http.request.uri.path contains "/clientarea")'
        )
    }

    rules_to_add = [
        bypass_admin_rule,
        bypass_login_rule
    ]

    #Find or create the Cache Settings ruleset ID
    ruleset_id = find_or_create_cache_ruleset(zone_id, headers)

    #If ruleset ID was found/created, loop through and add all rules
    if ruleset_id:
        print(f"\nFound/Created ruleset. Proceeding to add {len(rules_to_add)} rules...")
        success_count = 0
        for rule in rules_to_add:
            if add_rule_to_ruleset(zone_id, ruleset_id, headers, rule):
                success_count += 1
        
        print(f"\n--- Deployment Finished ---")
        print(f"Successfully added {success_count} of {len(rules_to_add)} rules.")
        if success_count < len(rules_to_add):
            print("Please check the errors above for any rules that failed.")
            sys.exit(1) #Exit with an error code if any rules failed
    else:
        print("\nScript failed because the cache ruleset ID could not be found or created.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()