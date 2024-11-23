from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from peraltas.models import ClienteColegio, FichaDeEvento, ProdutosPeraltas


class Cozinheiro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)

    @property
    def nome_completo(self):
        return self.usuario.get_full_name()

    @property
    def funcao(self):
        return ', '.join([
            grupo.__str__() for grupo in self.usuario.groups.all() if 'cozinha' in grupo.__str__() or 'Cozinheiro' in grupo.__str__()
        ])


class Relatorio(models.Model):
    ficha_de_evento = models.OneToOneField(FichaDeEvento, on_delete=models.CASCADE)
    grupo = models.ForeignKey(ClienteColegio, on_delete=models.CASCADE)
    tipo_evento = models.ForeignKey(ProdutosPeraltas, on_delete=models.PROTECT)
    pax_adulto = models.PositiveIntegerField(default=0)
    pax_crianca = models.PositiveIntegerField(default=0)
    pax_monitoria = models.PositiveIntegerField(default=0)
    total_pax = models.PositiveIntegerField(default=0, editable=False)
    dados_cafe_da_manha = models.JSONField(null=True, blank=True)
    dados_lanche_da_manha = models.JSONField(null=True, blank=True)
    dados_almoco = models.JSONField(null=True, blank=True)
    dados_lanche_da_tarde = models.JSONField(null=True, blank=True)
    dados_jantar = models.JSONField(null=True, blank=True)
    dados_lanche_da_noite = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'Dados refeições {self.grupo}'

    @staticmethod
    def dividir_refeicoes(dados_refeicoes):
        refeicoes= {}

        for refeicao_dia in dados_refeicoes.keys():
            if '-' in refeicao_dia:
                refeicao, dia = refeicao_dia.split('-')
                participantes = dados_refeicoes.getlist(refeicao_dia)

                if refeicao not in refeicoes:
                    refeicoes[refeicao] = []

                refeicoes[refeicao].append({
                    'dia': dia,
                    'hora': participantes[0],
                    'participantes': {
                        'adultos': participantes[1],
                        'criancas': participantes[2],
                        'monitoria': participantes[3],
                        'total': participantes[4],
                    }
                })

        return refeicoes

    def salvar_refeicoes(self, lista_refeicoes):
        refeicoes = lista_refeicoes.keys()

        if 'cafe_manha' in refeicoes:
            self.dados_cafe_da_manha = lista_refeicoes['cafe_manha']

        if 'lanche_manha' in refeicoes:
            self.dados_lanche_da_manha = lista_refeicoes['lanche_manha']

        if 'almoco' in refeicoes:
            self.dados_almoco = lista_refeicoes['almoco']

        if 'lanche_tarde' in refeicoes:
            self.dados_lanche_da_tarde = lista_refeicoes['lanche_tarde']

        if 'jantar' in refeicoes:
            self.dados_jantar = lista_refeicoes['jantar']

        if 'lanche_noite' in refeicoes:
            self.dados_lanche_da_noite = lista_refeicoes['lanche_noite']

    def save(self, *args, **kwargs):
        self.total_pax = self.pax_adulto + self.pax_crianca + self.pax_monitoria
        super().save(*args, **kwargs)

    def pegar_refeicoes_edicao(self):
        check_in = self.ficha_de_evento.check_in
        check_out = self.ficha_de_evento.check_out
        data_atual = check_in

        # Lista para armazenar as informações das refeições por dia
        refeicoes_por_dia = []

        while data_atual <= check_out:
            campos_refeicoes = [
                'dados_cafe_da_manha',
                'dados_lanche_da_manha',
                'dados_almoco',
                'dados_lanche_da_tarde',
                'dados_jantar',
                'dados_lanche_da_noite',
            ]

            # Inicializa o dicionário para o dia atual
            refeicoes_dia = {'data': data_atual}

            for campo in campos_refeicoes:
                dados_refeicao = getattr(self, campo, None)

                if dados_refeicao:
                    # Filtra as refeições pela data
                    for refeicao in dados_refeicao:
                        if refeicao['dia'] == data_atual.strftime('%Y_%m_%d'):
                            refeicoes_dia[campo] = {
                                'hora': refeicao['hora'],
                                'adultos': refeicao['participantes']['adultos'],
                                'criancas': refeicao['participantes']['criancas'],
                                'monitoria': refeicao['participantes']['monitoria'],
                                'total': refeicao['participantes']['total'],
                            }

            # Adiciona o dicionário do dia à lista de resultados
            refeicoes_por_dia.append(refeicoes_dia)

            # Incrementa para o próximo dia
            data_atual += timedelta(days=1)
        print(refeicoes_por_dia)
        return {
            'datas': refeicoes_por_dia,
            'adultos': self.ficha_de_evento.numero_adultos(),
            'criancas': self.ficha_de_evento.numero_criancas(),
        }

    def relatorio_refeicoes_dia(self, data):
        obj_nulo = {'hora': '', 'participantes': {'total': '0', 'adultos': '0', 'criancas': '0', 'monitoria': '0'}}
        cafe_manha = lanche_manha = almoco = lanche_tarde = jantar = lanche_noite = obj_nulo

        if self.dados_cafe_da_manha:
            for dia in self.dados_cafe_da_manha:
                if dia['dia'] == data.strftime('%Y_%m_%d'):
                    cafe_manha = dia

        if self.dados_lanche_da_manha:
            for dia in self.dados_lanche_da_manha:
                if dia['dia'] == data.strftime('%Y_%m_%d'):
                    lanche_manha = dia

        if self.dados_almoco:
            for dia in self.dados_almoco:
                if dia['dia'] == data.strftime('%Y_%m_%d'):
                    almoco = dia

        if self.dados_lanche_da_tarde:
            for dia in self.dados_lanche_da_tarde:
                if dia['dia'] == data.strftime('%Y_%m_%d'):
                    lanche_tarde = dia

        if self.dados_jantar:
            for dia in self.dados_jantar:
                if dia['dia'] == data.strftime('%Y_%m_%d'):
                    jantar = dia

        if self.dados_lanche_da_noite:
            for dia in self.dados_lanche_da_noite:
                if dia['dia'] == data.strftime('%Y_%m_%d'):
                    lanche_noite = dia

        return f"""
            <tr>
                <td rowspan="2" class="informacao_grupo">{ self.grupo }</td>
                <th>Hora</th>
                <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled value="{ cafe_manha['hora'] }" type="time">
                </td>
                <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo" name="lanhce_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled value="{ lanche_manha['hora'] }" type="time">                        
                </td>
                <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled value="{ almoco['hora'] }" type="time">                        
                </td>
                <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled value="{ lanche_tarde['hora'] }" type="time">                        
                </td>
                <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled value="{ jantar['hora'] }" type="time">                        
                </td>
                <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled value="{ lanche_noite['hora'] }" type="time">                        
                </td>
            </tr>
            <tr>
                <th>Adultos</th>
                <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo cafe_manha adultos" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ cafe_manha['participantes']['adultos'] }">
                </td>
                <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_manha adultos" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_manha['participantes']['adultos'] }">
                </td>
                <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo almoco adultos" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ almoco['participantes']['adultos'] }">
                </td>
                <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_tarde adultos" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_tarde['participantes']['adultos'] }">
                </td>
                <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo jantar adultos" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ jantar['participantes']['adultos'] }">
                </td>
                <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_noite adultos" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_noite['participantes']['adultos'] }">
                </td>
            </tr>
            <tr>
                <td class="informacao_grupo">{ self.tipo_evento }</td>
                <th>Crianças</th>
                <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo cafe_manha criancas" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ cafe_manha['participantes']['criancas'] }">
                </td>
                <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_manha criancas" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_manha['participantes']['criancas'] }">
                </td>
                <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo almoco criancas" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ almoco['participantes']['criancas'] }">
                </td>
                <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_tarde criancas" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_tarde['participantes']['criancas'] }">
                </td>
                <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo jantar criancas" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ jantar['participantes']['criancas'] }">
                </td>
                <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_noite criancas" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_noite['participantes']['criancas'] }">
                </td>
            </tr>
            <tr>
                <td class="informacao_grupo">{ self.ficha_de_evento.numero_adultos() } adultos</td>
                <th>Monitoria</th>
                <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo cafe_manha monitoria" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled type="number" onchange="atualizar_monitoria(this)" value="{ cafe_manha['participantes']['monitoria'] }">
                </td>
                <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_manha monitoria" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled type="number" onchange="atualizar_monitoria(this)" value="{ lanche_manha['participantes']['monitoria'] }">
                </td>
                <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo almoco monitoria" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled type="number" onchange="atualizar_monitoria(this)" value="{ almoco['participantes']['monitoria'] }">
                </td>
                <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_tarde monitoria" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled type="number" onchange="atualizar_monitoria(this)" value="{ lanche_tarde['participantes']['monitoria'] }">
                </td>
                <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo jantar monitoria" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled type="number" onchange="atualizar_monitoria(this)" value="{ jantar['participantes']['monitoria'] }">
                </td>
                <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_noite monitoria" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" disabled type="number" onchange="atualizar_monitoria(this)" value="{ lanche_noite['participantes']['monitoria'] }">
                </td>
            </tr>
            <tr class="ultima_linha">
                <td class="informacao_grupo">{ self.ficha_de_evento.numero_criancas() } crianças</td>
                <th>Total</th>
                <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo cafe_manha geral" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ cafe_manha['participantes']['total'] }">
                </td>
                <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_manha geral" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_manha['participantes']['total'] }">
                </td>
                <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo almoco geral" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ almoco['participantes']['total'] }">
                </td>
                <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_tarde geral" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_tarde['participantes']['total'] }">
                </td>
                <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo jantar geral" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ jantar['participantes']['total'] }">
                </td>
                <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                    <input class="grupo lanche_noite geral" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" disabled value="{ lanche_noite['participantes']['total'] }">
                </td>
            </tr>
        """


class RelatorioDia(models.Model):
    fichas_de_evento = models.ManyToManyField(FichaDeEvento)
    grupos = models.ManyToManyField(ClienteColegio)
    data = models.DateField(default=timezone.now)
    dados_cafe_da_manha = models.JSONField(null=True, blank=True)
    dados_lanche_da_manha = models.JSONField(null=True, blank=True)
    dados_almoco = models.JSONField(null=True, blank=True)
    dados_lanche_da_tarde = models.JSONField(null=True, blank=True)
    dados_jantar = models.JSONField(null=True, blank=True)
    dados_lanche_da_noite = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'Relatorio rfeicoes {self.data.strftime("%d/%m/%Y")}'

    class Meta:
        permissions = (('ver_descritivo_refeicoes', 'Ver descritivo as refeições'),)

    @staticmethod
    def processar_refeicoes(dados):
        refeicoes_map = {
            'cafe_manha': 'dados_cafe_da_manha',
            'lanche_manha': 'dados_lanche_da_manha',
            'almoco': 'dados_almoco',
            'lanche_tarde': 'dados_lanche_da_tarde',
            'jantar': 'dados_jantar',
            'lanche_noite': 'dados_lanche_da_noite',
        }
        lista_ids_eventos = set()
        lista_ids_grupos = set()
        dados_refeicoes = {campo: {'dados_grupos': [], 'totais': {'adultos': 0, 'criancas': 0, 'monitoria': 0, 'total': 0}} for campo in refeicoes_map.values()}

        for key, value in dados.lists():
            if key == 'csrfmiddlewaretoken':
                continue  # Ignora o token CSRF

            # Divide a chave no formato refeicao-data-id_ficha_de_evento
            try:
                _, _, ficha_id = key.split('-')
                lista_ids_eventos.add(int(ficha_id))
            except ValueError:
                continue

        fichas = FichaDeEvento.objects.filter(id__in=list(lista_ids_eventos)).values('id', 'cliente__id')
        fichas_dict = {str(ficha['id']): ficha['cliente__id'] for ficha in fichas}  # Mapeia ficha_id -> grupo_id

        # Processa cada item do QueryDict
        for key, value in dados.lists():
            if key == 'csrfmiddlewaretoken':
                continue

            # Divide a chave no formato refeicao-data-id_ficha_de_evento
            try:
                refeicao, _, ficha_id = key.split('-')
            except ValueError:
                continue  # Pula entradas com formato inesperado

            # Obtém o grupo_id correspondente
            grupo_id = fichas_dict.get(ficha_id)
            if not grupo_id:
                continue  # Ignora se a ficha não tem grupo associado

            # Garante que a refeição mapeia para um campo no modelo
            campo_modelo = refeicoes_map.get(refeicao)
            lista_ids_grupos.add(int(grupo_id))
            if not campo_modelo:
                continue

            participantes = {
                'adultos': int(value[1]),
                'criancas': int(value[2]),
                'monitoria': int(value[3]),
                'total': int(value[4]),
            }
            dados_refeicao = {
                'grupo_id': grupo_id,
                'hora': value[0],
                'participantes': participantes,
            }
            dados_refeicoes[campo_modelo]['dados_grupos'].append(dados_refeicao)

            # Atualiza os totais para a refeição
            dados_refeicoes[campo_modelo]['totais']['adultos'] += participantes['adultos']
            dados_refeicoes[campo_modelo]['totais']['criancas'] += participantes['criancas']
            dados_refeicoes[campo_modelo]['totais']['monitoria'] += participantes['monitoria']
            dados_refeicoes[campo_modelo]['totais']['total'] += participantes['total']

        return dados_refeicoes, list(lista_ids_eventos), list(lista_ids_grupos)

    def pegar_dados_refeicoes(self, id_cliente, ficha):
        campos_refeicoes = [
            'dados_cafe_da_manha',
            'dados_lanche_da_manha',
            'dados_almoco',
            'dados_lanche_da_tarde',
            'dados_jantar',
            'dados_lanche_da_noite',
        ]
        dados_grupo = {}

        for campo in campos_refeicoes:
            dados_refeicao = getattr(self, campo, None)

            if dados_refeicao:
                for grupo in dados_refeicao.get('dados_grupos', []):
                    if grupo['grupo_id'] == id_cliente:
                        dados_grupo[campo] = {
                            'hora': grupo.get('hora'),
                            'adultos': grupo['participantes'].get('adultos'),
                            'criancas': grupo['participantes'].get('criancas'),
                            'monitoria': grupo['participantes'].get('monitoria'),
                            'geral': grupo['participantes'].get('total'),
                        }

                        break

            if campo not in dados_grupo:
                dados_grupo[campo] = {
                    'hora': '',
                    'adultos': ficha.numero_adultos(),
                    'criancas': ficha.numero_criancas(),
                    'monitoria': 0,
                    'geral': ficha.numero_adultos() + ficha.numero_criancas(),
                }

        return dados_grupo

    def separar_refeicoes(self, id_grupos_excluidos):
        fichas = self.fichas_de_evento.all()
        eventos = []

        for ficha in fichas:
            if ficha.cliente.id not in id_grupos_excluidos:
                eventos.append({
                    'id': ficha.id,
                    'cliente': ficha.cliente,
                    'produto': ficha.produto,
                    'numero_adultos': ficha.numero_adultos(),
                    'numero_criancas': ficha.numero_criancas(),
                    'dados_refeicoes': self.pegar_dados_refeicoes(ficha.cliente.id, ficha)
                })

        return eventos
