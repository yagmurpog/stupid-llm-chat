from openrouter import OpenRouter
import os


config = {
    "key": os.getenv(""),
    "model": "",
    "system_prompt": "You are an AI chatbot, speak in a calm tone like someone if they're messaging on an online platform, keep your answers short like a human. Don't use emojis and speak like a terminally online personality would.",
}

client = OpenRouter(
    api_key=config["key"],
    server_url="https://ai.hackclub.com/proxy/v1",
)

previous_messages = [
    {
        "role": "system",
        "content": config["system_prompt"],
    }
]

modelSelection = False
selectedModel = ""
availableModels = []


def getModels(client):
    return client.models.list().data


availableModels = getModels(client)


def sortModelsByPrice(models):
    return sorted(availableModels, key=lambda x: float(x.pricing.completion))


def getModelIds(models):
    ids = []
    for model in models:
        ids.append(model.id)
    return ids


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
                    if inpSplit[1] in getModelIds(availableModels):
                        config["model"] = inpSplit[1]
                        print("model selected: " + inpSplit[1])
                    else:
                        print("model not found !")
                else:
                    print("pass along a paramater please")

            case "chat":
                if config["model"]:
                    inputText = "<You> "
                    print("type /exit to exit chat mode")
                    while True:
                        inp2 = format(input(inputText))
                        if inp2 == "/exit":
                            break
                        user_message = {"role": "user", "content": inp2}
                        previous_messages.append(user_message)

                        modeltouse = str(config["model"])
                        try:
                            response_template = client.chat.send(
                                model=config["model"], messages=previous_messages
                            )
                            previous_messages.append(
                                response_template.choices[0].message
                            )
                            print(
                                "<Chatbot> "
                                + response_template.choices[0].message.content
                            )
                        except BaseException as exc:
                            print(exc)
