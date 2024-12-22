import http.server
import json
import datetime
import psutil
import os
import threading
import time
import logging
from enum import Enum

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"

class SystemMetrics:
    """Clase para manejar umbrales y métricas del sistema"""
    # Umbrales para diferentes métricas
    THRESHOLDS = {
        'cpu': {
            'warning': 70,
            'critical': 90
        },
        'memory': {
            'warning': 80,
            'critical': 95
        },
        'disk': {
            'warning': 85,
            'critical': 95
        },
        'response_time': {
            'warning': 1.0,  # segundos
            'critical': 2.0
        }
    }

    @staticmethod
    def evaluate_metric(metric_name, value):
        if metric_name in SystemMetrics.THRESHOLDS:
            thresholds = SystemMetrics.THRESHOLDS[metric_name]
            if value >= thresholds['critical']:
                return HealthStatus.CRITICAL
            elif value >= thresholds['warning']:
                return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

class HealthMonitor:
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.request_count = 0
        self.errors = []
        self.response_times = []
        self._lock = threading.Lock()
        self.alert_count = 0
        self.last_automated_response = None
        self.system_metrics_history = {
            'cpu': [],
            'memory': []
        }

        # Iniciar monitoreo continuo
        self.monitoring_thread = threading.Thread(target=self._continuous_monitoring)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def increment_requests(self):
        with self._lock:
            self.request_count += 1

    def add_response_time(self, response_time):
        with self._lock:
            self.response_times.append(response_time)
            # Mantener solo los últimos 100 tiempos de respuesta
            if len(self.response_times) > 100:
                self.response_times.pop(0)

    def log_error(self, error):
        with self._lock:
            timestamp = datetime.datetime.now()
            error_entry = {
                'timestamp': timestamp.isoformat(),
                'error': str(error)
            }
            self.errors.append(error_entry)
            # Mantener solo los últimos 50 errores
            if len(self.errors) > 50:
                self.errors.pop(0)
            logging.error(f"Error detectado: {error}")

    def get_average_response_time(self):
        with self._lock:
            if not self.response_times:
                return 0
            return sum(self.response_times) / len(self.response_times)

    def _continuous_monitoring(self):
        """Monitoreo continuo del sistema"""
        while True:
            try:
                self._check_system_health()
                # Guardar métricas históricas
                with self._lock:
                    self.system_metrics_history['cpu'].append(psutil.cpu_percent())
                    self.system_metrics_history['memory'].append(psutil.virtual_memory().percent)
                    # Mantener solo las últimas 60 mediciones (1 hora)
                    if len(self.system_metrics_history['cpu']) > 60:
                        self.system_metrics_history['cpu'].pop(0)
                        self.system_metrics_history['memory'].pop(0)
                time.sleep(60)  # Revisar cada minuto
            except Exception as e:
                logging.error(f"Error en monitoreo continuo: {e}")

    def _check_system_health(self):
        """Verificar la salud del sistema y tomar acciones automáticas si es necesario"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        avg_response_time = self.get_average_response_time()

        # Evaluar métricas críticas
        metrics_status = {
            'cpu': SystemMetrics.evaluate_metric('cpu', cpu_percent),
            'memory': SystemMetrics.evaluate_metric('memory', memory.percent),
            'disk': SystemMetrics.evaluate_metric('disk', disk.percent),
            'response_time': SystemMetrics.evaluate_metric('response_time', avg_response_time)
        }

        # Acciones automáticas basadas en el estado
        self._take_automated_actions(metrics_status)

    def _take_automated_actions(self, metrics_status):
        """Implementar respuestas automáticas a problemas"""
        critical_count = sum(1 for status in metrics_status.values() 
                           if status == HealthStatus.CRITICAL)
        
        if critical_count > 0:
            self.alert_count += 1
            action_taken = "Alerta enviada al equipo de operaciones"
            
            # Simular acciones automáticas
            if self.alert_count >= 3:
                action_taken = "Iniciado proceso de auto-recuperación"
                # Aquí irían las acciones de auto-recuperación
                
            self.last_automated_response = {
                'timestamp': datetime.datetime.now().isoformat(),
                'action': action_taken,
                'trigger': 'Múltiples métricas críticas detectadas'
            }
            
            logging.warning(f"Acción automática tomada: {action_taken}")
        else:
            self.alert_count = 0

    def get_metrics_history(self):
        """Obtener historial de métricas de manera segura"""
        with self._lock:
            return {
                'cpu_trend': self.system_metrics_history['cpu'][-10:],
                'memory_trend': self.system_metrics_history['memory'][-10:]
            }

class EnhancedHealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, health_monitor=None, **kwargs):
        self.health_monitor = health_monitor
        super().__init__(*args, **kwargs)

    def do_GET(self):
        start_time = time.time()
        try:
            if self.path == '/health':
                self.health_monitor.increment_requests()
                self.send_health_check()
            elif self.path == '/metrics':
                self.send_detailed_metrics()
            elif self.path == '/trigger-error':
                raise Exception("Error simulado para pruebas")
            else:
                self.send_error(404)
        except Exception as e:
            self.health_monitor.log_error(e)
            # Enviar una respuesta JSON con el error en lugar de HTML
            self.send_json_error(500, str(e))
        finally:
            # Registrar tiempo de respuesta
            response_time = time.time() - start_time
            self.health_monitor.add_response_time(response_time)

    def send_health_check(self):
        """Endpoint principal de health check"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        avg_response_time = self.health_monitor.get_average_response_time()

        # Evaluar estado general
        metrics_status = {
            'cpu': SystemMetrics.evaluate_metric('cpu', cpu_percent),
            'memory': SystemMetrics.evaluate_metric('memory', memory.percent),
            'disk': SystemMetrics.evaluate_metric('disk', disk.percent),
            'response_time': SystemMetrics.evaluate_metric('response_time', avg_response_time)
        }

        overall_status = max(
            (status for status in metrics_status.values()), 
            key=lambda x: [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.CRITICAL].index(x)
        )

        health_data = {
            "status": overall_status.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "uptime_seconds": (datetime.datetime.now() - self.health_monitor.start_time).total_seconds(),
            "quick_metrics": {
                "request_count": self.health_monitor.request_count,
                "recent_errors": len(self.health_monitor.errors),
                "avg_response_time": avg_response_time
            },
            "system_metrics": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": disk.percent
            },
            "automated_response": self.health_monitor.last_automated_response
        }

        self._send_json_response(health_data)

    def send_detailed_metrics(self):
        """Endpoint para métricas detalladas"""
        detailed_data = {
            "errors": self.health_monitor.errors,
            "response_times": {
                "recent_times": self.response_times[-10:] if hasattr(self, 'response_times') else [],
                "average": self.health_monitor.get_average_response_time()
            },
            "system_metrics_history": self.health_monitor.get_metrics_history()
        }

        self._send_json_response(detailed_data)

    def _send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def send_json_error(self, code, message):
        """Enviar errores en formato JSON"""
        error_response = {
            "error": {
                "code": code,
                "message": message
            }
        }
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(error_response, indent=2).encode())

def run_server(port=8000):
    health_monitor = HealthMonitor()

    def handler_factory(*args, **kwargs):
        return EnhancedHealthCheckHandler(*args, health_monitor=health_monitor, **kwargs)

    server = http.server.HTTPServer(('localhost', port), handler_factory)
    print(f"\n=== Servidor de Health Check Mejorado ===")
    print(f"Servidor iniciado en http://localhost:{port}")
    print(f"\nEndpoints disponibles:")
    print(f"  - Health Check básico: http://localhost:{port}/health")
    print(f"  - Métricas detalladas: http://localhost:{port}/metrics")
    print(f"  - Simular Error: http://localhost:{port}/trigger-error")
    print("\nPresiona Ctrl+C para detener el servidor")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el servidor...")
        server.server_close()

if __name__ == '__main__':
    run_server()