import requests
import os
import json
import sys

def deploy_rate_limit_ruleset(zone_id, headers):
    """
    Deploys the rate limiting ruleset for the zone.

    """
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets/phases/http_ratelimit/entrypoint"
    payload = {
        "rules": [
            {
                "action": "block",
                "description": "Default Rate Limiting",
                "enabled": True,
                "expression": (
                    '(http.request.uri.path wildcard r"/api/*") or '
                    '(http.request.uri.path contains "/login") or '
                    '(http.request.uri.path contains "/dashboard") or '
                    '(http.request.uri.path contains "/wp-login.php") or '
                    '(http.request.uri.path eq "/administrator") or '
                    '(http.request.uri.path contains "/index.php/admin/") or '
                    '(http.request.uri.path contains "/wp-admin/") or '
                    '(http.request.uri.path wildcard r"/rest/*") or '
                    '(http.request.uri.path contains "/checkout") or '
                    '(http.request.uri.path contains "/xmlrpc.php")'
                ),
                "ratelimit": {
                    "characteristics": ["ip.src", "cf.colo.id"],
                    "mitigation_timeout": 10,
                    "period": 10,
                    "requests_per_period": 20
                }
            }
        ]
    }

    print(f"\nAttempting to SET (overwrite) rate limiting rules for zone {zone_id}...")
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()

        print("\n--- SUCCESS! ---")
        print("Rate limiting ruleset was successfully deployed.")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
        return True

    except requests.exceptions.HTTPError as errh:
        print(f"\nHttp Error while deploying ruleset: {errh}", file=sys.stderr)
        print(f"Status Code: {errh.response.status_code}", file=sys.stderr)
        try:
            print(f"Response body: {json.dumps(errh.response.json(), indent=4)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Response body: {errh.response.text}", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as err:
        print(f"\nSomething else went wrong: {err}", file=sys.stderr)
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

    #Deploy the ruleset
    if not deploy_rate_limit_ruleset(zone_id, headers):
        print("\nScript failed.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()