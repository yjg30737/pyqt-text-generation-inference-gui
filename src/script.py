def get_answer(client, question):
    try:
        text = ""
        for response in client.generate_stream(question, max_new_tokens=17, temperature=1.0):
            if not response.token.special:
                text += response.token.text
        return f'{text.strip()}'
    except Exception as e:
        raise Exception