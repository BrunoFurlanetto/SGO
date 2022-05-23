# Sistema de Gerenciamento Operacional (SGO)

## Resumo
<p align='justify'>
O sistema de Gerenciamento Operacional (SGO), é uma aplicação WEB que fará a unificação de todo o processo operacionais dentro da empresa, tomando para si os processos iniciais, como cadastro das  atividades que o cliente fará durante toda a estádia. Até os processos finais, com os cadatros de relatórios de atendimento e fichas de avaliação fornecidas pelo cliente.
</p>

## Objetivo
- <p align='justify'> O SGO busca como seu principal objetivo, fazer a unificação de todos os processos operacionais do grupo. Iniciando logo após a venda, com o cadastro da ficha de evento, passando pela criação das escalas e terminando com o cadastro dos relatórios de atendimento e fichas de avaliação pelo cliente.
</p>

## Tecnologias
- Linguagem:
  - Python
- Framework para WEB:
  - Django

## Módulos
<p>Dentro do sistema existem uma váriedade grande de módulos, podendo serem classificados
<b>essênciais</b> e <b>não essênciais</b>. No qual, a primeira classificação é o conjubnto
de módulos que são interligados do início da operação até o final, sendo eles:
</p>

- Ficha de evento;
- Ordem de serviço;
- Relatório de atendimento;
  - Colégio;
  - Empresa;
- Ficha de avaliação

<p>Agora quando entramos na gama dos módulos não essênciasi, estamos falando de módulos
que acrescentam funcionalidades a mais dentrod o sistema, que são (até o momento):</p>

- Escala;
- Calendário de eventos;
- Cadasro de relatório para atendimento a público;
- Detector de bombas;
- Paínel estátistico;
- Pré agendamento;
- Resumo financeiro dos funcionários;

<p>A frente será exposto um pouco de cada módulo, primeiramente dos principais e depois
módulos adicionais.</p>

### Ficha de Evento
Aqui temos a primeira etapa do processo, no qual o colaborador irá alimentar o banco e dados
com as informações gerais do evento como, cliente, repsonsável pelo evento, número de paricipantes, 
número de professores, dentre outras informações. Aqui também é o ponto em que é selecionado pela
primeira vez as atividades que irão realizar dentro do grupo.
