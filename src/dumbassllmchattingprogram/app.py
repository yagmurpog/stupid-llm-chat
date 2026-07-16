import os
import json
import requests
from pathlib import Path
from sys import platform


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


def send(text, chat, model, endpoint, headers):
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
        case "linux" | "darwin":
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
    print("saved chat as " + chatFile)
    with open(chatFile, "w", encoding="utf-8") as f:
        f.write(json.dumps(chat))
        f.close()


def createChatName(chatsPath):
    id = 0
    while "chat_" + str(id) + ".json" in os.listdir(chatsPath):
        id += 1
    return "chat_" + str(id)


def listModels(availableModels, searchQuery=""):
    for model in sortModelsByPrice(availableModels):
        if searchQuery in model["id"]:
            print(
                model["id"]
                + "  O $"
                + str(round(float(model["pricing"]["completion"]) * 1000000, 2))
            )


def setEndpoint(config, endpoint):
    config["endpoint"] = endpoint
    match endpoint:
        case "hack":
            config["endpoint"] = "https://ai.hackclub.com/proxy/v1/"
        case "openrouter":
            config["endpoint"] = "https://openrouter.ai/api/v1/"
    updateConfig(configFile, config)


def chat(config, messages, parameter=""):
    chatName = createChatName(config["chats_folder"])
    print("chatting with " + config["model"])

    if parameter != "":
        chatName = parameter
        try:
            messages = loadChat(parameter)
            print("loaded chat: " + parameter)
        except Exception:
            print("new chat created: " + chatName)
    else:
        print("new chat created: " + chatName)

    print("type /exit to exit chat mode")
    try:
        headers2 = {
            "Authorization": "Bearer " + config["key"],
            "Content-Type": "application/json",
        }

        while True:
            inp2 = format(input("<You> "))
            if inp2 == "/exit":
                saveChat(messages, chatName)
                break
            print(
                "<Chatbot> "
                + send(
                    inp2,
                    messages,
                    config["model"],
                    config["endpoint"],
                    headers2,
                )
            )
    except KeyboardInterrupt:
        print("ok exiting")
        saveChat(messages, chatName)


def main():
    # default config
    config = {
        "key": "",
        "model": "",
        "system_prompt": "You are an AI chatbot, speak in a calm tone like someone if they're messaging on an online platform, keep your answers short like a human. Don't use emojis and speak like a terminally online personality would.",
        "chats_folder": getChatsFolder(),
        "endpoint": "https://ai.hackclub.com/proxy/v1/",
    }

    # have this ready as a fallback
    configFile = "./config.json"

    configFile = getConfigFile()

    # check if config and chats folder exists
    # if not create them
    if not Path(config["chats_folder"]).exists():
        os.makedirs(config["chats_folder"])
    if Path(configFile).exists():
        config = readConfig(configFile)
    else:
        updateConfig(configFile, config)

    messages = [
        {
            "role": "system",
            "content": config["system_prompt"],
        }
    ]

    availableModels = getModels(config["endpoint"])

    print("my dumbass llm (cli?) chatting program")

    if config["key"] == "":
        print("set an api key with the key command to start chatting")

    try:
        while True:
            inputText = "<Command> "

            inp = format(input(inputText))

            if inp:
                search = False
                inpSplit = inp.split()
                hasArgument = len(inpSplit) > 1
                match inpSplit[0]:
                    case "help":
                        help = """
                            help :      yeah
                            list :      lists availaible models, add a parameter to search (anthropic, :free, openai) 
                            select :    selects a model
                            chat :      create or select a chat with a parameter
                            key :       set your api key
                            endpoint :  change the end point (don't forget to add a / at the end!)
                            lc :        lists chats
                        """
                        print(help)
                    case "list":
                        if len(inpSplit) > 1:
                            listModels(availableModels, inpSplit[1])
                        else:
                            listModels(availableModels)
                    case "select":
                        if hasArgument:
                            select(inpSplit[1], availableModels, config, configFile)
                        else:
                            print("pass along a paramater please")
                    case "key":
                        if hasArgument:
                            config["key"] = inpSplit[1]
                            updateConfig(configFile, config)
                        else:
                            print("pass along a paramater please")
                    case "endpoint":
                        if hasArgument:
                            setEndpoint(config, inpSplit[1])
                            print("endpoint set : " + config["endpoint"])
                        else:
                            print("pass along a paramater please")

                    case "chat":

                        if config["key"] == "":
                            print("please set an api key first with the key command")

                        if config["model"] == "":
                            print("please select an model first")

                        if config["model"] != "" and config["key"] != "":
                            if hasArgument:
                                chat(config, messages, inpSplit[1])
                            else:
                                chat(config, messages)
                    case "lc":
                        print(os.listdir(config["chats_folder"]))
                    case _:
                        print("command not found")

    except KeyboardInterrupt:
        print("buh bye!!")


if __name__ == "__main__":
    main()
