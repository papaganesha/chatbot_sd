from neuralintents import GenericAssistant
import time
import random


## RESPONDER SAUDAÇAO DE ACORDO COM HORARIO DO DIA
def function_for_greetings(message, response):

    #print(f'MSG RECEBIDA: {message} -- TAG/IDENTIFICADOR: SAUDAÇÃO')
    actual_hour = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()).split()[1][0:2]
    actual_hour = int(actual_hour)
    if(actual_hour >= 0 and actual_hour <= 5):
        return_message = 'Boa Madrugada'
    elif(actual_hour >= 6 and actual_hour <  12):
        return_message = 'Bom Dia'
    elif(actual_hour >= 12 and actual_hour < 18):
        return_message = 'Boa Tarde'
    elif(actual_hour >= 18 and actual_hour <= 23):
        return_message = 'Boa Noite'
    else:
        return response
    return return_message


def initialize_and_return_trained_model():
    # mappings = {'saudacoes': function_for_greetings} //intent_methods=mappings,
    mappings = {'saudacoes': function_for_greetings}

    assistant = GenericAssistant('intents.json', intent_methods=mappings, model_name="pyChatBot")
    assistant.train_model()
    assistant.save_model()
    return assistant



assistant = initialize_and_return_trained_model()

