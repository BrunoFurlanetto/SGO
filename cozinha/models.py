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
        cafe_manha = lanche_manha = almoco = lanhce_tarde = jantar = lanche_noite = obj_nulo

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
                    lanhce_tarde = dia

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
                        <input name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_cafe_da_manha else 'disabled' } value="{ cafe_manha['hora'] }" type="time">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="lanhce_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_lanche_da_manha else 'disabled' } value="{ lanche_manha['hora'] }" type="time">                        
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_almoco else 'disabled' } value="{ almoco['hora'] }" type="time">                        
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_lanche_da_tarde else 'disabled' } value="{ lanhce_tarde['hora'] }" type="time">                        
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_jantar else 'disabled' } value="{ jantar['hora'] }" type="time">                        
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_lanche_da_noite else 'disabled' } value="{ lanche_noite['hora'] }" type="time">                        
                    </td>
                </tr>
                <tr>
                    <th>Adultos</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha adultos" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_cafe_da_manha else 'disabled' } value="{ cafe_manha['participantes']['adultos'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha adultos" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_manha else 'disabled' } value="{ lanche_manha['participantes']['adultos'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco adultos" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_almoco else 'disabled' } value="{ almoco['participantes']['adultos'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde adultos" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_tarde else 'disabled' } value="{ lanhce_tarde['participantes']['adultos'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar adultos" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_jantar else 'disabled' } value="{ jantar['participantes']['adultos'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite adultos" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_noite else 'disabled' } value="{ lanche_noite['participantes']['adultos'] }">
                    </td>
                </tr>
                <tr>
                    <td class="informacao_grupo">{ self.tipo_evento }</td>
                    <th>Crianças</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha criancas" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_cafe_da_manha else 'disabled' } value="{ cafe_manha['participantes']['criancas'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha criancas" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_manha else 'disabled' } value="{ lanche_manha['participantes']['criancas'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco criancas" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_almoco else 'disabled' } value="{ almoco['participantes']['criancas'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde criancas" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_tarde else 'disabled' } value="{ lanhce_tarde['participantes']['criancas'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar criancas" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_jantar else 'disabled' } value="{ jantar['participantes']['criancas'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite criancas" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_noite else 'disabled' } value="{ lanche_noite['participantes']['criancas'] }">
                    </td>
                </tr>
                <tr>
                    <td class="informacao_grupo">{ self.ficha_de_evento.numero_adultos() } adultos</td>
                    <th>Monitoria</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha monitoria" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_cafe_da_manha else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ cafe_manha['participantes']['monitoria'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha monitoria" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_lanche_da_manha else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ lanche_manha['participantes']['monitoria'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco monitoria" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_almoco else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ almoco['participantes']['monitoria'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde monitoria" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_lanche_da_tarde else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ lanhce_tarde['participantes']['monitoria'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar monitoria" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_jantar else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ jantar['participantes']['monitoria'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite monitoria" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" { 'readonly' if self.dados_lanche_da_noite else 'disabled' } type="number" onchange="atualizar_monitoria(this)" value="{ lanche_noite['participantes']['monitoria'] }">
                    </td>
                </tr>
                <tr class="ultima_linha">
                    <td class="informacao_grupo">{ self.ficha_de_evento.numero_criancas() } crianças</td>
                    <th>Total</th>
                    <td class="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="cafe_manha geral" name="cafe_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_cafe_da_manha else 'disabled' } value="{ cafe_manha['participantes']['total'] }">
                    </td>
                    <td class="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_manha geral" name="lanche_manha-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_manha else 'disabled' } value="{ lanche_manha['participantes']['total'] }">
                    </td>
                    <td class="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="almoco geral" name="almoco-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_almoco else 'disabled' } value="{ almoco['participantes']['total'] }">
                    </td>
                    <td class="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_tarde geral" name="lanche_tarde-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_tarde else 'disabled' } value="{ lanhce_tarde['participantes']['total'] }">
                    </td>
                    <td class="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="jantar geral" name="jantar-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_jantar else 'disabled' } value="{ jantar['participantes']['total'] }">
                    </td>
                    <td class="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }">
                        <input class="lanche_noite geral" name="lanche_noite-{ data.strftime('%d_%m_%Y') }-{ self.ficha_de_evento.id }" type="number" { 'readonly' if self.dados_lanche_da_noite else 'disabled' } value="{ lanche_noite['participantes']['total'] }">
                    </td>
                </tr>
            """




class RelatorioDia(models.Model):
    fichas_de_evento = models.ManyToManyField(FichaDeEvento)
    grupos = models.ManyToManyField(ClienteColegio)
    data = models.DateField(default=timezone.now)
    total_pax_adulto = models.PositiveIntegerField(default=0)
    total_pax_crianca = models.PositiveIntegerField(default=0)
    total_pax_monitoria = models.PositiveIntegerField(default=0)
    total_geral_pax = models.PositiveIntegerField(default=0, editable=False)
    dados_cafe_da_manha = models.JSONField(null=True, blank=True)
    dados_lanche_da_manha = models.JSONField(null=True, blank=True)
    dados_almoco = models.JSONField(null=True, blank=True)
    dados_lanche_da_tarde = models.JSONField(null=True, blank=True)
    dados_jantar = models.JSONField(null=True, blank=True)
    dados_lanche_da_noite = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'Relatorio rfeicoes {self.data.strftime("%d/%m/%Y")}'

    def save(self, *args, **kwargs):
        self.total_geral_pax = self.total_pax_adulto + self.total_pax_crianca + self.total_pax_monitoria
        super().save(*args, **kwargs)
