# Dashboard de Detecção de Anomalias com LOF

Este projeto apresenta um dashboard desenvolvido em **Streamlit** para análise de anomalias em dados de consumo de energia elétrica.

O algoritmo utilizado foi o **Local Outlier Factor (LOF)**, aplicado previamente no Google Colab. O dashboard utiliza o arquivo gerado no Colab:

```text
resultado_anomalias_lof_energia.csv
```

## Estrutura do projeto

```text
projeto_dashboard_anomalias_lof/
│
├── app.py
├── requirements.txt
├── resultado_anomalias_lof_energia.csv
└── README.md
```

## Como executar localmente

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Execute o dashboard:

```bash
streamlit run app.py
```

3. Acesse o link local exibido no terminal.

## Arquivo necessário

O dashboard espera encontrar o arquivo:

```text
resultado_anomalias_lof_energia.csv
```

Esse arquivo deve ser gerado na etapa do Google Colab, após a aplicação do algoritmo LOF.

Caso o arquivo não esteja na pasta do projeto, você também pode enviá-lo manualmente pela barra lateral do dashboard.

## O que o dashboard apresenta

- Descrição do projeto;
- Informações sobre o dataset;
- Quantidade de registros;
- Quantidade e percentual de anomalias;
- Gráficos de análise exploratória;
- Visualização das anomalias;
- Score de anomalia;
- Tabela com registros anômalos;
- Filtros interativos;
- Conclusão.

## Publicação

A atividade solicita publicação em nuvem usando Render ou Railway.

Para publicar, suba estes arquivos em um repositório no GitHub e conecte o repositório ao Render ou Railway.

## Comando de inicialização no Render

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Tema do projeto

**Detecção de consumo anormal de energia elétrica utilizando Local Outlier Factor (LOF).**