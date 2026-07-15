from sys import platform
from pathlib import Path
import json
import os
from myowndumbasswrapperforopenrouternbecauseitdoesntworkonwindowsforsomereason import *


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
                + "\\AppData\\Roaming\\dumbassllmchattingprogram\\dumbassllmchattingprogramconfig.json"
            )


def loadChat(chatName):
    chatFile = getChatsFolder() + chatName + ".json"
    if Path(getChatsFolder() + chatName + ".json").exists():
        with open(chatFile, "r", encoding="utf-8") as f:
            return json.loads(f.read())
    else:
        raise Exception("chat doesn't exist!")
    


def saveChat(chat, chatName):
    chatFile = getChatsFolder() + chatName + ".json"
    with open(chatFile, "w", encoding="utf-8") as f:
        f.write(json.dumps(chat))
        f.close()


def createChatName(chatsPath):
    id = 0
    while "chat_" + str(id) + ".json" in os.listdir(chatsPath):
        id += 1
    return "chat_" + str(id)
