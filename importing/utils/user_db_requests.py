import httpx

async def user_db_request(data, upload_id, user_token, method='patch'):
    base_url = "http://localhost:8080/api/users/uploads"
    url = f"{base_url}/{upload_id}" if method == 'patch' else f"{base_url}/create"
    
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if method == 'patch':
                response = await client.patch(url, headers=headers, json=data)
            else:
                response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            print(f"Error during HTTP {method.upper()} request: {e}")
            return {"error": f"Failed to {method} data", "details": str(e)}
