import requests

# We will use the Staging (Pre-Prod) environment for testing [cite: 2]
AUTH_URL = "https://api-staging.cgifederal-aim.com/v1/auth/token"

# Paste your keys here for this local test
CLIENT_ID = "f21ewDFJ5HmDCdb9TIAAStRZJBWuHidjXWVDQhHL6jDBsaud"
CLIENT_SECRET = "KUEAzkI0cJcbIPIaG7Md8XSJzXVVl4IEfsCqrdcwcyxdUM6UbSKvXKhGNPDfLrEE"

def test_authentication():
    print("Requesting Bearer token from FAA...")
    
    payload = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(
            AUTH_URL, 
            data=payload, 
            auth=(CLIENT_ID, CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # This will trigger an exception if the FAA rejects our keys
        response.raise_for_status() 
        
        token_data = response.json()
        
        # The token is valid for 30 minutes (1799 seconds) [cite: 60, 63, 71]
        print("\nSuccess! Here is your temporary Bearer Token:")
        print(f"{token_data.get('access_token')[:40]}... (truncated for screen)")
        print(f"\nThis token expires in: {token_data.get('expires_in')} seconds.")
        
    except requests.exceptions.RequestException as e:
        print(f"\nAuthentication failed: {e}")
        # If it fails, this will print the exact reason the FAA rejected it
        if 'response' in locals() and response is not None:
            print(f"FAA Error Details: {response.text}")

if __name__ == "__main__":
    test_authentication()