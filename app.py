import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import json
import re

# --- Streamlit UI Configuration ---

# --- Constants & Credentials ---
ROBOT_ID = "ef597c3b-e228-4444-952d-6de2a65681c7"
API_KEY = "11a6fede-63f1-4708-9708-839af383cbb9:c6250626-cd55-4f9f-984d-fa0c959ca892"
BASE_URL = f"https://api.browse.ai/v2/robots/{ROBOT_ID}/tasks"

def latex_to_plain(text):
    """Converts LaTeX-style math strings into plain text."""
    # 1. Replace common mathematical symbols
    replacements = {
        r"\in": "in",
        r"\mathbb{N}": "N",
        r"\mathbb{Z}": "Z",
        r"\mathbb{R}": "R",
        r"\mid": "divides",
        r"\small": "",
        r"\\": " ",
        r"\quad": " ",
    }
    
    clean_text = text
    for lat, pla in replacements.items():
        clean_text = clean_text.replace(lat, pla)
    
    # 2. Remove LaTeX commands like \text{...} but keep the content inside the { }
    clean_text = re.sub(r'\\text\{([^}]*)\}', r'\1', clean_text)
    
    # 3. Remove dollar signs $
    clean_text = clean_text.replace("$", "")
    
    # 4. Remove any remaining curly braces
    clean_text = clean_text.replace("{", "").replace("}", "")
    
    # 5. Clean up extra whitespace
    clean_text = re.sub(' +', ' ', clean_text)
    
    return clean_text.strip()

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

        # 6. Second API Call: Get specific task details
        detail_url = f"{BASE_URL}/{last_task_id}"
        detail_response = requests.get(detail_url, headers=headers)
        detail_response.raise_for_status()

        return detail_response.json()

    except Exception as e:
        st.error(f"Error making the request: {e}")
        return None

result = fetch_robot_data()
clue=result['result']["capturedTexts"]["clue"]
dl=clue.split("()big()")[2].split("{\small")[0].replace("(dlnewline)","\n")
st.link_button("🎮 Play Logic", "https://dailyintegral.com/play/logic", use_container_width=True)
st.write("---")
st.latex(dl)
st.write("---")

copy_button_html = f"""
    <button id="copyBtn" style="
        width: 100%;
        height: 38px;
        background-color: #f0f2f6;
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        cursor: pointer;
        color: #31333F;
        font-family: sans-serif;
    ">📋 Copy Clue</button>

    <script>
    document.getElementById('copyBtn').onclick = function() {{
        const text = `{latex_to_plain(dl)}`;
        navigator.clipboard.writeText(text).then(function() {{
            const btn = document.getElementById('copyBtn');
            btn.innerText = '✅ Copied!';
            btn.style.backgroundColor = '#d4edda';
            setTimeout(() => {{
                btn.innerText = '📋 Copy Clue';
                btn.style.backgroundColor = '#f0f2f6';
            }}, 2000);
        }});
    }};
    </script>
    """
components.html(copy_button_html, height=45)

if st.button("Solve Problem with AI (without thinking)"):
    with st.spinner("Thinking... (Reasoning disabled)"):
        try:
            # Your specific OpenRouter request logic
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer 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",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "google/gemma-4-26b-a4b-it:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": dl+"Solve the above mathematics problem and show all steps, at the end, add a statement 'Therefore, the answer is ...': "
                        }
                    ],
                    "reasoning": {"enabled": False}
                })
            )
            
            # Parsing the response
            response_json = response.json()
            
            # Check for errors in response
            if 'choices' in response_json:
                answer = response_json['choices'][0]['message']['content']
                st.subheader("AI Solution (thinking disabled):")
                st.markdown(answer)
            else:
                st.error("Error from API: " + str(response_json))
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

if st.button("Solve Problem with AI (with thinking)"):
    with st.spinner("Thinking... (Reasoning enabled)"):
        try:
            # Your specific OpenRouter request logic
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer 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",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "google/gemma-4-26b-a4b-it:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": dl+"Solve the above mathematics problem and show all steps, at the end, add a statement 'Therefore, the answer is ...': "
                        }
                    ],
                    "reasoning": {"enabled": True}
                })
            )
            
            # Parsing the response
            response_json = response.json()
            
            # Check for errors in response
            if 'choices' in response_json:
                answer = response_json['choices'][0]['message']['content']
                st.subheader("AI Solution (thinking enabled):")
                st.markdown(answer)
            else:
                st.error("Error from API: " + str(response_json))
                
        except Exception as e:
            st.error(f"An error occurred: {e}")

