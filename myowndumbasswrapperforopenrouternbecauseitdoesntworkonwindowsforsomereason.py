import requests
import json

def getModels(endpoint):
    try:
        response = requests.get(endpoint + "models")
        if response.status_code == 200:
            return json.loads(response.text)["data"]
    except BaseException as exc:
        print(exc)

def sortModelsByPrice(models):
    return sorted(models, key=lambda x: float(x["pricing"]["completion"]))


def getModelIds(models):
    ids = []
    for model in models:
        ids.append(model["id"])
    return ids


def send(text, chat,model, endpoint,headers):
    user_message = {"role": "user", "content": text}
    chat.append(user_message)
    try:
        payload = {
            "model": model,
            "messages": chat,
        }

        response = requests.post(
            url=endpoint + "chat/completions",
            headers=headers,
            data=json.dumps(payload),
        )
        match response.status_code:
            case 200:
                jsonifiedResponse = json.loads(response.text)
                assistantMessage = jsonifiedResponse["choices"][0]["message"]

                chat.append(assistantMessage)
                return str(assistantMessage["content"])
            case 401:
                print("authentication failed, is api key valid?")
            case 404:
                print("not found, is endpoint valid? (and make sure it ends with a /)")
            case _:
                return response.text
    except BaseException as exc:
        return exc
