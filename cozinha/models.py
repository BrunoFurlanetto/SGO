from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from peraltas.models import ClienteColegio, FichaDeEvento, ProdutosPeraltas


class Cozinheiro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=11)


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
                        <input name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if cafe_manha != obj_nulo else 'disabled' } value="{ cafe_manha['hora'] }" type="time">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="lanhce_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if lanche_manha != obj_nulo else 'disabled' } value="{ lanche_manha['hora'] }" type="time">                        
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if almoco != obj_nulo else 'disabled' } value="{ almoco['hora'] }" type="time">                        
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if lanche_tarde != obj_nulo else 'disabled' } value="{ lanche_tarde['hora'] }" type="time">                        
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if jantar != obj_nulo else 'disabled' } value="{ jantar['hora'] }" type="time">                        
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if lanche_noite != obj_nulo else 'disabled' } value="{ lanche_noite['hora'] }" type="time">                        
                    </td>
                </tr>
                <tr>
                    <th>Adultos</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha adultos" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if cafe_manha != obj_nulo else 'disabled' } value="{ cafe_manha['participantes']['adultos'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha adultos" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_manha != obj_nulo else 'disabled' } value="{ lanche_manha['participantes']['adultos'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco adultos" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if almoco != obj_nulo else 'disabled' } value="{ almoco['participantes']['adultos'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde adultos" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_tarde != obj_nulo else 'disabled' } value="{ lanche_tarde['participantes']['adultos'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar adultos" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if jantar != obj_nulo else 'disabled' } value="{ jantar['participantes']['adultos'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite adultos" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_noite != obj_nulo else 'disabled' } value="{ lanche_noite['participantes']['adultos'] }">
                    </td>
                </tr>
                <tr>
                    <td class="informacao_grupo">{ self.tipo_evento }</td>
                    <th>Crianças</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha criancas" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if cafe_manha != obj_nulo else 'disabled' } value="{ cafe_manha['participantes']['criancas'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha criancas" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_manha != obj_nulo else 'disabled' } value="{ lanche_manha['participantes']['criancas'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco criancas" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if almoco != obj_nulo else 'disabled' } value="{ almoco['participantes']['criancas'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde criancas" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_tarde != obj_nulo else 'disabled' } value="{ lanche_tarde['participantes']['criancas'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar criancas" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if jantar != obj_nulo else 'disabled' } value="{ jantar['participantes']['criancas'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite criancas" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_noite != obj_nulo else 'disabled' } value="{ lanche_noite['participantes']['criancas'] }">
                    </td>
                </tr>
                <tr>
                    <td class="informacao_grupo">{ self.ficha_de_evento.numero_adultos() } adultos</td>
                    <th>Monitoria</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha monitoria" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if cafe_manha != obj_nulo else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ cafe_manha['participantes']['monitoria'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha monitoria" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if lanche_manha != obj_nulo else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ lanche_manha['participantes']['monitoria'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco monitoria" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if almoco != obj_nulo else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ almoco['participantes']['monitoria'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde monitoria" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if lanche_tarde != obj_nulo else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ lanche_tarde['participantes']['monitoria'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar monitoria" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if jantar != obj_nulo else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ jantar['participantes']['monitoria'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite monitoria" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if lanche_noite != obj_nulo else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ lanche_noite['participantes']['monitoria'] }">
                    </td>
                </tr>
                <tr class="ultima_linha">
                    <td class="informacao_grupo">{ self.ficha_de_evento.numero_criancas() } crianças</td>
                    <th>Total</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha geral" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if cafe_manha != obj_nulo else 'disabled' } value="{ cafe_manha['participantes']['total'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha geral" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_manha != obj_nulo else 'disabled' } value="{ lanche_manha['participantes']['total'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco geral" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if almoco != obj_nulo else 'disabled' } value="{ almoco['participantes']['total'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde geral" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_tarde != obj_nulo else 'disabled' } value="{ lanche_tarde['participantes']['total'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar geral" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if jantar != obj_nulo else 'disabled' } value="{ jantar['participantes']['total'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite geral" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if lanche_noite != obj_nulo else 'disabled' } value="{ lanche_noite['participantes']['total'] }">
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
            print('Ué')
        return dados_refeicoes, list(lista_ids_eventos), list(lista_ids_grupos)
