import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
from janitor import clean_names, remove_empty
import re
import plotly.subplots as sp

# Funcao troca sinal do df qdo negativo para mostrar linhas acima do eixo X usada de forma local de acordo com o df
def troca_sinal(dataframe, colunas):
    for e in colunas:
        if (dataframe[e] < 0).any():
            dataframe[e] = abs(dataframe[e])

# Funcao de grafico de linhas paralelas em relacao a coluna mes (x='mes')
def linhas_paral(dataframe, colunas):
    '''
    Funcao retorna grafico de linhas paralelas com hover simultaneo das linhas em relacao a posicao x.
    Funcao corrige sinal negativo para que o grafico seja mostrado acima de x.
    input: dataframe e lista de colunas
    output: grafico plotly
    '''
    # titulo faz a limpeza dos nomes das colunas
    titulo = re.sub(r'[0-9]', '', plots[0]).replace('_', ' ').replace('+', ' ').title()
    fig_linhas_paral = px.line(dataframe, x='mes', y=colunas, title = f'{titulo}', labels={'value':'Valores', 'mes':''})
    fig_linhas_paral.update_traces(mode="markers+lines", hovertemplate=None)
    fig_linhas_paral.update_layout(hovermode="x unified", legend=dict(title="Despesas/Taxas"))
    return(fig_linhas_paral)


# Funcao calcula metricas Melhor:max, Pior:min, Media:mean e STD:std das colunas especificadas do dataframe
def calc_metricas(dataframe, colunas):
    '''
    Funcao retorna dataframe das metricas Melhor:max, Pior:min, Media:mean e STD:std das colunas.
    input: dataframe e lista de colunas
    output: dataframe
    '''
    for i in colunas:
        print(f'Metricas: {i}')
        display(pd.DataFrame({'Melhor' : [f'{dataframe[i].max():,.2f}'], 'Pior' : [f'{dataframe[i].min():,.2f}'], 'Media' : [f'{dataframe[i].mean():,.2f}'], 'STD' : [f'{dataframe[i].std():,.2f}']}, index=['']))

# Funcao cria colunas de percentual dos elementos da coluna em relacao ao proprio total
def calc_perc(data, coluna):
    df_col = data[coluna].copy()
    
    for coluna in df_col.columns:
        df_col[f'perc_{coluna}'] = df_col[coluna]/df_col[coluna].sum()
        df_col[f'{coluna}/ROB'] = df_col[coluna]/df_col['Receita Operacional Bruta']

    return df_col

# Funcao gera colunas dentro do container com total e percentual sobre o ROB
def gera_medidas (lista_titulo, lista_coluna, lista_cols):
        """
        Funcao gera colunas dentro do container com total e percentual sobre o ROB
        input: 3 listas (titulo de exibicao, lista das colunas do df, lista das col a serem criadas)
        output: st.markdown com respectivos valores nas respectivas colunas
        """
        for titulo, coluna, col in zip(lista_titulo, lista_coluna, lista_cols):
            with col:
                st.markdown(f'###### {titulo}')
                valor = df_perc[coluna].sum()
                percentual = valor / df_perc['Receita Operacional Bruta'].sum()
                # Correcao da formatacao de numeros casa decimal e milhar
                st.markdown(f"#### {valor:,.2f}".replace(',', ';').replace('.', ',').replace(';', '.'))
                st.markdown(f"##### :green[{percentual:.2%}]".replace('.', ','))

#===============
# Carregando dados
#===============

df = pd.read_excel('DRE_G.xlsx', sheet_name='DRE_dummy', engine='openpyxl', index_col='Variaveis',
                   usecols=['Variaveis', 'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])

# Gerando df transposta
df_trans = df.T.reset_index()

df_trans = df_trans.rename(columns={'index':'Mes'})


#===============
# Criando sidebar
#===============

st.sidebar.title('Exercicio 2021')
meses_selecionados = st.sidebar.multiselect('Meses', list(df_trans['Mes'].unique()), default=['Jan', 'Fev', 'Mar'])

# Filtrando df_trans pelos meses selecionados
df_meses_selecionados = df_trans[df_trans['Mes'].isin(meses_selecionados)].copy()

st.sidebar.write('---')
st.sidebar.markdown('##### Powered by FREDAO:nerd_face:')


#===============
# Layout
#===============

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(["Principais", "ROB" , "ROL", "MCl", "MC2", "EBITDA", "ROP", "RAI", "RGP"])

#------------------ Principais indicadores -----------------------------------------------------------------------------------------------
with tab1:
    st.markdown("### Principais Indicadores")
    # Calculando percentuais
    df_perc = calc_perc(df_meses_selecionados, ['Receita Operacional Bruta', 'Deduções Da Receita Operacional Bruta', 'Receita Operacional Liquida', 'Custo Das Vendas', 'Margem de Contribuição 1', 'Margem de Contribuição 2', 'Ebitda', 'Despesa com Escritório', 'Resultado Operacional', '(+/-) Resultado Financeiro Líquido','Resultado Antes do Imposto', 'Resultado Gerencial do Período'])
    df_perc['Mes'] = df_trans['Mes']
    
    px.bar(df_perc, x='Mes', y=['Receita Operacional Bruta/ROB', 'Receita Operacional Liquida/ROB', 'Custo das Vendas/ROB'])

    # exibindo df transposto, correcao de virgulas e pontos decimais, destaque do valor minimo
    
    st.dataframe(df_perc.set_index('Mes').T.style.format(precision=2, decimal=',', thousands='.').highlight_min(color='red'), 
                 use_container_width=True)


    #st.metric(label='Receita Operacional Bruta', value=f"{df_perc['Receita Operacional Bruta'].sum():,.2f}")
    # total_ROB = f"{df_perc:,.3f}".replace(',', ';').replace('.', ',').replace(';', '.')
    # st.markdown(f"#### Consolidado Receita Operacional Bruta (ROB): " + total_ROB)
    st.markdown(f"### Consolidado Receita Operacional Bruta (ROB): {df_perc['Receita Operacional Bruta'].sum():,.2f}".replace(',', ';').replace('.', ',').replace(';', '.'))

    st.write('---')
    
    with st.container():
        st.markdown("#### Consolidado anual e respectivos percentuais sobre ROB")
        col1, col2, col3 = st.columns(3)
        lista_titulo = ['ROL', 'MC1', 'MC2']
        lista_coluna = ['Receita Operacional Liquida', 'Margem de Contribuição 1', 'Margem de Contribuição 2']
        lista_cols = st.columns(len(lista_titulo))

        gera_medidas (lista_titulo, lista_coluna, lista_cols)

    st.write('---')

    with st.container():
        col4, col5, col6 = st.columns(3)
        lista_titulo = ['Ebitda', 'Resultado Operacional', 'Resultado Financeiro Líquido']
        lista_coluna = ['Ebitda', 'Resultado Operacional', '(+/-) Resultado Financeiro Líquido']
        lista_cols = st.columns(len(lista_titulo))

        gera_medidas (lista_titulo, lista_coluna, lista_cols)
                   
    st.write('---')

    with st.container():
        col7, col8 = st.columns(2)
        lista_titulo = ['Resultado Antes do Imposto', 'Resultado Gerencial do Período']
        lista_coluna = ['Resultado Antes do Imposto', 'Resultado Gerencial do Período']
        lista_cols = st.columns(len(lista_titulo))

        gera_medidas (lista_titulo, lista_coluna, lista_cols)

    st.write('---')


#     with st.container():  # grafico em cascata flying bricks
        
#         df_perc_rob = df_perc.filter(like='/ROB').drop('Receita Operacional Bruta/ROB', axis=1)
#         # df_perc_rob['Mes'] = df_perc['Mes']
#         st.dataframe(df_perc_rob)
        
        
#         st.markdown('grafico em cascata flying bricks')
#         df_perc_rob = df_perc.filter(like='/ROB')   # st.dataframe(df_perc)
        
#         st.dataframe(df_perc_rob)
#         # st.dataframe(df_perc_rob.set_index('Mes'), use_container_width=True)

        
#         fig_teste = px.bar(df_perc_rob, x='Mes', y=['Receita Operacional Bruta/ROB', 'Receita Operacional Liquida/ROB', 'Custo das Vendas/ROB','Deduções Da Receita Operacional Bruta/ROB', 'Margem de Contribuição 1/ROB', 'Margem de Contribuição 2/ROB', 'Ebitda/ROB'])
#         st.plotly_chart(fig_teste)



#------------------ ROB ---------------------------------------------------------------------------------------------------------------

with tab2: 
    st.markdown("#### Receita Operacional Bruta")
    # Selecionando principais metricas das colunas desejadas com describe

    df_metricas = calc_perc(df_meses_selecionados, ['Receita Operacional Bruta', '1.1 - Vendas de mercadorias', '1.2 - Prestação De Serviços', '1.3 – Pacotes'])
    st.dataframe(df_metricas, use_container_width=True)
    
    # DISTRIBUICAO DA RECEITA OPERACIONAL BRUTA ENTRE VENDA DE MERCADORIAS E PRESTACAO DE SERVICOS

    total_VM = df_meses_selecionados['1.1 - Vendas de mercadorias'].sum()
    total_PS = df_meses_selecionados['1.2 - Prestação De Serviços'].sum()
    total_PC = df_meses_selecionados['1.3 – Pacotes'].sum()
    
    st.markdown("##### Distribuicao do ROB entre VM, PS, e Pacotes")
    fig_pie = px.pie(df_meses_selecionados, values=[total_VM, total_PS, total_PC], names=['VM', 'PS', 'Pacotes'], hole=0.5)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # DISTRIBUICAO MENSAL DE ROB VM E PS excluindo a linha Total
    st.markdown("##### Distribuicao Mensal ROB por VM, PS, Pacotes")

    fig_vmps = px.line(df_meses_selecionados.iloc[0:12,:], x='Mes', y=['Receita Operacional Bruta', '1.1 - Vendas de mercadorias','1.2 - Prestação De Serviços','1.3 – Pacotes'], labels={'Mes':'', 'value':'Valores'})
    fig_vmps.update_traces(mode="markers+lines", hovertemplate=None)
    fig_vmps.update_layout(hovermode="x unified", showlegend=False) 
    st.plotly_chart(fig_vmps, use_container_width=True)
    
#------------------ ROL -----------------------------------------------------------------------------------------------------------------
with tab3:
    st.markdown("#### Receita Operacional Liquida")
    # Criando df de colunas selecionadas
    df_rol = df_meses_selecionados.iloc[:,[0, 1, 6, 7, 8, 9, 10, 11, 12,13]]
    # Renomeando colunas
    df_rol.columns = ['Mes','ROB', 'Imposto_venda', 'COFINS', 'ICMS', 'ISS', 'Simples', 'devol_vendas','desc_abat','ROL']
    st.dataframe(df_rol.set_index('Mes'), use_container_width=True)
    
    st.markdown("##### Distribuicao Mensal ROB, Imposto_venda,ROL")

    fig_rol = px.line(df_rol, x='Mes', y=['ROB', 'Imposto_venda','ROL'])
    fig_rol.update_traces(mode="markers+lines", hovertemplate=None)
    fig_rol.update_layout(hovermode="x unified", showlegend=False) 
    st.plotly_chart(fig_rol, use_container_width=True)
    
    # Grafico dos impostos
    fig_rol_imp = px.bar(df_rol, x='Mes', y=['COFINS', 'ICMS', 'ISS', 'Simples', 'devol_vendas','desc_abat'], barmode='group')
    st.plotly_chart(fig_rol_imp, use_container_width=True)


#------------------ MC1 ----------------------------------------------------------------------------------------------------------------
with tab4:
    st.markdown("#### Margem de Contribuicao 1")
    df_mc1 = df_meses_selecionados.iloc[:,[0, 1, 14,15,16,17]]
    df_mc1.columns = ['Mes', 'ROB', 'Custo_Vendas', 'Custo_Mercadoria', 'Perdas_Estoque', 'MC1']
    st.dataframe(df_mc1.set_index('Mes'), use_container_width=True)
    
    st.markdown("##### Distribuicao Mensal MC1, Imposto_venda,ROL")

    fig_mc1 = px.line(df_mc1, x='Mes', y=['ROB', 'Custo_Vendas','MC1'])
    fig_mc1.update_traces(mode="markers+lines", hovertemplate=None)
    fig_mc1.update_layout(hovermode="x unified", showlegend=False) 

    st.plotly_chart(fig_mc1, use_container_width=True)
    
    # Grafico dos impostos
    fig_mc1_imp = px.bar(df_mc1, x='Mes', y=['Custo_Mercadoria', 'Perdas_Estoque'], barmode='group')
    st.plotly_chart(fig_mc1_imp, use_container_width=True)

#------------------ MC2 ----------------------------------------------------------------------------------------------------------------

with tab5:
    st.markdown("#### Margem de Contribuicao 2")

    df_mc2 = df_meses_selecionados.iloc[:, 18:36]

    # Removendo colunas zeradas

    for coluna in df_mc2.columns:
        if df_mc2[coluna].sum() == 0:
            df_mc2.drop(coluna, axis=1, inplace=True)

    df_mc2.columns = ['Outros','Comis_vendas','taxa_cartao','taxa_franq','esforco_mark','esforco_mark_prom','midia_reg','midia_loc','amostras','flaconetes','eventos','brindes','embalagem','MC2']

    df_mc2['Mes'] = df_meses_selecionados['Mes']
    df_mc2['ROB'] = df_meses_selecionados['Receita Operacional Bruta']

    st.dataframe(df_mc2.set_index('Mes'), use_container_width=True)

    st.markdown("##### Distribuicao Mensal, Outros, Esforco Marketing, Embalagem, MC2")

    fig_mc2 = px.line(df_mc2, x='Mes', y=['ROB', 'Outros','esforco_mark_prom','embalagem','MC2'], labels=dict(value='Valores', Mes=''))
    fig_mc2.update_traces(mode="markers+lines", hovertemplate=None)
    fig_mc2.update_layout(hovermode="x unified", showlegend=False) 

    st.plotly_chart(fig_mc2, use_container_width=True)

    # Grafico dos impostos
    fig_mc2_imp = px.bar(df_mc2, x='Mes', y=['Comis_vendas', 'taxa_cartao','taxa_franq', 'esforco_mark', 'midia_reg','midia_loc','amostras','flaconetes','eventos','brindes'], barmode='group', labels=dict(value='Valores', Mes=''))
    st.plotly_chart(fig_mc2_imp, use_container_width=True)

    # Plotando as despesas em grafico individuais
    # listando colunas
    lista_subplot = ['Comis_vendas', 'taxa_cartao','taxa_franq', 'esforco_mark', 'midia_reg','midia_loc','amostras','flaconetes','eventos','brindes']
    
    # limpando nome das colunas e armazenando em outra variavel
    lista_mc2 = [nome.replace('_', ' ').replace('+', ' ').title() for nome in lista_subplot]

    # formando espaco de plotagem com titulos limpos
    fig_mc2_imp2 = sp.make_subplots(rows=5, cols=2, subplot_titles=lista_mc2)

    for i, subplot_title in enumerate(lista_subplot):
        row = (i // 2) + 1  # define a linha da subparcela com base no índice do subplot_title
        col = (i % 2) + 1   # define a coluna da subparcela com base no índice do subplot_title
        fig_mc2_imp2.add_trace(go.Scatter(x=df_mc2['Mes'], y=abs(df_mc2[subplot_title]), mode='lines+markers', line=go.scatter.Line()), row=row, col=col)

        fig_mc2_imp2.update_layout(height=800, width=1200, title_text="DESPESAS COMPONENTES DE MC2 ", showlegend=False)
    st.plotly_chart(fig_mc2_imp2, use_container_width=True)
                                        
#------------------ EBITDA -------------------------------------------------------------------------------------------------------------
        
with tab6:
    df_ebitda = (df_meses_selecionados.iloc[:,36:137].pipe(clean_names).pipe(remove_empty))
    
    # Removendo colunas zeradas

    for coluna in df_ebitda.columns:
        if df_ebitda[coluna].sum() == 0:
            df_ebitda.drop(coluna, axis=1, inplace=True)
        
        #df_ebitda[f'perc_{coluna}'] = df_ebitda[coluna]/df_ebitda[coluna].sum()
    
    # Criando colunas percetuais
    
    for coluna in df_ebitda.columns:                            
        df_ebitda[f'perc_{coluna}'] = df_ebitda[coluna]/df_ebitda[coluna].sum()
    
         # Acrescentando colunas de mes
    df_ebitda['mes'] = df_meses_selecionados['Mes']

    st.markdown('##### Ebitda: (MC2 - Despesas Operacionais)')

    st.dataframe(df_ebitda.set_index('mes'), use_container_width=True)

    # Metricas    
    media_ebitda = df_ebitda['ebitda'].mean()
    max_ebitda = df_ebitda['ebitda'].max()
    min_ebitda = df_ebitda['ebitda'].min()
    std_ebitda = df_ebitda['ebitda'].std()

    st.write((pd.DataFrame({'Melhor' : [f'{max_ebitda:,.2f}'], 'Pior' : [f'{min_ebitda:,.2f}'], 'Media' : [f'{media_ebitda:,.2f}'], 'STD' : [f'{std_ebitda:,.2f}']}, index=[''])))


    # Criar figura
    fig_ebitda = go.Figure()

    # Plotando ebitda
    
    
    
        # Adicionar linha da coluna analisada ao gráfico com hover mostrando valor e percentual
    fig_ebitda.add_trace(go.Scatter(x=df_ebitda['mes'], y=df_ebitda['ebitda'], mode='lines+markers',hovertemplate='Valor: %{y:,.2f}<br>Perc do Total: %{customdata:.2f}%<extra></extra>', customdata=df_ebitda['perc_ebitda']))    
     
        # Adicionar linha da média ao gráfico
    fig_ebitda.add_shape(type='line', xref='paper', yref='y', x0=0, x1=1, y0=media_ebitda, y1=media_ebitda,line=dict(color='red', dash='dash'), name='Média')

        # Definir layout
    fig_ebitda.update_layout(xaxis_title='', yaxis_title='Ebitda', showlegend=False)

        # Exibir gráfico
    st.plotly_chart(fig_ebitda, use_container_width=True)
    
    # Listas das despesas que compoem Ebitda
    lista_ebit_desp = ['ebitda','8_1_despesas_estruturais','8_2_despesas_com_comunicacao', '8_3_despesas_de_apoio_a_operacao', '8_4_pessoal', '8_5_taxa_de_ocupacao', '8_6_despesas_com_veiculos', '8_7_despesas_administrativas', '8_8_despesas_gerais', '8_8_6_outras_despesas', '8_9_servicos_de_terceiros']

         # Analisando Despesas Estruturais
    lista_desp_estru = ['8_1_despesas_estruturais','8_1_1_agua', '8_1_2_energia_eletrica', '8_1_3_limpeza_e_conservacao', '8_1_4_manutencao_e_reparos']

     # Despesa comuinicacao
    lista_desp_comunicacao = ['8_2_despesas_com_comunicacao', '8_2_1_pos_cartoes', '8_2_2_vsat', '8_2_3_telefonia', '8_2_4_internet']

     #  Despesa apoio operacional
    lista_desp_apoio_op = ['8_3_despesas_de_apoio_a_operacao', '8_3_2_vitrines', '8_3_4_uniformes']

     # Analise das Despesas Pessoal(Salario e composicoes)
    lista_pessoal_salario = ['8_4_pessoal', '8_4_1_salarios', '8_4_1_1_salarios', '8_4_1_2_13º_salario', '8_4_1_3_hora_extra', '8_4_1_4_dsr', '8_4_1_5_ferias', '8_4_1_7_irrf_salarios','8_4_1_8_contribuicao_sindical', '8_4_1_9_adiantamento_salarial', '8_4_1_11_descontos_gerais_sobre_folha', '8_4_1_12_descontos_inss', '8_4_1_13_descontos_irrf','8_4_1_14_descontos_sobre_beneficios']

     # Analise das Despesas Pessoal (Encargos e composicoes)
    lista_pessoal_encargos = ['8_4_2_encargos_sociais', '8_4_2_1_inss_empresa', '8_4_2_2_fgts']

     # Analise das Despesas Pessoal (Beneficios e composicoes)
    lista_pessoal_benef = ['8_4_3_beneficios', '8_4_3_1_vale_transporte','8_4_3_2_vale_refeicao', '8_4_3_3_plano_de_saude', '8_4_3_4_premios_bonus', '8_4_3_6_ajuda_de_custo', '8_4_3_7_farmacia']

     # Analise das Despesas Pessoal
    lista_pessoal_recisao = ['8_4_4_movimentacao_de_pessoal','8_4_4_1_rescisao_do_contrato_de_trabalho']

     # Analise taxa ocupacao
    lista_ocupacao = ['8_5_taxa_de_ocupacao', '8_5_1_aluguel', '8_5_5_iptu']

     # Analise despesas com veiculos
    lista_veiculos = ['8_6_despesas_com_veiculos', '8_6_1_ipva_licenciamento', '8_6_3_combustivel', '8_6_4_manutencao_veiculos', '8_6_7_multa_veiculos']

     # Analise despesas administrativas
    lista_admin = ['8_7_despesas_administrativas', '8_7_1_material_de_escritorio', '8_7_4_copa_e_cozinha', '8_7_5_despesas_bancarias', '8_7_6_outras_despesas_administrativas']

     # Analise despesas gerais
    lista_gerais = ['8_8_despesas_gerais', '8_8_2_doacoes', '8_8_2_2_outras_entidades', '8_8_3_impostos_e_taxas', '8_8_3_3_taxa_de_licenca_e_alvara', '8_8_3_4_outros_impostos_e_taxas', '8_8_4_seguros', '8_8_5_treinamento', '8_8_6_outras_despesas']

     # Analise despesas com terceiros
    lista_terceiros = ['8_9_servicos_de_terceiros', '8_9_1_contabilidade', '8_9_3_servicos_de_informatica', '8_9_4_servicos_vigilancia_e_seguranca', '8_9_6_servicos_de_transporte', '8_9_7_outros_servicos_terceirizados', '8_9_11_sistemas']


    
    
    # loop de plotagem das listas dos componentes da Ebitda
    for plots in [lista_ebit_desp,lista_desp_estru,lista_desp_comunicacao,lista_desp_apoio_op,lista_pessoal_salario,lista_pessoal_encargos,lista_pessoal_benef,lista_pessoal_recisao,lista_ocupacao,lista_veiculos,lista_admin, lista_gerais, lista_terceiros]:
                     #titulo = re.sub(r'[0-9]', '', plots[0]).replace('_', ' ').title()
                     #st.markdown(f'##### Ebitda:{titulo}')
                     st.plotly_chart(linhas_paral(df_ebitda, plots), use_container_width=True)

# ---------------------------- ROP -----------------------------------------------------------------------------------------------------
                    
with tab7:    
     
    df_res_op = (df_meses_selecionados.iloc[:,138:165].pipe(clean_names).pipe(remove_empty))
    
     # Removendo colunas zeradas

    for coluna in df_res_op.columns:
        if df_res_op[coluna].sum() == 0:
            df_res_op.drop(coluna, axis=1, inplace=True)
    
    # Criando colunas percetuais
    
    for coluna in df_res_op.columns:                            
        df_res_op[f'perc_{coluna}'] = df_res_op[coluna]/df_res_op[coluna].sum()
    
    df_res_op['mes'] = df_meses_selecionados['Mes']
    
    st.dataframe(df_res_op.set_index('mes'), use_container_width=True)

    # Metricas    
    media_df_res_op = df_res_op['resultado_operacional'].mean()
    max_df_res_op = df_res_op['resultado_operacional'].max()
    min_df_res_op = df_res_op['resultado_operacional'].min()
    std_df_res_op = df_res_op['resultado_operacional'].std()

    st.write((pd.DataFrame({'Melhor' : [f'{max_df_res_op:,.2f}'], 'Pior' : [f'{min_df_res_op:,.2f}'], 'Media' : [f'{media_df_res_op:,.2f}'], 'STD' : [f'{std_df_res_op:,.2f}']}, index=[''])))
    
    #st.markdown('##### Resultado Operacional:')
    #st.markdown(' Res. Finan. Liquido + Desp. Finan. + Depreciacao + Receitas/Desp Nao Operacionais')
    
    lista_res_fin_liq = ['_+_resultado_financeiro_liquido','10_1_receitas_financeiras', '10_1_1_juros_sobre_receitas',
       '10_1_3_descontos_sobre_despesas', '10_1_4_rendimento_de_aplicacoes','10_1_6_sobra_de_caixa']
    
    lista_desp_finan = ['10_2_despesas_financeiras', '10_2_1_juros_sobre_despesas', '10_2_3_descontos_sobre_receitas', '10_2_4_juros_sobre_emprestimos', '10_2_5_taxa_de_antecipacao_de_cartoes', '10_2_6_iof', '10_2_8_outras_despesas_financeiras', '10_2_9_falta_de_caixa']
    
    for plots in [lista_res_fin_liq, lista_desp_finan]:
                     st.plotly_chart(linhas_paral(df_res_op, plots), use_container_width=True)

# ---------------------------- RAI ------------------------------------------------------------------------------------------------------

with tab8:
            
    df_rai = (df_meses_selecionados.iloc[:,[136,137,138,167]].pipe(clean_names).pipe(remove_empty))
    
    # Removendo colunas zeradas
    df_rai = df_rai[~(df_rai == 0).all(axis=1)]
    
    
    # Criando colunas percetuais
    
    for coluna in df_rai.columns:                            
        df_rai[f'perc_{coluna}'] = df_rai[coluna]/df_rai[coluna].sum()
    
         # Acrescentando colunas de mes
    df_rai['mes'] = df_meses_selecionados['Mes']

    st.dataframe(df_rai.set_index('mes'), use_container_width=True)

    # Metricas    
    media_df_rai = df_rai['resultado_operacional'].mean()
    max_df_rai = df_rai['resultado_operacional'].max()
    min_df_rai = df_rai['resultado_operacional'].min()
    std_df_rai = df_rai['resultado_operacional'].std()

    st.write((pd.DataFrame({'Melhor' : [f'{max_df_rai:,.2f}'], 'Pior' : [f'{min_df_rai:,.2f}'], 'Media' : [f'{media_df_rai:,.2f}'], 'STD' : [f'{std_df_rai:,.2f}']}, index=[''])))
    
    lista_rai = ['ebitda','despesa_com_escritorio','resultado_operacional','resultado_antes_do_imposto']
    
    # Formatacao dos nomes das colunas para titulos de cada grafico
    lista_rai_nome = [nome.replace('_', ' ').replace('+', ' ').title() for nome in lista_rai]
     
    # Subplots necessario para melhor visualizaca das variaveis
    
    # Estancia para definir subplots
    fig_df_rai = sp.make_subplots(rows=2, cols=2, subplot_titles=lista_rai_nome) 
    for i, coluna in enumerate(lista_rai):
        linha = i // 2 + 1
        coluna_subplot = i % 2 + 1
        fig_df_rai.add_trace(go.Scatter(x=df_rai['mes'], y=df_rai[coluna], mode='lines+markers', line=go.scatter.Line()), row=linha, col=coluna_subplot)

    # atualizar layout dos subplots
    fig_df_rai.update_layout(height=600, width=1080, title_text="DISTRIBUICAO DA COMPOSICAO DE RESULTADO ANTES DOS IMPOSTOS", showlegend=False)

    st.plotly_chart(fig_df_rai, use_container_width=True)
    
# ---------------------------- RGP -----------------------------------------------------------------------------------------------------

with tab9:
    st.write('Resultado Operacional do Periodo')
    
    df_rgp = (df_meses_selecionados.iloc[:,[167,168,171]].pipe(clean_names).pipe(remove_empty))

    
    # Removendo colunas zeradas
    df_rgp = df_rgp[~(df_rgp == 0).all(axis=1)]
    
    
    # Criando colunas percetuais
    
    for coluna in df_rgp.columns:                            
        df_rgp[f'perc_{coluna}'] = df_rgp[coluna]/df_rgp[coluna].sum()
    
         # Acrescentando colunas de mes
    df_rgp['mes'] = df_meses_selecionados['Mes']

    st.dataframe(df_rgp, use_container_width=True)

    # Metricas    
    media_rgp = df_rgp['resultado_antes_do_imposto'].mean()
    max_rgp = df_rgp['resultado_antes_do_imposto'].max()
    min_rgp = df_rgp['resultado_antes_do_imposto'].min()
    std_rgp = df_rgp['resultado_antes_do_imposto'].std()

    st.write((pd.DataFrame({'Melhor' : [f'{max_rgp:,.2f}'], 'Pior' : [f'{min_rgp:,.2f}'], 'Media' : [f'{media_rgp:,.2f}'], 'STD' : [f'{std_rgp:,.2f}']}, index=[''])))

        # Criar figura
    fig_rgp = go.Figure()

    # Plotando ebitda
    st.markdown('##### Resultado Gerencial do Periodo')
        
        # Adicionar linha da coluna analisada ao gráfico com hover mostrando valor e percentual
    fig_rgp.add_trace(go.Scatter(x=df_rgp['mes'], y=df_rgp['resultado_gerencial_do_periodo'], mode='lines+markers',hovertemplate='Valor: %{y:,.2f}<br>Perc do Total: %{customdata:.2f}%<extra></extra>', customdata=df_rgp['perc_resultado_gerencial_do_periodo']))    
     
        # Adicionar linha da média ao gráfico
    fig_rgp.add_shape(type='line', xref='paper', yref='y', x0=0, x1=1, y0=media_rgp, y1=media_rgp,line=dict(color='red', dash='dash'), name='Média')

        # Definir layout
    fig_rgp.update_layout(xaxis_title='', yaxis_title='RGP', showlegend=False)

        # Exibir gráfico
    st.plotly_chart(fig_rgp, use_container_width=True)
    