import requests


def send_message(chat_id, text):
    token = "7230321353:AAFJkYp1QvtN77f737ffvuLzdud199oAtxU"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.get(url, params=params)
    return response.json()


if __name__ == "__main__":
    chat_id = 5867217420
    message = "Hello! This is a test message."
    result = send_message(chat_id, message)
    if result["ok"]:
        print("Message sent successfully!")
    else:
        print("Failed to send message.")
