from openrouter import OpenRouter
import json

def getModels(client):
    return client.models.list().data


def sortModelsByPrice(models):
    return sorted(models, key=lambda x: float(x.pricing.completion))


def getModelIds(models):
    ids = []
    for model in models:
        ids.append(model.id)
    return ids

def updateConfig(configFile,config):
    with open(configFile, "w", encoding="utf-8") as f:
        f.write(json.dumps(config))
        f.close()

def readConfig(configFile):
    with open("./config.json", "r", encoding="utf-8") as f:
        return json.loads(f.read())
        f.close()

def select(modelid,availableModels,config):
    if modelid in getModelIds(availableModels):
        config["model"] = modelid
        print("model selected: " + modelid)
        updateConfig("./config.json",config)
    else:
     print("model not found !")
              

def send(text, chat, client, config):
    user_message = {"role": "user", "content": text}
    chat.append(user_message)
    try:
        response = client.chat.send(model=config["model"], messages=chat)
        chat.append(response.choices[0].message)
        return response.choices[0].message.content
    except BaseException as exc:
        return exc

