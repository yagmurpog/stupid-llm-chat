from openrouter import OpenRouter
import os
import json
from pathlib import Path
from dumbasslib import *
from sys import platform


config = {
    "key": "",
    "model": "",
    "system_prompt": "You are an AI chatbot, speak in a calm tone like someone if they're messaging on an online platform, keep your answers short like a human. Don't use emojis and speak like a terminally online personality would.",
}


# have this ready as a fallback
configFile = "./config.json"

match platform:
    case "linux" | "darwin":
        configFile = str(Path.home()) + "/.config/dumbassllmchattingprogramconfig.json"
        pass
    case "win32":
        configFile = (
            str(Path.home())
            + "\\AppData\\Roaming\\dumbassllmchattingprogramconfig.json"
        )


if Path(configFile).exists():
    config = readConfig(configFile)
else:
    updateConfig(configFile, config)


client = OpenRouter(
    api_key=config["key"],
    server_url="https://ai.hackclub.com/proxy/v1",
)

messages = [
    {
        "role": "system",
        "content": config["system_prompt"],
    }
]

availableModels = getModels(client)


while True:
    inputText = "<Command> "

    inp = format(input(inputText))
    if inp:
        search = False
        inpSplit = inp.split()
        match inpSplit[0]:
            case "help":
                print("list, select, chat")
            case "list":
                if len(inpSplit) > 1:
                    search = True
                for model in sortModelsByPrice(availableModels):
                    if search:
                        if inpSplit[1] in model.id:
                            print(
                                model.id
                                + "  O $"
                                + str(float(model.pricing.completion) * 1000000)
                            )
                    else:
                        print(
                            model.id
                            + "  O $"
                            + str(float(model.pricing.completion) * 1000000)
                        )
            case "select":
                if len(inpSplit) > 1:
                    select(inpSplit[1], availableModels, config)
                else:
                    print("pass along a paramater please")

            case "api":
                if len(inpSplit) > 1:
                    config["key"] = inpSplit[1]
                    updateConfig(configFile, config)
                else:
                    print("pass along a paramater please")

            case "chat":
                if config["key"] == "":
                    print("please set an api key first with the api command")

                if config["model"] and config["key"] != "":
                    inputText = "<You> "
                    print("type /exit to exit chat mode")
                    while True:
                        inp2 = format(input(inputText))
                        if inp2 == "/exit":
                            break
                        print("<Chatbot>" + send(inp2, messages, client, config))
