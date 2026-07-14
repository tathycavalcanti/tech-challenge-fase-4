import streamlit as st
import pickle
import pandas as pd
import numpy as np

# 1. CONFIGURAÇÃO DA PÁGINA E TEMA ESCURO (Estilo FIAP)
st.set_page_config(
    page_title="Triagem Inteligente - Diagnóstico de Obesidade",
    page_icon="🩺",
    layout="wide"
)

# Estilização CSS personalizada com a paleta FIAP (Preto, Branco e Magenta/Rosa)
st.markdown("""
    <style>
    /* Fundo da tela principal */
    .stApp {
        background-color: #0B0B0C;
        color: #FFFFFF;
    }
    
    /* Título Principal */
    h1 {
        color: #ED145B !important; /* Rosa/Magenta FIAP */
        font-weight: 800 !important;
    }
    
    /* Subtítulos e textos */
    h3, h5, p, label, .stMarkdown {
        color: #F8F9FA !important;
    }
    
    /* Caixas de seleção e Inputs */
    .stSelectbox div[data-baseweb="select"], .stNumberInput div[data-baseweb="input"] {
        background-color: #1A1A1C !important;
        color: #FFFFFF !important;
        border: 1px solid #333336 !important;
    }
    
    /* Textos dentro dos inputs */
    input, div[role="listbox"] {
        color: #FFFFFF !important;
    }

    /* Botão de Avançar/Calcular (Estilo FIAP Magenta) */
    div.stButton > button:first-child {
        background-color: #ED145B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: bold !important;
        width: 100% !important;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #C10D46 !important;
    }

    /* Botão de Voltar (Cinza Escuro) */
    div.stButton > button[key*="voltar"] {
        background-color: #2D2D30 !important;
        color: #FFFFFF !important;
        border: 1px solid #434348 !important;
    }
    div.stButton > button[key*="voltar"]:hover {
        background-color: #434348 !important;
    }
    
    /* Esconder marca d'água do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. CONTROLE DE ESTADO DA NAVEGAÇÃO (Session State)
if 'etapa' not in st.session_state:
    st.session_state.etapa = 1

# Inicializar os dados do formulário na memória se não existirem
valores_padrao = {
    'gender': "Feminino", 'age': 25, 'height': 1.70, 'weight': 70.0,
    'favc': "Não", 'fcvc': "Às vezes", 'ncp': "3 refeições",
    'caec': "Às vezes", 'ch2o': "Entre 1 e 2 litros", 'scc': "Não",
    'faf': "1 a 2 dias por semana", 'tue': "Moderado (2h a 4h)",
    'family_history': "Não", 'calc': "Às vezes", 'smoke': "Não",
    'mtrans': "Transporte Público"
}

for chave, valor in valores_padrao.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor

# 3. CARREGANDO O MODELO DO GITHUB
@st.cache_resource
def carregar_modelo():
    try:
        with open('modelo_obesidade.pkl', 'rb') as f:
            artefatos = pickle.load(f)
        return artefatos['modelo'], artefatos['colunas_treino']
    except FileNotFoundError:
        st.error("⚠️ Erro: O arquivo 'modelo_obesidade.pkl' não foi encontrado. Verifique os arquivos do repositório.")
        return None, None

modelo, colunas_treino = carregar_modelo()

# 4. TÍTULO DO PROJETO
st.title("🩺 Painel de Triagem Inteligente")
st.write("Medicina Preventiva e Diagnóstico Auxiliado por Inteligência Artificial.")

# Barra de Progresso Visual
progresso = {1: 33, 2: 66, 3: 100}
st.progress(progresso[st.session_state.etapa] / 100)
st.markdown(f"**Etapa {st.session_state.etapa} de 3**")
st.markdown("---")

if modelo is not None:
    
    # ==========================================
    # ETAPA 1: DADOS BIOMÉTRICOS
    # ==========================================
    if st.session_state.etapa == 1:
        st.subheader("📋 Etapa 1: Informações Físicas Básicas")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.gender = st.selectbox("Gênero biológico do paciente:", ["Feminino", "Masculino"], index=["Feminino", "Masculino"].index(st.session_state.gender))
            st.session_state.age = st.number_input("Idade (anos):", min_value=14, max_value=100, value=st.session_state.age, step=1)
        with col2:
            st.session_state.height = st.number_input("Altura (metros):", min_value=1.00, max_value=2.50, value=st.session_state.height, step=0.01, format="%.2f")
            st.session_state.weight = st.number_input("Peso (kg):", min_value=30.0, max_value=250.0, value=st.session_state.weight, step=0.1, format="%.1f")

        st.markdown("<br>", unsafe_allow_html=True)
        col_vazio, col_btn = st.columns([4, 1])
        with col_btn:
            if st.button("Continuar ➡️", key="btn_cont_1"):
                st.session_state.etapa = 2
                st.rerun()

    # ==========================================
    # ETAPA 2: ROTINA ALIMENTAR
    # ==========================================
    elif st.session_state.etapa == 2:
        st.subheader("🥗 Etapa 2: Comportamento e Hábitos de Consumo")
        col3, col4 = st.columns(2)
        with col3:
            st.session_state.favc = st.selectbox("Consome alimentos calóricos (fast food, frituras) com frequência?", ["Sim", "Não"], index=["Sim", "Não"].index(st.session_state.favc))
            st.session_state.fcvc = st.selectbox("Com que frequência consome vegetais/legumes nas refeições principais?", ["Nunca", "Às vezes", "Sempre"], index=["Nunca", "Às vezes", "Sempre"].index(st.session_state.fcvc))
            st.session_state.ncp = st.selectbox("Quantas refeições principais realiza por dia?", ["1 a 2 refeições", "3 refeições", "Mais de 3 refeições"], index=["1 a 2 refeições", "3 refeições", "Mais de 3 refeições"].index(st.session_state.ncp))
        with col4:
            st.session_state.caec = st.selectbox("Costuma comer alimentos extras entre as refeições?", ["Não", "Às vezes", "Frequentemente", "Sempre"], index=["Não", "Às vezes", "Frequentemente", "Sempre"].index(st.session_state.caec))
            st.session_state.ch2o = st.selectbox("Qual a média diária de consumo de água?", ["Menos de 1 litro", "Entre 1 e 2 litros", "Mais de 2 litros"], index=["Menos de 1 litro", "Entre 1 e 2 litros", "Mais de 2 litros"].index(st.session_state.ch2o))
            st.session_state.scc = st.selectbox("Monitora ou conta as calorias diárias consumidas?", ["Sim", "Não"], index=["Sim", "Não"].index(st.session_state.scc))

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn_voltar, col_vazio, col_btn_avancar = st.columns([1, 3, 1])
        with col_btn_voltar:
            if st.button("⬅️ Voltar", key="btn_voltar_1"):
                st.session_state.etapa = 1
                st.rerun()
        with col_btn_avancar:
            if st.button("Continuar ➡️", key="btn_cont_2"):
                st.session_state.etapa = 3
                st.rerun()

    # ==========================================
    # ETAPA 3: ESTILO DE VIDA E CÁLCULO
    # ==========================================
    elif st.session_state.etapa == 3:
        st.subheader("🏃‍♂️ Etapa 3: Atividade Física, Tecnologia e Histórico")
        col5, col6 = st.columns(2)
        with col5:
            st.session_state.faf = st.selectbox("Com que frequência pratica atividades físicas?", ["Não pratica (Sedentário)", "1 a 2 dias por semana", "3 a 4 dias por semana", "5 ou mais dias por semana"], index=["Não pratica (Sedentário)", "1 a 2 dias por semana", "3 a 4 dias por semana", "5 ou mais dias por semana"].index(st.session_state.faf))
            st.session_state.tue = st.selectbox("Quantas horas diárias passa utilizando telas (celular, TV, computador)?", ["Baixo (Menos de 2h)", "Moderado (2h a 4h)", "Alto (Mais de 4h)"], index=["Baixo (Menos de 2h)", "Moderado (2h a 4h)", "Alto (Mais de 4h)"].index(st.session_state.tue))
            st.session_state.family_history = st.selectbox("Histórico familiar de sobrepeso ou obesidade direta?", ["Sim", "Não"], index=["Sim", "Não"].index(st.session_state.family_history))
        with col6:
            st.session_state.calc = st.selectbox("Com que frequência consome bebidas alcoólicas?", ["Não consome", "Às vezes", "Frequentemente", "Sempre"], index=["Não consome", "Às vezes", "Frequentemente", "Sempre"].index(st.session_state.calc))
            st.session_state.smoke = st.selectbox("O paciente fuma?", ["Sim", "Não"], index=["Sim", "Não"].index(st.session_state.smoke))
            st.session_state.mtrans = st.selectbox("Meio de transporte principal no dia a dia:", ["Transporte Público", "Automóvel Próprio", "Motocicleta", "Bicicleta", "Caminhada"], index=["Transporte Público", "Automóvel Próprio", "Motocicleta", "Bicicleta", "Caminhada"].index(st.session_state.mtrans))

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn_voltar, col_vazio, col_btn_calcular = st.columns([1, 2.5, 1.5])
        
        with col_btn_voltar:
            if st.button("⬅️ Voltar", key="btn_voltar_2"):
                st.session_state.etapa = 2
                st.rerun()
                
        with col_btn_calcular:
            processar_calculo = st.button("🚀 Calcular Diagnóstico Clínico", key="btn_calcular")

        # Se o médico apertar para calcular o diagnóstico
        if processar_calculo:
            # Mapeamento dos inputs guardados na memória
            map_sim_nao = {"Sim": 1, "Não": 0}
            map_gender = {"Feminino": 0, "Masculino": 1}
            map_fcvc = {"Nunca": 1.0, "Às vezes": 2.0, "Sempre": 3.0}
            map_ncp = {"1 a 2 refeições": 1.0, "3 refeições": 3.0, "Mais de 3 refeições": 4.0}
            map_caec = {"Não": 0, "Às vezes": 1, "Frequentemente": 2, "Sempre": 3}
            map_ch2o = {"Menos de 1 litro": 1.0, "Entre 1 e 2 litros": 2.0, "Mais de 2 litros": 3.0}
            map_faf = {"Não pratica (Sedentário)": 0.0, "1 a 2 dias por semana": 1.0, "3 a 4 dias por semana": 2.0, "5 ou mais dias por semana": 3.0}
            map_tue = {"Baixo (Menos de 2h)": 0.0, "Moderado (2h a 4h)": 1.0, "Alto (Mais de 4h)": 2.0}
            map_calc = {"Não consome": 0, "Às vezes": 1, "Frequentemente": 2, "Sempre": 3}

            mtrans_public = 1 if st.session_state.mtrans == "Transporte Público" else 0
            mtrans_walking = 1 if st.session_state.mtrans == "Caminhada" else 0
            mtrans_motorbike = 1 if st.session_state.mtrans == "Motocicleta" else 0
            mtrans_bike = 1 if st.session_state.mtrans == "Bicicleta" else 0

            dados_paciente = {
                'Gender': map_gender[st.session_state.gender],
                'Age': st.session_state.age,
                'Height': st.session_state.height,
                'Weight': st.session_state.weight,
                'family_history': map_sim_nao[st.session_state.family_history],
                'FAVC': map_sim_nao[st.session_state.favc],
                'FCVC': map_fcvc[st.session_state.fcvc],
                'NCP': map_ncp[st.session_state.ncp],
                'CAEC': map_caec[st.session_state.caec],
                'SMOKE': map_sim_nao[st.session_state.smoke],
                'CH2O': map_ch2o[st.session_state.ch2o],
                'SCC': map_sim_nao[st.session_state.scc],
                'FAF': map_faf[st.session_state.faf],
                'TUE': map_tue[st.session_state.tue],
                'CALC': map_calc[st.session_state.calc],
                'MTRANS_Public_Transportation': mtrans_public,
                'MTRANS_Walking': mtrans_walking,
                'MTRANS_Motorbike': mtrans_motorbike,
                'MTRANS_Bike': mtrans_bike
            }

            input_df = pd.DataFrame([dados_paciente])
            input_df = input_df[colunas_treino]

            probabilidades = modelo.predict_proba(input_df)[0]
            predicao = modelo.predict(input_df)[0]
            confianca = max(probabilidades) * 100

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

            st.markdown("---")
            st.subheader("📋 Laudo de Triagem")
            
            # Alertas estilizados para combinar com o fundo escuro
            if status == 'success':
                st.success(f"**Resultado:** {resultado_texto} (Confiança: {confianca:.2f}%)")
            elif status == 'warning':
                st.warning(f"**Resultado:** {resultado_texto} (Confiança: {confianca:.2f}%)")
            else:
                st.error(f"**Resultado:** {resultado_texto} (Confiança: {confianca:.2f}%)")

            st.write(orientacao)
            
            # GRAFICO LIMPO E PERSONALIZADO (Estilo FIAP)
            st.markdown("##### Probabilidades por Categoria:")
            classes_nomes = [dicionario_classes[c][0] for c in modelo.classes_]
            
            # Criando o dataframe para o plot
            chart_data = pd.DataFrame({
                'Categoria': classes_nomes,
                'Probabilidade (%)': np.round(probabilidades * 100, 1)
            }).sort_values(by='Probabilidade (%)', ascending=True)

            # Criando o gráfico direto via Matplotlib para controle cirúrgico dos elementos visuais
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 4.5))
            fig.patch.set_facecolor('#0B0B0C') # Cor de fundo da figura igual à do Streamlit
            ax.set_facecolor('#0B0B0C')

            cores_barras = ['#ED145B' if cat == resultado_texto else '#2D2D30' for cat in chart_data['Categoria']]
            
            barras = ax.barh(chart_data['Categoria'], chart_data['Probabilidade (%)'], color=cores_barras, edgecolor='none', height=0.6)
            
            # Adicionando os rótulos de % ao lado de cada barra
            for barra in barras:
                width = barra.get_width()
                if width > 1.0:
                    ax.text(width + 1.0, barra.get_y() + barra.get_height()/2, f'{width:.1f}%', 
                            va='center', ha='left', color='#FFFFFF', fontweight='bold', fontsize=9)

            # Limpando a grade, bordas e títulos indesejados
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.get_xaxis().set_visible(False) # Esconde o eixo X e suas linhas de grade
            ax.tick_params(axis='y', colors='#FFFFFF', labelsize=10, length=0) # Mantém apenas os rótulos do Y brancos, sem traços de marcação

            plt.tight_layout()
            st.pyplot(fig)
