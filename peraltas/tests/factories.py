import factory
from django.contrib.auth.models import User
from django.utils import timezone

from ordemDeServico.models import OrdemDeServico
from peraltas.models import Eventos, FichaDeEvento, ClienteColegio, Responsavel, ProdutosPeraltas, Vendedor


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser{n}')
    email = 'testuser@example.com'
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')


class ClienteColegioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClienteColegio

    razao_social = factory.Faker('company')
    cnpj = factory.Sequence(lambda n: f'123456780001{n:02d}')
    nome_fantasia = factory.Faker('company_suffix')
    endereco = factory.Faker('street_address')
    bairro = factory.Faker('city')
    cidade = factory.Faker('city')
    estado = factory.Faker('state_abbr')
    cep = factory.Faker('postcode')
    responsavel_alteracao = factory.SubFactory(UserFactory)
    responsavel_cadastro = factory.SubFactory(UserFactory)


class ResponsavelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Responsavel

    nome = factory.Faker('name')
    fone = factory.Faker('phone_number')
    email_responsavel_evento = factory.Faker('email')

    # Relacionamento many-to-many com ListaDeCargos
    @factory.post_generation
    def cargo(self, create, extracted, **kwargs):
        if not create:
            # Apenas para evitar a criação automática de cargos
            return

        if extracted:
            for cargo in extracted:
                self.cargo.add(cargo)

    # Relacionamento com User (responsavel_cadastro e responsavel_atualizacao)
    responsavel_cadastro = factory.SubFactory(UserFactory)
    responsavel_atualizacao = factory.SubFactory(UserFactory)


class ProdutosPeraltasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProdutosPeraltas

    produto = factory.Faker('word')
    pernoite = factory.Faker('boolean')
    colegio = factory.Faker('boolean')
    brotas_eco = factory.Faker('boolean')
    meninos_e_meninas = factory.Faker('boolean')

    # Campos adicionais
    n_dias = factory.Faker('random_int', min=1, max=10)  # Exemplo de geração aleatória
    hora_padrao_check_in = factory.Faker('time')
    hora_padrao_check_out = factory.Faker('time')


class VendedorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vendedor

    usuario = factory.SubFactory(UserFactory)
    telefone = factory.Faker('phone_number')
    supervisor = factory.Faker('boolean')
    nota = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    n_avaliacoes = factory.Faker('random_int', min=0, max=100)


class FichaDeEventoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FichaDeEvento

    cliente = factory.SubFactory(ClienteColegioFactory)
    responsavel_evento = factory.SubFactory(ResponsavelFactory)
    produto = factory.SubFactory(ProdutosPeraltasFactory)
    check_in = factory.Faker('date_time_this_year')
    check_out = factory.Faker('date_time_this_year')
    vendedora = factory.SubFactory(VendedorFactory)
    empresa = factory.Iterator(['Peraltas', 'CEU', 'Peraltas CEU'])
    data_preenchimento = timezone.now()


class OrdemDeServicoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrdemDeServico

    tipo = factory.Iterator(['Colégio', 'Empresa'])
    ficha_de_evento = factory.SubFactory(FichaDeEventoFactory)
    instituicao = factory.Faker('company')
    cidade = factory.Faker('city')
    check_in = factory.Faker('date_time_this_year')
    check_out = factory.Faker('date_time_this_year')
    n_participantes = factory.Faker('random_int', min=1, max=100)
    responsavel_grupo = factory.Faker('name')
    empresa = factory.Iterator(['Peraltas', 'CEU', 'Peraltas CEU'])


class EventosFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Eventos

    colaborador = factory.SubFactory(VendedorFactory)
    cliente = factory.SubFactory(ClienteColegioFactory)
    data_check_in = factory.Faker('date_this_decade', before_today=True)
    hora_check_in = factory.Faker('time')
    data_check_out = factory.LazyAttribute(lambda o: o.data_check_in + timezone.timedelta(days=o.dias_evento))
    hora_check_out = factory.Faker('time')
    qtd_previa = factory.Faker('random_int', min=10, max=100)
    qtd_confirmado = factory.Faker('random_int', min=10, max=100)
    data_preenchimento = factory.Faker('date_this_decade')
    estagio_evento = factory.Faker('random_element',
                                   elements=['pre_reserva', 'confirmado', 'ficha_evento', 'ordem_servico'])
    codigo_pagamento = factory.Faker('bothify', text='#######')
    tipo_evento = factory.Faker('random_element', elements=['Colégio', 'Empresa'])
    dias_evento = factory.Faker('random_int', min=1, max=5)
    produto_peraltas = factory.SubFactory(ProdutosPeraltasFactory)
    adesao = factory.Faker('pyfloat', left_digits=2, right_digits=2, positive=True)
    veio_ano_anterior = factory.Faker('boolean')
