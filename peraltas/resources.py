from import_export import resources

from peraltas.models import Eventos


class EventosResource(resources.ModelResource):
    class Meta:
        model = Eventos
        fields = (
            'ordem_de_servico__id',
            'ficha_de_evento__id',
            'colaborador',
            'cliente',
            'cnpj',
            'responsavel',
            'cargo_responsavel',
            'telefone_responsavel',
            'email_responsavel',
            'data_check_in',
            'hora_check_in',
            'data_check_out',
            'hora_check_out',
            'qtd_previa',
            'qtd_confirmado',
            'data_preenchimento',
            'estagio_evento',
            'codigo_pagamento',
            'tipo_evento',
            'dias_evento',
            'produto_peraltas__produto',
            'produto_corporativo__produto',
            'adesao',
            'veio_ano_anterior',
        )

    def dehydrate_data_check_in(self, evento):
        return evento.data_check_in.strftime("%d/%m/%Y")

    def dehydrate_hora_check_in(self, evento):
        return evento.hora_check_in.strftime("%H:%M")

    def dehydrate_data_check_out(self, evento):
        return evento.data_check_out.strftime("%d/%m/%Y")

    def dehydrate_hora_check_out(self, evento):
        return evento.hora_check_out.strftime("%H:%M")

    def dehydrate_colaborador(self, evento):
        return evento.colaborador.usuario.get_full_name()

    def dehydrate_adesao(self, evento):
        return float(evento.adesao / 100)

    def dehydrate_cliente(self, evento):
        return evento.cliente

    def dehydrate_responsavel(self, evento):
        return evento.responsavel

    def dehydrate_qtd_previa(self, evento):
        return int(evento.qtd_previa)

    def dehydrate_qtd_confirmado(self, evento):
        return int(evento.qtd_confirmado)

    def dehydrate_data_preenchimento(self, evento):
        return evento.data_preenchimento.strftime("%d/%m/%Y")

    def dehydrate_dias_evento(self, evento):
        return int(evento.dias_evento)

    def dehydrate_veio_ano_anterior(self, evento):
        return 'Sim' if evento.veio_ano_anterior else 'Não'
