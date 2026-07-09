from openrouter import OpenRouter
from sys import platform
from pathlib import Path
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


def updateConfig(configFile, config):
    with open(configFile, "w", encoding="utf-8") as f:
        f.write(json.dumps(config))
        f.close()


def readConfig(configFile):
    with open(configFile, "r", encoding="utf-8") as f:
        return json.loads(f.read())
        f.close()


def select(modelid, availableModels, config, configFile):
    if modelid in getModelIds(availableModels):
        config["model"] = modelid
        print("model selected: " + modelid)
        updateConfig(configFile, config)
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


def getChatsFolder():
    match platform:
        case "linux":
            return str(Path.home()) + "/.local/share/dumbassllmchattingprogram/chats/"

        case "win32":
            return (
                str(Path.home())
                + "\\AppData\\Roaming\\dumbassllmchattingprogram\\chats\\"
            )


def getConfigFile():
    match platform:
        case "linux" | "darwin":
            return str(Path.home()) + "/.config/dumbassllmchattingprogramconfig.json"

        case "win32":
            return (
                str(Path.home())
                + "\\AppData\\Roaming\\dumbassllmchattingprogramconfig.json"
            )


def loadChat(chatName):
    chatFile = getChatsFolder() + chatName + ".json"
    if Path(getChatsFolder() + chatName + ".json").exists():
        with open(chatFile, "r", encoding="utf-8") as f:
            return json.loads(f.read())


def saveChat(chat, chatName):
    chatFile = getChatsFolder() + chatName + ".json"
    with open(chatFile, "w", encoding="utf-8") as f:
        f.write("[")
        for i,entry in enumerate(chat):
            if isinstance(entry, dict):
                f.write(json.dumps(entry) + ",\n")
            else:
                f.write(
                    json.dumps(
                        {
                            "role": "assistant",
                            "content": entry.content,
                        }
                    ) 
                )
                if i != len(chat) -1 :
                    f.write(",")
        f.write("]")
        f.close()


def createChatName():
    return "dumdum"
    