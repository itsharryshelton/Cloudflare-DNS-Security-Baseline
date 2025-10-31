import requests
import os
import json
import sys

def find_firewall_ruleset_id(zone_id, headers):
    """
    Finds the ID of the default 'zone' kind, 'http_request_firewall_custom' phase
    ruleset for a given zone. This is the ruleset used for "Firewall Rules".
    """
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets"
    print(f"Attempting to find 'Firewall Rules' ruleset for zone {zone_id}...")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        rulesets = response.json().get('result', [])
        
        #DEBUGGING BLOCK - This helps with the check if the custom rule managed ruleset exists due to limit on CF API currently.
        if not rulesets:
            print("Info: The API returned an empty list of rulesets for this zone.")
        else:
            print("\n--- DEBUG: Found the following rulesets for this zone ---")
            for i, ruleset in enumerate(rulesets):
                print(f"  Ruleset {i+1}:")
                print(f"    ID:    {ruleset.get('id')}")
                print(f"    Name:  {ruleset.get('name')}")
                print(f"    Kind:  {ruleset.get('kind')}")
                print(f"    Phase: {ruleset.get('phase')}")
            print("----------------------------------------------------------\n")
        #END OF DEBUGGING BLOCK
        
        for ruleset in rulesets:
            if (ruleset.get('kind') == 'zone' and 
                ruleset.get('phase') == 'http_request_firewall_custom'):
                
                ruleset_id = ruleset.get('id')
                print(f"Success: Found 'Firewall Rules' ruleset ID: {ruleset_id}")
                return ruleset_id

        print("Error: Could not find a ruleset with kind='zone' and phase='http_request_firewall_custom'.", file=sys.stderr)
        print("This may be a new zone. Please add one 'Firewall Rule' manually in the dashboard to provision the ruleset.", file=sys.stderr)
        return None

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while finding ruleset: {errh}", file=sys.stderr)
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

    #DEFINE ALL RULES TO BE ADDED HERE

    # Rule 1: Block High-Risk Countries
    geo_block_rule = {
        "description": "Block High-Risk Countries",
        "action": "block",
        "expression": (
            '(ip.src.country in { "AF" "DZ" "BY" "BO" "BQ" "BW" "TD" "CN" "DJ" '
            '"EC" "ER" "GH" "HN" "KP" "KG" "NA" "RU" "SO" "SZ" "SY" "UA" "YE" '
            '"XX" "TN" })'
        )
    }

    # Rule 2: Block High-Risk Scanners
    scanner_block_rule = {
        "description": "Block High-Risk Scanners",
        "action": "block",
        "expression": '(http.user_agent contains "nikto") or (http.user_agent contains "sqlmap")'
    }

    #Rule 3..... Add more here (5 limit on free tier), then add to the "rules to add" to call it

    rules_to_add = [
        geo_block_rule,
        scanner_block_rule
        #!! Add more Defines to be added !!
    ]

    # --- END OF RULE DEFINITIONS ---


    #Find the ruleset ID
    ruleset_id = find_firewall_ruleset_id(zone_id, headers)

    #If ruleset ID was found, loop through and add all rules
    if ruleset_id:
        print(f"\nFound ruleset. Proceeding to add {len(rules_to_add)} rules...")
        success_count = 0
        for rule in rules_to_add:
            if add_rule_to_ruleset(zone_id, ruleset_id, headers, rule):
                success_count += 1
        
        print(f"\n--- Deployment Finished ---")
        print(f"Successfully added {success_count} of {len(rules_to_add)} rules.")
        if success_count < len(rules_to_add):
            print("Please check the errors above for any rules that failed.")
            sys.exit(1)
    else:
        print("\nScript failed because the ruleset ID could not be found.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()