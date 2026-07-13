import requests
import json

def getModels(endpoint):
    response = requests.get(endpoint + "models")
    if response.status_code == 200:
        return json.loads(response.text)["data"]


def sortModelsByPrice(models):
    return sorted(models, key=lambda x: float(x["pricing"]["completion"]))


def getModelIds(models):
    ids = []
    for model in models:
        ids.append(model["id"])
    return ids


def send(text, chat,endpoint,headers):
    user_message = {"role": "user", "content": text}
    chat.append(user_message)
    try:
        payload = {
            "model": "tencent/hy3:free",
            "messages": chat,
        }

        response = requests.post(
            url=endpoint + "chat/completions",
            headers=headers,
            data=json.dumps(payload),
        )

        if response.status_code == 200:
            jsonifiedResponse = json.loads(response.text)
            assistantMessage = jsonifiedResponse["choices"][0]["message"]

        chat.append(assistantMessage)
        return str(assistantMessage["content"])
    except BaseException as exc:
        return exc
