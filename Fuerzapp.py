###########################################################################################################################
# fuerzaapp.py
###########################################################################################################################
# Necesidades:
# Presentar app tipo webapp con contendido de lo aprendido en pythom y bases de datos.
# Caracteristicas:
# Uso de streamlit como interprete para creacion de app, manejo de HTML / CSS
# Uso de Sqlite sistema de base de datos emebebido para uso de bbd.
# Uso de sesiones mediante archivo
#######################################################
####################################################### Carga basica de sitio
#######################################################
# 🖥️  Importo libreria de Interfaz en Streamlit
import streamlit as st
# Importo libreria Base de datos PostgreSQL
import psycopg2
# Importo libreria cifrar contraseñas
import hashlib
# Importo comandos OS
import os
# Importo sistema de ca
import pandas as pd
# Importo libreria para manejo de fechas
from datetime import date

# --- Configuración de página ---
st.set_page_config(page_title="FuerzApp", page_icon="💪", layout="wide")
# --- Funcion de graficas
import plotly.express as px

###########################################################################################################################
# Back End
###########################################################################################################################
#######################################################
####################################################### Funciones de Usuario
#######################################################
# Funciones auxiliares
def get_connection():
    """
    Establece y devuelve una conexión a la base de datos PostgreSQL.
    Las credenciales se obtienen de st.secrets para mayor seguridad.
    """
    try:
        conn = psycopg2.connect(st.secrets["db_connection_string"])
        print("[DEBUG] Conexión a la base de datos PostgreSQL establecida.")
        return conn
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        st.stop() # Detiene la ejecución de la app si no se puede conectar

# Función para convertir una contraseña en un hash irreversible, para no guardar texto plano. Usa SHA-256.
def hash_password(password):
    """
    Convierte una contraseña en un hash SHA-256.
    """
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return hashed

# Validar login (Consulta en la base si existe un usuario con ese mail y contraseña cifrada.)
def validar_usuario(email, password):
    """
    Valida un usuario consultando en la base de datos si existe con el email y contraseña hasheada.
    """
    print(f"[DEBUG] Validando usuario: {email}")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, email, contraseña, foto FROM usuarios WHERE email = %s AND contraseña = %s", (email, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    print(f"[DEBUG] Usuario encontrado: {user}")
    return user

# Registrar nuevo usuario (Registra un nuevo usuario. Si el email ya existe, devuelve False. Guarda la contraseña cifrada.)
def registrar_usuario(nombre, email, password):
    """
    Registra un nuevo usuario en la base de datos.
    Devuelve True si el registro es exitoso, False si el email ya existe o hay otro error.
    """
    print(f"[DEBUG] Registrando usuario: {nombre}, {email}")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Insertar usuario con foto por defecto (None)
        cursor.execute("INSERT INTO usuarios (nombre, email, contraseña, foto) VALUES (%s, %s, %s, %s)", (nombre, email, hash_password(password), None))
        conn.commit()
        conn.close()
        print("[DEBUG] Registro exitoso")
        return True
    except psycopg2.IntegrityError as e:
        # Error de integridad ocurre si el email ya existe (UNIQUE NOT NULL)
        st.error("El email ya está registrado. Por favor, usá otro o iniciá sesión.")
        print(f"[ERROR] Registro fallido: {e}")
        return False
    except Exception as e:
        st.error(f"Error al registrar usuario: {e}")
        print(f"[ERROR] Registro fallido: {e}")
        return False

#######################################################
####################################################### Funciones de Sesiones (simplificadas con st.session_state)
#######################################################
# La gestión de sesiones con archivo (sesion.json) se elimina.
# Streamlit maneja el estado de la sesión en memoria con st.session_state.
# La persistencia del usuario logueado se basa en que el usuario inicie sesión
# contra la base de datos persistente (Supabase) cada vez que la app se recargue.

# --- Estado de sesión ---
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# Si el usuario no está logueado en la sesión actual, muestra el login/registro
if st.session_state.usuario is None:
    #######################################################
    ####################################################### Avatares (adaptado para la ruta en el repo)
    #######################################################
    # Avatares predeterminados
    AVATAR_OPCIONES = {
        "Avatar 1": "perfiles/avatar1.png",
        "Avatar 2": "perfiles/avatar2.png",
        "Avatar 3": "perfiles/avatar3.png"
    }

    # Asegurar carpeta para fotos (esto solo es relevante localmente, en Streamlit Cloud es efímero)
    os.makedirs("perfiles", exist_ok=True)

    #######################################################
    ####################################################### Diseño de sitio (aplicar tema)
    #######################################################
    def aplicar_tema(tema):
        """
        Aplica estilos CSS para cambiar el tema de la aplicación.
        """
        if tema == "Oscuro":
            st.markdown("""
                <style>
                    body,header,button {
                        background-color: #121212!important;
                        color: #ffffff!important;
                    }
                    .stApp {
                        background-color: #121212!important;
                    }
                    h1, h2, h3, h4, h5, h6, p {
                        color: #ffffff!important;
                    }
                    .stSidebar, .css-1d391kg {
                        background-color: #1f1f1f !important;
                    }
                    div.stButton > button {
                        width: 100%;
                        height: 3rem;
                        font-size: 1.1rem;
                        margin-bottom: 8px;
                        color: #ffffff!important;
                    }
                </style>
            """, unsafe_allow_html=True)
        elif tema == "Claro":
            st.markdown("""
                <style>
                    body,header,button {
                        background-color: #f5f5f5!important;
                        color: #000000!important;
                    }
                    .stApp {
                        background-color: #f5f5f5!important;
                    }
                    h1, h2, h3, h4, h5, h6, p {
                        color: #000000!important;
                    }
                    .stSidebar, .css-1d391kg {
                        background-color: #e0e0e0 !important;
                    }
                    div.stButton > button {
                        width: 100%;
                        height: 3rem;
                        font-size: 1.1rem;
                        margin-bottom: 8px;
                    }
                </style>
            """, unsafe_allow_html=True)

    # --- sesión tema
    if "tema" not in st.session_state:
        st.session_state.tema = "Claro"

    # Selector de tema
    tema = st.sidebar.selectbox("Selecciona un tema", ["Oscuro", "Claro"])
    aplicar_tema(tema)


    st.title("FuerzApp - Iniciar sesión o registrarse")
    opcion = st.radio("Seleccioná una opción", ["Iniciar sesión", "Registrarse"])

    if opcion == "Iniciar sesión":
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            user = validar_usuario(email, password)
            if user:
                st.success(f"Bienvenido/a {user[1]}")
                st.session_state.usuario = user
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    elif opcion == "Registrarse":
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")

        st.markdown("### Elegí tu avatar")
        avatar_seleccionado = st.selectbox("Seleccioná un avatar", list(AVATAR_OPCIONES.keys()))
        avatar_url = AVATAR_OPCIONES[avatar_seleccionado]

        imagen_subida = st.file_uploader("O subí tu propia foto (opcional)", type=["png", "jpg", "jpeg"])
        if st.button("Registrarme"):
            if registrar_usuario(nombre, email, password):
                # Advertencia: Las imágenes subidas a la carpeta 'perfiles/' en Streamlit Cloud
                # NO son persistentes entre reinicios de la aplicación.
                # Para persistencia real, se necesitaría un servicio de almacenamiento en la nube
                # como Supabase Storage, AWS S3, Google Cloud Storage, etc.
                if imagen_subida:
                    # Guarda la imagen temporalmente en el sistema de archivos del contenedor de Streamlit Cloud
                    # Esto se perderá si la app se reinicia.
                    ruta_imagen_temporal = f"perfiles/{email}_uploaded.png"
                    with open(ruta_imagen_temporal, "wb") as f:
                        f.write(imagen_subida.read())
                    avatar_url = ruta_imagen_temporal
                    st.warning("¡Atención! La foto subida no será persistente en la nube. Se perderá al reiniciar la aplicación.")
                else:
                    avatar_url = AVATAR_OPCIONES[avatar_seleccionado]

                # Guardar la ruta de la foto en la base de datos
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE usuarios SET foto = %s WHERE email = %s", (avatar_url, email))
                conn.commit()
                conn.close()

                print(f"[DEBUG] Avatar guardado en DB: {avatar_url}")
                st.success("Registro exitoso. ¡Ahora iniciá sesión!")

    st.stop() # Detiene la ejecución si el usuario no está logueado

#######################################################
####################################################### # --- Panel logueo
#######################################################
# --- Usuario logueado ---
usuario = st.session_state.usuario
usuario_id = usuario[0]
nombre = usuario[1]
# Asegurarse de que el índice 4 exista antes de intentar acceder a él
foto = usuario[4] if len(usuario) > 4 and usuario[4] else None
print(f"[DEBUG] Foto cargada del usuario logueado: {foto}")

with st.sidebar:
    col1, col2 = st.columns(2)
    with col1:
        # Verifica si la foto existe y es un archivo local antes de intentar mostrarla
        if foto and os.path.exists(foto):
            st.image(foto, width=100)
        elif foto and foto.startswith("perfiles/avatar"): # Si es un avatar predeterminado
            st.image(foto, width=100)
        else:
            st.info("Sin foto de perfil")
    with col2:
        st.markdown(f"**Bienvenido/a, {nombre}**")
        if st.button("Cerrar sesión"):
            st.session_state.usuario = None
            st.rerun()


#Crea un bloque desplegable en el panel lateral para cambiar la imagen.
#######################################################
####################################################### # --- Cambio perfil
#######################################################
with st.sidebar.expander("Cambiar foto de perfil"):
    st.markdown("**Elegí un nuevo avatar o subí tu foto personalizada**")
    # Selección de avatar
    nuevo_avatar = st.selectbox("Selecciona...", list(AVATAR_OPCIONES.keys()))
    # Mostrar previsualización del avatar seleccionado
    st.image(AVATAR_OPCIONES[nuevo_avatar], width=50)

    # Subida opcional de imagen personalizada
    nueva_imagen = st.file_uploader("O subí una nueva foto", type=["png", "jpg", "jpeg"])

    # Botón para actualizar
    if st.button("Actualizar foto"):
        nueva_ruta = None

        if nueva_imagen:
            # Advertencia: Las imágenes subidas a la carpeta 'perfiles/' en Streamlit Cloud
            # NO son persistentes entre reinicios de la aplicación.
            # Para persistencia real, se necesitaría un servicio de almacenamiento en la nube
            # como Supabase Storage, AWS S3, Google Cloud Storage, etc.
            os.makedirs("perfiles", exist_ok=True)
            nueva_ruta = f"perfiles/{usuario[2]}_updated.png"  # usuario[2] es el email
            with open(nueva_ruta, "wb") as f:
                f.write(nueva_imagen.read())
            st.warning("¡Atención! La foto subida no será persistente en la nube. Se perderá al reiniciar la aplicación.")
        else:
            nueva_ruta = AVATAR_OPCIONES[nuevo_avatar]

        # Guardar nueva ruta de imagen en la base de datos
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET foto = %s WHERE id = %s", (nueva_ruta, usuario_id))
        conn.commit()
        conn.close()

        # Mensaje y actualización en sesión
        st.success("Foto actualizada correctamente.")
        # Actualiza la sesión con la nueva ruta de la foto
        st.session_state.usuario = (usuario[0], usuario[1], usuario[2], usuario[3], nueva_ruta)
        st.rerun()

# Muestra el título, el menú lateral y guarda el ID del usuario logueado (columna 0 de la tabla usuarios).
#######################################################
####################################################### # --- Menú principal ---
#######################################################

st.title("📊 FuerzApp - Seguimiento de Entrenamientos y Dietas")

if st.sidebar.button("🏠 Inicio"):
    st.session_state.menu = "Inicio"
if st.sidebar.button("💪 Entrenamiento"):
    st.session_state.menu = "Registrar Entrenamiento"
if st.sidebar.button("🍽️ Comida"):
    st.session_state.menu = "Registrar Comida"
if st.sidebar.button("📏 Medidas"):
    st.session_state.menu = "Registrar Medidas"
if st.sidebar.button("📊 Reportes"):
    st.session_state.menu = "Reportes"
# Luego mostrar la sección según st.session_state.menu
menu = st.session_state.get("menu", "Inicio")

#######################################################
####################################################### # Selector de tema (ya se aplica al inicio si no hay usuario)
#######################################################
# Si el usuario ya está logueado, el selector de tema se muestra en el sidebar
if st.session_state.usuario:
    # Selector de tema
    tema = st.sidebar.selectbox("Selecciona un tema", ["Oscuro", "Claro"])
    # Aplicar tema
    aplicar_tema(tema)


#######################################################
####################################################### # --- Resumen general ---
#######################################################

if menu == "Inicio":
    st.subheader("Resumen general")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Últimos entrenamientos")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, tipo, duracion, calorias, notas
            FROM entrenamientos
            WHERE usuario_id = %s
            ORDER BY fecha DESC
            LIMIT 5
        """, (usuario_id,))
        entrenamientos = cursor.fetchall()
        conn.close()

        if entrenamientos:
            df = pd.DataFrame(entrenamientos, columns=["Fecha", "Tipo", "Duración (min)", "Calorías", "Notas"])
            st.dataframe(df.reset_index(drop=True), use_container_width=True)
        else:
            st.info("Aún no registraste entrenamientos.")

    with col2:
        st.subheader("Últimos alimentos")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, tipo_comida, alimento, calorias, notas
            FROM comidas
            WHERE usuario_id = %s
            ORDER BY fecha DESC
            LIMIT 5
        """, (usuario_id,))
        comidas = cursor.fetchall()
        conn.close()

        if comidas:
            df = pd.DataFrame(comidas, columns=["Fecha", "Tipo", "Alimento", "Calorías", "Notas"])
            st.dataframe(df.reset_index(drop=True), use_container_width=True)
        else:
            st.info("Aún no registraste alimentos.")
    st.subheader("Últimas medidas")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, abdomen, cintura, brazo, pecho, pierna, peso, notas
        FROM medidas
        WHERE usuario_id = %s
        ORDER BY fecha DESC
        LIMIT 5
    """, (usuario_id,))
    medidas = cursor.fetchall()
    conn.close()

    if medidas:
        df = pd.DataFrame(medidas, columns=["Fecha", "Abdomen (cm)", "Cintura (cm)", "Brazo (cm)", "Pecho (cm)", "Pierna (cm)", "Peso (kg)", "Notas"])
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
    else:
        st.info("Aún no registraste medidas.")
#######################################################
####################################################### # --- Registro entrenamiento ---
#######################################################

elif menu == "Registrar Entrenamiento":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💪 Registrar nuevo entrenamiento")
        with st.form("form_entrenamiento"):
            fecha = st.date_input("Fecha", value=date.today()) # Valor por defecto a la fecha actual
            tipo = st.selectbox("Tipo de entrenamiento", ["Fuerza", "Cardio", "Funcional", "Movilidad", "Otro"])
            duracion = st.number_input("Duración (minutos)", min_value=0, step=5)
            calorias = st.number_input("Calorías estimadas", min_value=0, step=10)
            notas = st.text_area("Notas adicionales (opcional)")
            enviar = st.form_submit_button("Guardar entrenamiento")
            if enviar:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO entrenamientos (usuario_id, fecha, tipo, duracion, calorias, notas)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (usuario_id, fecha, tipo, duracion, calorias, notas))
                conn.commit()
                conn.close()
                st.success("✅ Entrenamiento registrado correctamente.")

    with col2:
        st.subheader("🕒 Últimos entrenamientos")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, tipo, duracion, calorias, notas
            FROM entrenamientos
            WHERE usuario_id = %s
            ORDER BY fecha DESC
            LIMIT 5
        """, (usuario_id,))
        entrenamientos = cursor.fetchall()
        conn.close()

        if entrenamientos:
            df = pd.DataFrame(entrenamientos, columns=["Fecha", "Tipo", "Duración (min)", "Calorías", "Notas"])
            st.dataframe(df.reset_index(drop=True), use_container_width=True)
        else:
            st.info("Aún no registraste entrenamientos.")


#######################################################
####################################################### # --- Registro comida---
#######################################################

elif menu == "Registrar Comida":
    st.subheader("Nueva comida")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(" Registrar nuevo alimento")
        with st.form("form_comidas"):
            fecha = st.date_input("Fecha", value=date.today())
            tipo_comida = st.selectbox("Tipo de alimento", ["Carnes, pescados y huevos", "Fruta y Verdura", "Cereales y derivados", "Lacteos y derivados", "Legumbres", "Grasas y aceites", "Otro"])
            alimento = st.text_input("Alimento")
            calorias = st.number_input("Calorías estimadas", min_value=0, step=10)
            notas = st.text_area("Notas adicionales (opcional)")
            enviar2 = st.form_submit_button("Guardar alimento")
            if enviar2:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO comidas (usuario_id, fecha, tipo_comida, alimento, calorias, notas)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (usuario_id, fecha, tipo_comida, alimento, calorias, notas))
                conn.commit()
                conn.close()
                st.success("✅ Alimento registrado correctamente.")

    with col2:
        st.subheader("🕒 Últimos alimentos")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, tipo_comida, alimento, calorias, notas
            FROM comidas
            WHERE usuario_id = %s
            ORDER BY fecha DESC
            LIMIT 5
        """, (usuario_id,))
        comidas = cursor.fetchall()
        conn.close()

        if comidas:
            df = pd.DataFrame(comidas, columns=["Fecha", "Tipo", "Alimento", "Calorías", "Notas"])
            st.dataframe(df.reset_index(drop=True), use_container_width=True)
        else:
            st.info("Aún no registraste alimentos.")


#######################################################
####################################################### # --- Registro Medidas ---
#######################################################

elif menu == "Registrar Medidas":
    st.subheader("Nueva Medida")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(" Registrar nueva medida")
        with st.form("form_medidas"):
            fecha = st.date_input("Fecha", value=date.today())
            abdomen = st.number_input("Abdomen (cm)", min_value=40.0, max_value=200.0, value=80.0, step=0.5)
            cintura = st.number_input("Cintura (cm)", min_value=30.0, max_value=180.0, value=75.0, step=0.5)
            pecho = st.number_input("Pecho (cm)", min_value=60.0, max_value=220.0, value=100.0, step=0.5)
            brazo = st.number_input("Brazo (cm)", min_value=15.0, max_value=80.0, value=30.0, step=0.1)
            pierna = st.number_input("Pierna (cm)", min_value=30.0, max_value=120.0, value=55.0, step=0.1)
            peso = st.number_input("Peso (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.1)
            notas = st.text_area("Notas adicionales (opcional)")
            enviar = st.form_submit_button("Guardar medidas")
            if enviar:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO medidas (usuario_id, fecha, abdomen, cintura, brazo, pecho, pierna, peso, notas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (usuario_id, fecha, abdomen, cintura, brazo, pecho, pierna, peso, notas))
                conn.commit()
                conn.close()
                st.success("✅ Medidas registradas.")

    with col2:
        st.subheader("🕒 Últimas medidas")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, abdomen, cintura, brazo, pecho, pierna, peso, notas
            FROM medidas
            WHERE usuario_id = %s
            ORDER BY fecha DESC
            LIMIT 5
        """, (usuario_id,))
        medidas = cursor.fetchall()
        conn.close()

        if medidas:
            df = pd.DataFrame(medidas, columns=["Fecha", "Abdomen (cm)", "Cintura (cm)", "Brazo (cm)", "Pecho (cm)", "Pierna (cm)", "Peso (kg)", "Notas"])
            st.dataframe(df.reset_index(drop=True), use_container_width=True)
        else:
            st.info("Aún no registraste medidas.")

#######################################################
####################################################### # --- Registro Reportes ---
#######################################################

elif menu == "Reportes":
    st.subheader("Reportes y análisis")
    conn = get_connection()
    df_comidas = pd.read_sql_query("""
        SELECT fecha, tipo_comida, calorias FROM comidas
        WHERE usuario_id = %s
        ORDER BY fecha
    """, conn, params=(usuario_id,))
    conn.close()

    if not df_comidas.empty:
        df_comidas['fecha'] = pd.to_datetime(df_comidas['fecha'])

        st.markdown("### Calorías por tipo de comida")
        fig_comidas = px.pie(df_comidas, names="tipo_comida", values="calorias")
        st.plotly_chart(fig_comidas, use_container_width=True)
    else:
        st.info("No hay datos de comidas para graficar.")

    conn = get_connection() # Nueva conexión para entrenamientos
    df_entrenamiento = pd.read_sql_query("""
        SELECT fecha, tipo, duracion, calorias FROM entrenamientos
        WHERE usuario_id = %s
        ORDER BY fecha
    """, conn, params=(usuario_id,))
    conn.close()

    if not df_entrenamiento.empty:
        df_entrenamiento['fecha'] = pd.to_datetime(df_entrenamiento['fecha'])

        st.markdown("### Evolución de duración de entrenamientos")
        fig_dur = px.line(df_entrenamiento, x="fecha", y="duracion", color="tipo", markers=True)
        st.plotly_chart(fig_dur, use_container_width=True)

        st.markdown("### Calorías quemadas por día")
        fig_cal = px.bar(df_entrenamiento, x="fecha", y="calorias", color="tipo")
        st.plotly_chart(fig_cal, use_container_width=True)
    else:
        st.info("No hay datos de entrenamiento para graficar.")

    conn = get_connection() # Nueva conexión para medidas
    df_medidas = pd.read_sql_query("""
        SELECT fecha, abdomen, cintura, pecho, brazo, pierna, peso FROM medidas
        WHERE usuario_id = %s
        ORDER BY fecha
    """, conn, params=(usuario_id,))
    conn.close()

    if not df_medidas.empty:
        df_medidas['fecha'] = pd.to_datetime(df_medidas['fecha'])

        st.markdown("### Evolución corporal")
        for columna in ["abdomen", "cintura", "pecho", "brazo", "pierna", "peso"]:
            fig = px.line(df_medidas, x="fecha", y=columna, title=f"Evolución de {columna.capitalize()}")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de medidas para mostrar.")
