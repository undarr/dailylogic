import streamlit as st
import requests
import time
import json

# --- Streamlit UI Configuration ---
st.title("Daily Logic Replay")

# --- Constants & Credentials ---
ROBOT_ID = "ef597c3b-e228-4444-952d-6de2a65681c7"
API_KEY = "11a6fede-63f1-4708-9708-839af383cbb9:c6250626-cd55-4f9f-984d-fa0c959ca892"
BASE_URL = f"https://api.browse.ai/v2/robots/{ROBOT_ID}/tasks"

def fetch_robot_data():
    # 1. Logic for Start of Today (Replicating your JS math)
    # Note: eighttotwelve is assumed to be 0 or a millisecond offset
    eighttotwelve = 0 
    ms_in_day = 24 * 60 * 60 * 1000
    
    tdy = int(time.time() * 1000)
    start_of_today_ms = (int((tdy - eighttotwelve) / ms_in_day) * ms_in_day) + eighttotwelve
    from_date_unix = int(start_of_today_ms / 1000)

    # 2. Setup Headers and Params
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    params = {
        "page": 1, 
        "fromDate": from_date_unix
    }

    try:
        # 3. First API Call: Get list of tasks
        st.info(f"Fetching tasks from timestamp: {from_date_unix}...")
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status() # Check for HTTP errors
        
        data = response.json()
        all_items = data.get("result", {}).get("robotTasks", {}).get("items", [])

        # 4. Filter for successful tasks
        successful_items = [item for item in all_items if item.get("status") == "successful"]

        if not successful_items:
            st.warning("No successful tasks found for today.")
            return

        # 5. Get the ID of the last successful task
        last_task_id = successful_items[-1]["id"]
        st.success(f"Found successful task ID: {last_task_id}")

        # 6. Second API Call: Get specific task details
        detail_url = f"{BASE_URL}/{last_task_id}"
        detail_response = requests.get(detail_url, headers=headers)
        detail_response.raise_for_status()

        return detail_response.json()

    except Exception as e:
        st.error(f"Error making the request: {e}")
        return None

result = fetch_robot_data()
st.json(result)

