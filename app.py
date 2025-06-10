from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import vapi_service
import datetime
import logging
import os
from dateutil.parser import isoparse

load_dotenv()

# --- CONFIGURACIÓN PRINCIPAL ---
TARGET_ASSISTANT_ID = "7fc144d6-6d36-469f-8fab-da66343e003c"
TARGET_ASSISTANT_NAME = "Tessa - Cialix CS"
# --- FIN DE LA CONFIGURACIÓN ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "a_very_secure_default_secret_key")

# --- I18N & L10N SETUP (No changes here) ---
TRANSLATIONS = {
    'en': {
        'Agente': 'Agent',
        'Dashboard de Llamadas': 'Calls Dashboard',
        'ChatDash Vapi': 'ChatDash Vapi',
        'Dashboard de Agente - Vapi ChatDash': 'Agent Dashboard - Vapi ChatDash',
        'Dashboard de Agente': 'Agent Dashboard',
        'Última Actualización:': 'Last Updated:',
        'ID del Asistente': 'Assistant ID',
        'Nombre': 'Name',
        'Proveedor Modelo': 'Model Provider',
        'Nombre Modelo': 'Model Name',
        'Estado': 'Status',
        'Acciones': 'Actions',
        'Ver Llamadas del Agente': 'View Agent Calls',
        'No se pudo cargar la información del agente.': 'Could not load agent information.',
        'Dashboard de Llamadas:': 'Calls Dashboard:',
        'Períodos Rápidos:': 'Quick Periods:',
        'Hoy': 'Today',
        'Semana': 'Week',
        'Mes': 'Month',
        'Fecha de inicio': 'Start date',
        'Fecha de fin': 'End date',
        'Filtrar': 'Filter',
        'Total de Llamadas': 'Total Calls',
        'Minutos Totales (MM:SS)': 'Total Minutes (MM:SS)',
        'Promedio (MM:SS)': 'Average (MM:SS)',
        'Detalle de Llamadas (Período:': 'Call Details (Period:',
        'ID de Llamada': 'Call ID',
        'Número Cliente': 'Customer Number',
        'Iniciada en': 'Started At',
        'Duración (MM:SS)': 'Duration (MM:SS)',
        'Transcripción': 'Transcript',
        'Ver': 'View',
        'No hay llamadas para mostrar en este período.': 'No calls to display for this period.',
        'Transcripción de la Llamada': 'Call Transcript',
        'Vista Chat': 'Chat View',
        'Texto Plano': 'Plain Text',
        'Cargando...': 'Loading...',
        'Cerrar': 'Close',
        'Detalles del Asistente -': 'Assistant Details -',
        'Detalles del Asistente:': 'Assistant Details:',
        'Volver al Dashboard': 'Back to Dashboard',
        'Error:': 'Error:',
        'No se encontraron datos para este asistente.': 'No data found for this assistant.',
        'Información General': 'General Information',
        'ID del Asistente:': 'Assistant ID:',
        'Nombre:': 'Name:',
        'Creado en:': 'Created At:',
        'Actualizado en:': 'Updated At:',
        'Server Webhook URL:': 'Server Webhook URL:',
        'No configurado': 'Not configured',
        'Server Webhook URL (Backup):': 'Server Webhook URL (Backup):',
        'Configuración del Modelo IA': 'AI Model Configuration',
        'Proveedor:': 'Provider:',
        'Modelo:': 'Model:',
        'Mensajes del Sistema/Prompt:': 'System Messages/Prompt:',
        'Rol:': 'Role:',
        'Herramientas (Tools):': 'Tools:',
        'Tipo:': 'Type:',
        'Descripción:': 'Description:',
        'Parámetros:': 'Parameters:',
        'No hay información de configuración del modelo disponible.': 'No model configuration information available.',
        'Configuración de Voz (TTS)': 'Voice Configuration (TTS)',
        'Proveedor TTS:': 'TTS Provider:',
        'ID de Voz:': 'Voice ID:',
        'No hay información de configuración de voz disponible.': 'No voice configuration information available.',
        'Configuración de Llamada': 'Call Configuration',
        'Primer Mensaje (First Message):': 'First Message:',
        'Transferencia de Destino (Número):': 'Transfer Destination (Number):',
        'Máx. Duración (segundos):': 'Max. Duration (seconds):',
        'Metadata': 'Metadata',
        'Datos JSON Completos del Asistente': 'Full Assistant JSON Data',
        'Última actualización de esta página:': 'Page last updated:',
        'Ocurrió un error al procesar las llamadas.': 'An error occurred while processing calls.',
        'No se pudieron obtener detalles para la llamada {call_id}.': 'Could not get details for call {call_id}.',
        'No se encontró transcripción en los detalles de la llamada {call_id}.': 'Transcript not found in call details for {call_id}.',
        'No se encontró transcripción para esta llamada.': 'No transcript found for this call.',
        'El formato de la transcripción no es compatible.': 'The transcript format is not compatible.',
    },
    'es': {
        'Agente': 'Agente',
        'Dashboard de Llamadas': 'Dashboard de Llamadas',
        'ChatDash Vapi': 'ChatDash Vapi',
        'Dashboard de Agente - Vapi ChatDash': 'Dashboard de Agente - Vapi ChatDash',
        'Dashboard de Agente': 'Dashboard de Agente',
        'Última Actualización:': 'Última Actualización:',
        'ID del Asistente': 'ID del Asistente',
        'Nombre': 'Nombre',
        'Proveedor Modelo': 'Proveedor Modelo',
        'Nombre Modelo': 'Nombre Modelo',
        'Estado': 'Estado',
        'Acciones': 'Acciones',
        'Ver Llamadas del Agente': 'Ver Llamadas del Agente',
        'No se pudo cargar la información del agente.': 'No se pudo cargar la información del agente.',
        'Dashboard de Llamadas:': 'Dashboard de Llamadas:',
        'Períodos Rápidos:': 'Períodos Rápidos:',
        'Hoy': 'Hoy',
        'Semana': 'Semana',
        'Mes': 'Mes',
        'Fecha de inicio': 'Fecha de inicio',
        'Fecha de fin': 'Fecha de fin',
        'Filtrar': 'Filtrar',
        'Total de Llamadas': 'Total de Llamadas',
        'Minutos Totales (MM:SS)': 'Minutos Totales (MM:SS)',
        'Promedio (MM:SS)': 'Promedio (MM:SS)',
        'Detalle de Llamadas (Período:': 'Detalle de Llamadas (Período:',
        'ID de Llamada': 'ID de Llamada',
        'Número Cliente': 'Número Cliente',
        'Iniciada en': 'Iniciada en',
        'Duración (MM:SS)': 'Duración (MM:SS)',
        'Transcripción': 'Transcripción',
        'Ver': 'Ver',
        'No hay llamadas para mostrar en este período.': 'No hay llamadas para mostrar en este período.',
        'Transcripción de la Llamada': 'Transcripción de la Llamada',
        'Vista Chat': 'Vista Chat',
        'Texto Plano': 'Texto Plano',
        'Cargando...': 'Cargando...',
        'Cerrar': 'Cerrar',
        'Detalles del Asistente -': 'Detalles del Asistente -',
        'Detalles del Asistente:': 'Detalles del Asistente:',
        'Volver al Dashboard': 'Volver al Dashboard',
        'Error:': 'Error:',
        'No se encontraron datos para este asistente.': 'No se encontraron datos para este asistente.',
        'Información General': 'Información General',
        'ID del Asistente:': 'ID del Asistente:',
        'Nombre:': 'Nombre:',
        'Creado en:': 'Creado en:',
        'Actualizado en:': 'Actualizado en:',
        'Server Webhook URL:': 'Server Webhook URL:',
        'No configurado': 'No configurado',
        'Server Webhook URL (Backup):': 'Server Webhook URL (Backup):',
        'Configuración del Modelo IA': 'Configuración del Modelo IA',
        'Proveedor:': 'Proveedor:',
        'Modelo:': 'Modelo:',
        'Mensajes del Sistema/Prompt:': 'Mensajes del Sistema/Prompt:',
        'Rol:': 'Rol:',
        'Herramientas (Tools):': 'Herramientas (Tools):',
        'Tipo:': 'Tipo:',
        'Descripción:': 'Descripción:',
        'Parámetros:': 'Parámetros:',
        'No hay información de configuración del modelo disponible.': 'No hay información de configuración del modelo disponible.',
        'Configuración de Voz (TTS)': 'Configuración de Voz (TTS)',
        'Proveedor TTS:': 'Proveedor TTS:',
        'ID de Voz:': 'ID de Voz:',
        'No hay información de configuración de voz disponible.': 'No hay información de configuración de voz disponible.',
        'Configuración de Llamada': 'Configuración de Llamada',
        'Primer Mensaje (First Message):': 'Primer Mensaje (First Message):',
        'Transferencia de Destino (Número):': 'Transferencia de Destino (Número):',
        'Máx. Duración (segundos):': 'Máx. Duración (segundos):',
        'Metadata': 'Metadata',
        'Datos JSON Completos del Asistente': 'Datos JSON Completos del Asistente',
        'Última actualización de esta página:': 'Última actualización de esta página:',
        'Ocurrió un error al procesar las llamadas.': 'Ocurrió un error al procesar las llamadas.',
        'No se pudieron obtener detalles para la llamada {call_id}.': 'No se pudieron obtener detalles para la llamada {call_id}.',
        'No se encontró transcripción en los detalles de la llamada {call_id}.': 'No se encontró transcripción en los detalles de la llamada {call_id}.',
        'No se encontró transcripción para esta llamada.': 'No se encontró transcripción para esta llamada.',
        'El formato de la transcripción no es compatible.': 'El formato de la transcripción no es compatible.',
    }
}

def get_locale():
    return session.get('language', 'en')

def gettext(text):
    return TRANSLATIONS.get(get_locale(), {}).get(text, text)

@app.context_processor
def inject_utilities():
    return {
        'get_status_badge_class': get_status_badge_class,
        'now': datetime.datetime.utcnow,
        '_': gettext
    }

@app.route('/language/<lang>')
def set_language(lang):
    session['language'] = lang
    return redirect(request.referrer or url_for('dashboard'))

def get_status_badge_class(status_str):
    status_lower = str(status_str).lower()
    if "error" in status_lower: return "badge-danger"
    if "active" in status_lower or "in-progress" in status_lower or "ringing" in status_lower: return "badge-success"
    if "ended" in status_lower or "completed" in status_lower: return "badge-secondary"
    return "badge-info"

@app.route('/')
@app.route('/dashboard')
def dashboard():
    assistant = vapi_service.get_assistant_details(TARGET_ASSISTANT_ID)
    agent_view_model = {}
    error_message = None
    if assistant:
        agent_view_model = {
            'id': assistant.get('id', 'N/A'),
            'name': assistant.get('name', 'Sin Nombre'),
            'model_provider': assistant.get('model', {}).get('provider', 'N/A'),
            'model_name': assistant.get('model', {}).get('model', 'N/A'),
            'status': "IDLE"
        }
    else:
        error_message = gettext("No se pudo cargar la información del agente.").format(name=TARGET_ASSISTANT_NAME)
    return render_template('index.html', agents=[agent_view_model] if agent_view_model else [],
                           error_message=error_message, last_updated=datetime.datetime.now())

# --- NEW: Page loading route ---
@app.route('/calls')
def calls_dashboard():
    """
    This route now ONLY renders the page shell with skeletons.
    The actual data will be fetched by a JavaScript call to /api/calls-data.
    """
    return render_template('calls.html',
                           agent_name=TARGET_ASSISTANT_NAME,
                           start_date=request.args.get('start_date'),
                           end_date=request.args.get('end_date'))

# --- NEW: API endpoint for fetching call data ---
@app.route('/api/calls-data')
def api_calls_data():
    """
    This new endpoint contains all the logic to fetch and process call data.
    It returns the data as JSON for the frontend to render.
    """
    period = request.args.get('period')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    now = datetime.datetime.now(datetime.timezone.utc)
    calls_for_period, error_message, total_duration_seconds = [], None, 0
    selected_period_display = "All Time"

    try:
        all_calls = vapi_service.get_active_calls(assistant_id=TARGET_ASSISTANT_ID)
        for call in all_calls:
            if not call.get('startedAt') or not call.get('endedAt'): continue
            start_time = isoparse(call['startedAt'])
            end_time = isoparse(call['endedAt'])
            
            in_period = False
            if start_date_str and end_date_str:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if start_date <= start_time.date() <= end_date: in_period = True
                selected_period_display = f"{start_date_str} to {end_date_str}"
            elif period:
                if period == 'day':
                    if start_time.date() == now.date(): in_period = True
                    selected_period_display = gettext('Hoy')
                elif period == 'week':
                    if now - datetime.timedelta(days=7) <= start_time: in_period = True
                    selected_period_display = gettext('Semana')
                elif period == 'month':
                    if start_time.month == now.month and start_time.year == now.year: in_period = True
                    selected_period_display = gettext('Mes')
            else:
                in_period = True

            if in_period:
                duration = end_time - start_time
                total_duration_seconds += duration.total_seconds()
                duration_str = f"{int(duration.total_seconds()) // 60:02d}:{int(duration.total_seconds()) % 60:02d}"
                calls_for_period.append({'id': call.get('id'), 'customer_number': call.get('customer', {}).get('number', 'N/A'),
                                         'status': call.get('status', 'UNKNOWN'), 'started_at': call.get('startedAt'),
                                         'ended_at': call.get('endedAt'), 'duration': duration_str})
    except Exception as e:
        app.logger.error(f"Error in api_calls_data: {e}", exc_info=True)
        error_message = gettext("Ocurrió un error al procesar las llamadas.")
        return jsonify({'error': error_message}), 500

    total_calls = len(calls_for_period)
    
    total_mins = int(total_duration_seconds) // 60
    total_secs = int(total_duration_seconds) % 60
    total_minutes_formatted = f"{total_mins:02d}:{total_secs:02d}"
    
    average_seconds = (total_duration_seconds / total_calls) if total_calls > 0 else 0
    avg_mins = int(average_seconds) // 60
    avg_secs = int(average_seconds) % 60
    average_minutes_formatted = f"{avg_mins:02d}:{avg_secs:02d}"

    return jsonify({
        'calls': calls_for_period,
        'total_calls': total_calls,
        'total_minutes_str': total_minutes_formatted,
        'average_minutes_str': average_minutes_formatted,
        'selected_period': selected_period_display
    })
                           
@app.route('/api/call/<call_id>/transcript')
def api_get_transcript(call_id):
    app.logger.info(f"Requesting transcript for call: {call_id}")
    call_details = vapi_service.get_call_details(call_id)
    if not call_details:
        app.logger.error(f"Could not get details for call {call_id}.")
        return jsonify({'error': gettext('No se pudieron obtener detalles para la llamada {call_id}.').format(call_id=call_id)}), 404
    
    transcript_data = call_details.get('transcript')
    if not transcript_data:
        app.logger.warning(f"Transcript not found in call details for {call_id}.")
        return jsonify({'transcript': gettext('No se encontró transcripción para esta llamada.')})

    if isinstance(transcript_data, list):
        formatted_transcript = [f"[{message.get('role', 'N/A').capitalize()}]: {message.get('message', '')}" for message in transcript_data]
        return jsonify({'transcript': "\n".join(formatted_transcript)})
    elif isinstance(transcript_data, str):
        return jsonify({'transcript': transcript_data})
    else:
        return jsonify({'transcript': gettext('El formato de la transcripción no es compatible.')})

@app.route('/assistant/<assistant_id>')
def assistant_details(assistant_id):
    assistant_data = vapi_service.get_assistant_details(assistant_id)
    return render_template('assistant_detail.html', assistant=assistant_data, last_updated=datetime.datetime.now())

if __name__ == '__main__':
    # For deployment, host must be '0.0.0.0' and the port is set by the 'PORT' env var.
    # Debug mode should be turned off for security.
    port = int(os.getenv("PORT", 7000))
    app.run(host="0.0.0.0", port=port, debug=False)