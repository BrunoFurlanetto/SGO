from django.contrib.auth.models import User
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

from orcamento.models import Orcamento
from peraltas.models import ClienteColegio, Responsavel, Vendedor


class OrcamentoPDF:
    def __init__(self, id_orcamento):
        self.orcamento = Orcamento.objects.get(pk=id_orcamento)
        self.modelo_pptx = "orcamento/modelos/pdf.pptx"
        self.presentation = Presentation(self.modelo_pptx)
        self.cor_fonte = RGBColor(131, 128, 131)
        self.tamanho_fonte = Pt(14)
        self.fonte = 'IBM Plex Sans'

    def gerar_pdf(self):
        self.__alterar_dados_cliente_responsavel()
        self.__alterar_dados_vendedora()
        self.__salvar_pdf()

    def __obter_shape_por_nome(self, nome_do_shape):
        for slide in self.presentation.slides:
            for shape in slide.shapes:
                if shape.name == nome_do_shape:
                    return shape

        return None

    def __substituir_texto(self, nome_do_shape, valor_shape):
        shape = self.__obter_shape_por_nome(nome_do_shape)

        if shape:
            shape.text = valor_shape

            for p in shape.text_frame.paragraphs:
                for _p in p.runs:
                    _p.font.name = self.fonte
                    _p.font.size = self.tamanho_fonte
                    _p.font.color.rgb = self.cor_fonte
                    shape.text_frame.word_wrap = True
                    shape.text_frame.auto_size = True

    def __salvar_pdf(self):
        self.presentation.save('pdf_teste.pdf')

    def __alterar_dados_cliente_responsavel(self):
        cliente = ClienteColegio.objects.get(pk=self.orcamento.cliente.id)
        responsavel = Responsavel.objects.get(pk=self.orcamento.responsavel.id)

        self.__substituir_texto('NomeColegio', cliente.nome_fantasia)
        self.__substituir_texto('NomeResponsavel', responsavel.nome)
        self.__substituir_texto('TelefoneResponsavel', responsavel.fone)
        self.__substituir_texto('EmailResponsavel', responsavel.email_responsavel_evento)

    def __alterar_dados_vendedora(self):
        vendedora = Vendedor.objects.get(usuario=self.orcamento.colaborador)
        self.__substituir_texto('NomeVendedora', vendedora.usuario.get_full_name())
        self.__substituir_texto('TelefoneVendedora', vendedora.telefone)
        self.__substituir_texto('WhatsVendedora', vendedora.telefone)
        self.__substituir_texto('EmailVendedora', vendedora.usuario.email)
