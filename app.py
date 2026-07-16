import os
import json
from pathlib import Path
from dumbasslib import *
from sys import platform
from myowndumbasswrapperforopenrouternbecauseitdoesntworkonwindowsforsomereason import *


def listModels(availableModels,searchQuery=""):
    for model in sortModelsByPrice(availableModels):
        if searchQuery in model["id"]:
            print(
                model["id"]
                + "  O $"
                + str(
                    round(float(model["pricing"]["completion"]) * 1000000,2)
                )
            )



def setEndpoint(config, endpoint):
    config["endpoint"] = endpoint
    match endpoint:
        case "hack":
            config["endpoint"] = "https://ai.hackclub.com/proxy/v1/"
        case "openrouter":
            config["endpoint"] = "https://openrouter.ai/api/v1/"
    updateConfig(configFile, config)


def chat(config,messages,parameter=""):
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



if __name__ == '__main__':
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
    if Path(configFile).exists():
        config = readConfig(configFile)
        if not Path(config["chats_folder"]).exists():
            os.makedirs(config["chats_folder"])
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
                        if len (inpSplit) > 1:
                            listModels(availableModels,inpSplit[1])
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
                            setEndpoint(config,inpSplit[1])
                            print("endpoint set : "+ config["endpoint"]) 
                        else:
                            print("pass along a paramater please")

                    case "chat":

                        if config["key"] == "":
                            print("please set an api key first with the api command")

                        if config["model"] == "":
                            print("please select an model first")

                        if config["model"] != "" and config["key"] != "":
                            if hasArgument:
                                chat(config,messages,inpSplit[1])
                            else:
                                chat(config,messages)
                    case "lc":
                        print(os.listdir(config["chats_folder"]))
                    case _:
                        print("command not found")

    except KeyboardInterrupt:
        print("buh bye!!")


