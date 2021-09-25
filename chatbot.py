def dialog_flow(message, token):
    from apiai import ApiAI
    import json
    request = ApiAI(token).text_request()
    request.lang = 'ru'
    request.session_id = 'barmen-gxppsm'
    request.query = message
    response = json.loads(request.getresponse().read().decode('utf-8'))
    request = None
    if 'result' in response:
        response = response['result']['fulfillment']['speech']
        if response:
            return response
    else:
        return None


if __name__ == '__main__':
    import json
    while True:
        msg = input()
        with open('params.json') as init_file:
            bot_params = json.loads(init_file.read())
            chatbot_token = bot_params["chatbot_token"]
        dialog_flow(msg, chatbot_token)
