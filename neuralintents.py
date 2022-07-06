from abc import ABCMeta, abstractmethod

import random
import json
import pickle
import numpy as np
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.models import load_model

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)



class IAssistant(metaclass=ABCMeta):

    @abstractmethod
    def train_model(self):
        """ Implemented in child class """

    @abstractmethod
    def request_tag(self, message):
        """ Implemented in child class """

    @abstractmethod
    def get_tag_by_id(self, id):
        """ Implemented in child class """

    @abstractmethod
    def request_method(self, message):
        """ Implemented in child class """

    @abstractmethod
    def request(self, message):
        """ Implemented in child class """


class GenericAssistant(IAssistant):
    ## REQUER AS INTENCOES, OS METODOS PARA INTENCOES(IDENTIFICADORES), NOME DO MODELO
    def __init__(self, intents, intent_methods={}, model_name="assistant_model"):
        # SETANDO OS VALORES RECEBIDOS
        self.intents = intents
        self.intent_methods = intent_methods
        self.model_name = model_name

        ## VERIFICA SE O ARQUIVO INTENTS TERMINA EM .JSON E O ABRE CASO SIM
        if intents.endswith(".json"):
            self.load_json_intents(intents)

        ## INICIA O LEMMATIZER
        # JUNTAR PALAVRAS SEMELHANTES
        self.lemmatizer = WordNetLemmatizer()

    ## ABRE O ARQUIVO JSON NA VARIAVEL DO MESMO
    def load_json_intents(self, intents):
        self.intents = json.loads(open(intents).read(ensure_ascii=False))

    ## ABRE O ARQUIVO CSV NA VARIAVEL DO MESMO
    ## ABRE O ARQUIVO JSON NA VARIAVEL DO MESMO
    def load_json_intents(self, intents):
        self.intents = json.loads(open(intents).read())
    ## TREINAR MODELO
    def train_model(self):
        self.words = []
        self.classes = []
        # CLASSES/TAGS: IDENTIFICADOR DE INTENÇOES
        documents = []
        ## LETRAS A SEREM IGNORADAS
        ignore_letters = ['!', '?', ',', '.']

        ## ITERA PARA CADA UMA DAS INTENCOES
        for intent in self.intents['intents']:
            ## PARA CADA PADRAO(PALAVRA DE PERGUNTA) EM CADA INTENCAO
            for pattern in intent['patterns']:
                # QUEBRA A FRASE EM PALAVRAS
                word = nltk.word_tokenize(pattern)
                # INSERE WORD NO ARRAY WORDS
                self.words.extend(word)
                # INSERE A WORD EM DOCUMENTS PARA IDENTIFICAR QUE A WORD TEM CERTA TAG/IDENTIFICADOR
                documents.append((word, intent['tag']))
                # VERIFICA SE TAG/IDENTIFICADOR ESTA OU NAO CADASTRADO EM CLASSES E O CADASTRA
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

        ## SETA WORDS COMO SENDO APENAS PALAVRAS SEMELHANTES PARA CADA UMA DAS PALAVRAS IN SELF.WORDS TIRANDO AS LETRAS IGNORADAS
        self.words = [self.lemmatizer.lemmatize(w.lower()) for w in self.words if w not in ignore_letters]
        ## SORTEIA E RETIRA DUPLICATAS
        self.words = sorted(list(set(self.words)))
        ## SORTEIA E RETIRA DUPLICATAS
        self.classes = sorted(list(set(self.classes)))



        ## INICIANDO O TREINAMENTO DE DADOS
        training = []
        output_empty = [0] * len(self.classes)

        for doc in documents:
            # INICIA A BOLSA DE PALAVRAS
            bag = []
            # LISTA AS PALAVRAS TOKENIZADAS PARA O PADRAO
            word_patterns = doc[0]
            ## LEMATIZA CADA PALAVRA -- CRIA PALAVRA BASE, TENTATIVA DE REPRESENTAR PALAVRAS RELACIONADAS
            word_patterns = [self.lemmatizer.lemmatize(word.lower()) for word in word_patterns]
            ## CRIA A BOLSA DE PALAVRAS COM 1, CASO ACHE A PALAVRA NO PADRAO ATUAL
            for word in self.words:
                bag.append(1) if word in word_patterns else bag.append(0)

            # OUTPUT É 0 PARA CADA TAG E 1 PARA A TAG ATUAL(PARA CADA PADRAO)
            output_row = list(output_empty)
            output_row[self.classes.index(doc[1])] = 1
            training.append([bag, output_row])

        ## MISTURA AS FUNCIONALIDADES E AS INSERE NO NP.ARRAY
        random.shuffle(training)
        training = np.array(training, dtype=object)

        ## CRIA LISTAS DE TREINO E TESTE
        train_x = list(training[:, 0])
        train_y = list(training[:, 1])
        print("Data de treino criada")

        # CRIA O MODELO
        # 3 CAMADAS - 1C: COM 128 NEURONS, 2C: COM 64 NEUROS, 3C: OUTPUT LAYER, NUMERO DE NEURONS AO NUMERO DE INTENCOES DE SAIDA
        self.model = Sequential()
        self.model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(len(train_y[0]), activation='softmax'))

        # COMPILAR O MODELO, GRADIENTE ESTOCASTICO COM GRADIENTE ACELERADO DE NESTEROV, BONS RESULTADOS PARA ESTE MODELO
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
        self.model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

        ## FAZENDO O FIT DO MODELO
        self.hist = self.model.fit(np.array(train_x), np.array(train_y), epochs=100, batch_size=5, verbose=1)

    ## SALVANDO O MODELO
    def save_model(self, model_name=None):
        if model_name is None:
            self.model.save(f"{self.model_name}.h5", self.hist)
            pickle.dump(self.words, open(f'{self.model_name}_words.pkl', 'wb'))
            pickle.dump(self.classes, open(f'{self.model_name}_classes.pkl', 'wb'))
        else:
            self.model.save(f"{model_name}.h5", self.hist)
            pickle.dump(self.words, open(f'{model_name}_words.pkl', 'wb'))
            pickle.dump(self.classes, open(f'{model_name}_classes.pkl', 'wb'))

    ## CARREGANDO O MODELO
    def load_model(self, model_name=None):
        if model_name is None:
            self.words = pickle.load(open(f'{self.model_name}_words.pkl', 'rb'))
            self.classes = pickle.load(open(f'{self.model_name}_classes.pkl', 'rb'))
            self.model = load_model(f'{self.model_name}.h5')
        else:
            self.words = pickle.load(open(f'{model_name}_words.pkl', 'rb'))
            self.classes = pickle.load(open(f'{model_name}_classes.pkl', 'rb'))
            self.model = load_model(f'{model_name}.h5')


    ## LIMPANDO AS SENTENCAS
    def _clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    ## RETORNA BOLSA DE PALAVRA, SENDO 0 OU 1 PARA CADA PALAVRA QUE ECISTE NA SENTENCA
    def _bag_of_words(self, sentence, words):
        # TOKENIZA O PADRAO
        sentence_words = self._clean_up_sentence(sentence)
        # BOLSA DE PALAVRAS - MATRIZ DE N PALAVRAS
        bag = [0] * len(words)
        for s in sentence_words:
            for i, word in enumerate(words):
                if word == s:
                    ## DESIGNA 1 SE A PALAVRA ATUAL ESTA NA POSICAO DO VOCABULARIO
                    bag[i] = 1
        return np.array(bag)

    def _predict_class(self, sentence):
        # FILTRA PREDICOES ABAIXO DO TRESHHOLD
        p = self._bag_of_words(sentence, self.words)
        res = self.model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.1
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        ## SORTEIA POR FORÇA DE PROBABILIDADE
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

    def _get_response(self, ints, intents_json):
        try:
            tag = ints[0]['intent']
            list_of_intents = intents_json['intents']
            for i in list_of_intents:
                if i['tag']  == tag:
                    result = random.choice(i['responses'])
                    break
        except IndexError:
            result = "I don't understand!"
        return result


    def request_tag(self, message):
        pass

    def get_tag_by_id(self, id):
        pass

    def request_method(self, message):
        pass

    def request(self, message):
        ints = self._predict_class(message)
        #print("Mensagem recebida: ",message)
        #print('Classificação: ',ints[0]['intent'])
        response = self._get_response(ints, self.intents)
        if ints[0]['intent'] in self.intent_methods.keys():
            returnMessage = self.intent_methods[ints[0]['intent']](message, response)
            if returnMessage != "" or returnMessage != None:
                return returnMessage
        else:
            return response

