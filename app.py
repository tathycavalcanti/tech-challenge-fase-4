import streamlit as st
import pickle
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA (Aparência Hospitalar)
st.set_page_config(
    page_title="Triagem Inteligente - Diagnóstico de Obesidade",
    page_icon="🩺",
    layout="wide"
)

# Estilização básica para o visual clínico
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 8px; width: 100%; }
    .stButton>button:hover { background-color: #0056b3; }
    h1 { color: #1e293b; }
    h3 { color: #0f172a; }
    </style>
""", unsafe_allow_html=True)

# 2. CARREGANDO O MODELO CAMPEÃO (LightGBM)
@st.cache_resource
def carregar_modelo():
    try:
        with open('modelo_obesidade.pkl', 'rb') as f:
            artefatos = pickle.load(f)
        return artefatos['modelo'], artefatos['colunas_treino']
    except FileNotFoundError:
        st.error("⚠️ Erro: O arquivo 'modelo_obesidade.pkl' não foi encontrado na pasta atual. Certifique-se de exportá-lo no seu notebook primeiro!")
        return None, None

modelo, colunas_treino = carregar_modelo()

# 3. INTERFACE VISUAL
st.title("🩺 Painel de Triagem Inteligente e Medicina Preventiva")
st.write("Insira as métricas físicas e comportamentais do paciente para obter o diagnóstico preditivo em tempo real.")

st.markdown("---")

if modelo is not None:
    # Organizando as perguntas em Abas/Guias para melhorar a usabilidade médica
    tab1, tab2, tab3 = st.tabs(["📊 Dados Biométricos", "🥗 Rotina Alimentar", "🏃‍♂️ Estilo de Vida"])

    with tab1:
        st.subheader("Informações Físicas Básicas")
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gênero biológico do paciente:", ["Feminino", "Masculino"])
            age = st.number_input("Idade (anos):", min_value=14, max_value=100, value=25, step=1)
        with col2:
            height = st.number_input("Altura (metros):", min_value=1.00, max_value=2.50, value=1.70, step=0.01, format="%.2f")
            weight = st.number_input("Peso (kg):", min_value=30.0, max_value=250.0, value=70.0, step=0.1, format="%.1f")

    with tab2:
        st.subheader("Comportamento e Hábitos de Consumo")
        col3, col4 = st.columns(2)
        with col3:
            favc = st.selectbox("Consome alimentos calóricos (fast food, frituras) com frequência?", ["Sim", "Não"])
            fcvc = st.selectbox("Com que frequência consome vegetais/legumes nas refeições principais?", ["Nunca", "Às vezes", "Sempre"])
            ncp = st.selectbox("Quantas refeições principais realiza por dia?", ["1 a 2 refeições", "3 refeições", "Mais de 3 refeições"])
        with col4:
            caec = st.selectbox("Costuma comer alimentos extras entre as refeições?", ["Não", "Às vezes", "Frequentemente", "Sempre"])
            ch2o = st.selectbox("Qual a média diária de consumo de água?", ["Menos de 1 litro", "Entre 1 e 2 litros", "Mais de 2 litros"])
            scc = st.selectbox("Monitora ou conta as calorias diárias consumidas?", ["Sim", "Não"])

    with tab3:
        st.subheader("Atividade Física, Tecnologia e Histórico")
        col5, col6 = st.columns(2)
        with col5:
            faf = st.selectbox("Com que frequência pratica atividades físicas?", ["Não pratica (Sedentário)", "1 a 2 dias por semana", "3 a 4 dias por semana", "5 ou mais dias por semana"])
            tue = st.selectbox("Quantas horas diárias passa utilizando telas (celular, TV, computador)?", ["Baixo (Menos de 2h)", "Moderado (2h a 4h)", "Alto (Mais de 4h)"])
            family_history = st.selectbox("Histórico familiar de sobrepeso ou obesidade direta?", ["Sim", "Não"])
        with col6:
            calc = st.selectbox("Com que frequência consome bebidas alcoólicas?", ["Não consome", "Às vezes", "Frequentemente", "Sempre"])
            smoke = st.selectbox("O paciente fuma?", ["Sim", "Não"])
            mtrans = st.selectbox("Meio de transporte principal no dia a dia:", ["Transporte Público", "Automóvel Próprio", "Motocicleta", "Bicicleta", "Caminhada"])

    st.markdown("---")

    # 4. TRADUÇÃO DAS RESPOSTAS PARA OS VALORES NUMÉRICOS DO MODELO
    # Mapeamentos construídos com base nos padrões do dataset tratado
    map_sim_nao = {"Sim": 1, "Não": 0}
    map_gender = {"Feminino": 0, "Masculino": 1}
    map_fcvc = {"Nunca": 1.0, "Às vezes": 2.0, "Sempre": 3.0}
    map_ncp = {"1 a 2 refeições": 1.0, "3 refeições": 3.0, "Mais de 3 refeições": 4.0}
    map_caec = {"Não": 0, "Às vezes": 1, "Frequentemente": 2, "Sempre": 3}
    map_ch2o = {"Menos de 1 litro": 1.0, "Entre 1 e 2 litros": 2.0, "Mais de 2 litros": 3.0}
    map_faf = {"Não pratica (Sedentário)": 0.0, "1 a 2 dias por semana": 1.0, "3 a 4 dias por semana": 2.0, "5 ou mais dias por semana": 3.0}
    map_tue = {"Baixo (Menos de 2h)": 0.0, "Moderado (2h a 4h)": 1.0, "Alto (Mais de 4h)": 2.0}
    map_calc = {"Não consome": 0, "Às vezes": 1, "Frequentemente": 2, "Sempre": 3}

    # Tratamento dummy para meios de transporte (One-Hot Encoding que o modelo espera)
    mtrans_public = 1 if mtrans == "Transporte Público" else 0
    mtrans_walking = 1 if mtrans == "Caminhada" else 0
    mtrans_motorbike = 1 if mtrans == "Motocicleta" else 0
    mtrans_bike = 1 if mtrans == "Bicicleta" else 0

    # Criando o dicionário com os valores mapeados
    dados_paciente = {
        'Gender': map_gender[gender],
        'Age': age,
        'Height': height,
        'Weight': weight,
        'family_history': map_sim_nao[family_history],
        'FAVC': map_sim_nao[favc],
        'FCVC': map_fcvc[fcvc],
        'NCP': map_ncp[ncp],
        'CAEC': map_caec[caec],
        'SMOKE': map_sim_nao[smoke],
        'CH2O': map_ch2o[ch2o],
        'SCC': map_sim_nao[scc],
        'FAF': map_faf[faf],
        'TUE': map_tue[tue],
        'CALC': map_calc[calc],
        'MTRANS_public_transportation': mtrans_public,
        'MTRANS_walking': mtrans_walking,
        'MTRANS_motorbike': mtrans_motorbike,
        'MTRANS_bike': mtrans_bike
    }

    # Convertendo para DataFrame e garantindo a ordem exata das colunas que o modelo exige
    input_df = pd.DataFrame([dados_paciente])
    input_df = input_df[colunas_treino]

    # Botão de Ação para o diagnóstico
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 Calcular Diagnóstico Clínico"):
            # Realizando a predição probabilística e a predição direta
            probabilidades = modelo.predict_proba(input_df)[0]
            predicao = modelo.predict(input_df)[0]
            confianca = max(probabilidades) * 100

            # Traduzindo a classe predita para o diagnóstico legível
            dicionario_classes = {
                'Insufficient_Weight': ('Baixo Peso', 'warning', '⚠️ O paciente está abaixo do peso ideal. Recomenda-se acompanhamento nutricional.'),
                'Normal_Weight': ('Peso Normal', 'success', '✅ O paciente apresenta peso saudável. Incentive a manutenção dos hábitos atuais.'),
                'Overweight_Level_I': ('Sobrepeso Grau I', 'warning', '⚠️ Atenção: Fase inicial de sobrepeso. Indicado ajustes na rotina de exercícios e alimentação.'),
                'Overweight_Level_II': ('Sobrepeso Grau II', 'warning', '⚠️ Atenção Moderada: Risco aumentado. Recomendado intervenção focada na perda de gordura.'),
                'Obesity_Type_I': ('Obesidade Grau I', 'danger', '🚨 Alerta: Obesidade instalada. Necessário plano de ação médico estruturado.'),
                'Obesity_Type_II': ('Obesidade Grau II (Moderada)', 'danger', '🚨 Alerta Alto: Risco cardiovascular acentuado. Exige intervenção clínica multidisciplinar.'),
                'Obesity_Type_III': ('Obesidade Grau III (Grave)', 'danger', '🚨 Alerta Crítico: Elevado risco à saúde geral do paciente. Requer urgência em consultas e acompanhamento severo.')
            }

            resultado_texto, status, orientacao = dicionario_classes[predicao]

            # Exibindo o resultado em um painel visual destacado
            st.markdown("---")
            st.subheader("📋 Laudo do Modelo Preditivo")
            
            if status == 'success':
                st.success(f"**Resultado:** {resultado_texto} (Confiança da IA: {confianca:.2f}%)")
            elif status == 'warning':
                st.warning(f"**Resultado:** {resultado_texto} (Confiança da IA: {confianca:.2f}%)")
            else:
                st.error(f"**Resultado:** {resultado_texto} (Confiança da IA: {confianca:.2f}%)")

            st.write(orientacao)
            
            # Gráfico rápido de barra lateral mostrando as probabilidades de cada classe
            st.markdown("##### Probabilidades por Categoria de Peso:")
            classes_nomes = [dicionario_classes[c][0] for c in modelo.classes_]
            chart_data = pd.DataFrame({
                'Categoria': classes_nomes,
                'Probabilidade (%)': probabilidades * 100
            }).sort_values(by='Probabilidade (%)', ascending=True)
            
            st.bar_chart(data=chart_data, x='Categoria', y='Probabilidade (%)', horizontal=True, color="#007bff")
