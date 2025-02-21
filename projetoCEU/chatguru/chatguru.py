import requests


try:
    from local_settings import CHATG_KEY, CHATG_ACCOUNT_ID, CHATG_PHONE_ID, CHATG_BASE_URL
except ImportError:
    ...


# O NUMERO DEVE SER PASSADO COM O CODIGO DO PAIS + DDD + NUMERO
# EX: 5511999999999
class Chatguru:
    def __init__(self, ):
        self.key = CHATG_KEY
        self.account_id = CHATG_ACCOUNT_ID
        self.phone_id = CHATG_PHONE_ID
        self.base_url = f"{CHATG_BASE_URL}?key={self.key}&account_id={self.account_id}&phone_id={self.phone_id}"

    def send_message(self, number, message):
        url = f"{self.base_url}&action=message_send&chat_number={number}&text={message}"
        response = requests.post(url)
        return response.json() 
    
    def send_file(self, number, file_name, file_url):
        url = f"{self.base_url}&action=message_file_send&chat_number={number}&caption={file_name}&file_url={file_url}"
        response = requests.post(url)
        return response.json()

    #OBS: VC PODE MANDAR MSG DIRETO NESSA REQUISIÇÂO 
    #OBS2: SE O CHAT FOR VAZIO (" ") ELE CRIA UM NOVO CHAT MAS NÃO ENVIA NADA PARA O CLIENTE.
    def add_chat(self, number, name, message=" ", user_id=None, dialog_id=None):
        url = f"{self.base_url}&action=chat_add&chat_number={number}&name={name}&text={message}"
        if user_id:
            url += f"&user_id={user_id}"
        if dialog_id:
            url += f"&dialog_id={dialog_id}"
        response = requests.post(url)
        return response.json()

    #AUTOMAÇÔES INTERNAS FEITAS PELO CHATGURU
    def exec_dialog(self, number, dialog_id):
        url = f"{self.base_url}&action=dialog_execute&chat_number={number}&dialog_id={dialog_id}"
        response = requests.post(url)
        return response.json()
    
    #INFORME O CONTEXTO SENDO UM ARRAY DE OBJETOS COM OS CAMPOS "id" E "value"
    # EX: [{"id": "pagamento", "value": "concluido"}]
    # O id do contexto é pego no CHATGURU
    def context(self, number, context):
        url = f"{self.base_url}&action=chat_update_context&chat_number={number}"
        for item in context:
            url += f"&var__{item['id']}={item['value']}"
        response = requests.post(url)
        return response.json()
    
    #INFORME O CAMPO SENDO UM ARRAY DE OBJETOS COM OS CAMPOS "id" E "value"
    # EX: [{"id": "email", "value": fool@fool.com}]
    # O id do campo é pego no CHATGURU
    def edit_field(self, number, field):
        url = f"{self.base_url}&action=chat_update_custom_fields&chat_number={number}"
        for item in field:
            url += f"&field__{item['id']}={item['value']}"
        response = requests.post(url)
        return response.json()