from flask import Flask, render_template, request, jsonify
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
app.secret_key = os.getenv("FLASK_SECRET_KEY", "una_llave_secreta_por_defecto_muy_segura")

def get_status_badge_class(status_str):
    status_lower = str(status_str).lower()
    if "error" in status_lower: return "badge-danger"
    if "active" in status_lower or "in-progress" in status_lower or "ringing" in status_lower: return "badge-success"
    if "ended" in status_lower or "completed" in status_lower: return "badge-secondary"
    return "badge-info"

@app.context_processor
def utility_processor():
    return dict(get_status_badge_class=get_status_badge_class)

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow}

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
        error_message = f"No se pudo cargar la información del agente '{TARGET_ASSISTANT_NAME}'."
    return render_template('index.html', agents=[agent_view_model] if agent_view_model else [],
                           error_message=error_message, last_updated=datetime.datetime.now())

@app.route('/calls')
def calls_dashboard():
    """Renderiza el dashboard de llamadas con filtros y KPIs formateados."""
    period = request.args.get('period')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    now = datetime.datetime.now(datetime.timezone.utc)
    calls_for_period, error_message, total_duration_seconds = [], None, 0
    selected_period_display = "Todo"

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
                selected_period_display = f"{start_date_str} a {end_date_str}"
            elif period:
                if period == 'day' and start_time.date() == now.date(): in_period = True
                elif period == 'week' and now - datetime.timedelta(days=7) <= start_time: in_period = True
                elif period == 'month' and start_time.month == now.month and start_time.year == now.year: in_period = True
                selected_period_display = period.capitalize()
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
        app.logger.error(f"Error en calls_dashboard: {e}", exc_info=True)
        error_message = "Ocurrió un error al procesar las llamadas."

    total_calls = len(calls_for_period)

    # --- INICIO DE LA MODIFICACIÓN ---
    # Formatear el tiempo total en MM:SS
    total_mins = int(total_duration_seconds) // 60
    total_secs = int(total_duration_seconds) % 60
    total_minutes_formatted = f"{total_mins:02d}:{total_secs:02d}"

    # Formatear el tiempo promedio en MM:SS
    average_seconds = (total_duration_seconds / total_calls) if total_calls > 0 else 0
    avg_mins = int(average_seconds) // 60
    avg_secs = int(average_seconds) % 60
    average_minutes_formatted = f"{avg_mins:02d}:{avg_secs:02d}"
    # --- FIN DE LA MODIFICACIÓN ---

    return render_template('calls.html', calls=calls_for_period, error_message=error_message,
                           last_updated=datetime.datetime.now(), agent_name=TARGET_ASSISTANT_NAME,
                           total_calls=total_calls,
                           total_minutes_str=total_minutes_formatted,      # <-- Variable actualizada
                           average_minutes_str=average_minutes_formatted,  # <-- Variable actualizada
                           selected_period=selected_period_display,
                           start_date=start_date_str, end_date=end_date_str)
                           
@app.route('/api/call/<call_id>/transcript')
def api_get_transcript(call_id):
    app.logger.info(f"Solicitando transcripción para la llamada: {call_id}")
    call_details = vapi_service.get_call_details(call_id)
    if not call_details:
        app.logger.error(f"No se pudieron obtener detalles para la llamada {call_id}.")
        return jsonify({'error': f'No se pudieron obtener detalles para la llamada {call_id}.'}), 404
    transcript_data = call_details.get('transcript')
    if not transcript_data:
        app.logger.warning(f"No se encontró transcripción en los detalles de la llamada {call_id}.")
        return jsonify({'transcript': 'No se encontró transcripción para esta llamada.'})
    if isinstance(transcript_data, list):
        formatted_transcript = [f"[{message.get('role', 'N/A').capitalize()}]: {message.get('message', '')}" for message in transcript_data]
        return jsonify({'transcript': "\n".join(formatted_transcript)})
    elif isinstance(transcript_data, str):
        return jsonify({'transcript': transcript_data})
    else:
        return jsonify({'transcript': 'El formato de la transcripción no es compatible.'})

@app.route('/assistant/<assistant_id>')
def assistant_details(assistant_id):
    assistant_data = vapi_service.get_assistant_details(assistant_id)
    return render_template('assistant_detail.html', assistant=assistant_data, last_updated=datetime.datetime.now())

if __name__ == '__main__':
    app.run(host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
            port=int(os.getenv("FLASK_RUN_PORT", 7000)),
            debug=True)