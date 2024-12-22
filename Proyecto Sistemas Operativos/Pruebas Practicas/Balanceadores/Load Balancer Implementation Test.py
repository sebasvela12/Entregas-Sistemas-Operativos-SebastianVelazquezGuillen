import time
import random
from collections import deque

class SimpleLoadBalancer:
    """Implementación del algoritmo Round-Robin"""
    def __init__(self, servers):
        self.servers = deque(servers)
        self.request_counts = {server: 0 for server in servers}
        self.total_response_time = {server: 0 for server in servers}

    def get_next_server(self):
        current_server = self.servers[0]
        self.servers.rotate(-1)
        self.request_counts[current_server] += 1
        return current_server

    def add_response_time(self, server, time):
        self.total_response_time[server] += time

    def print_stats(self):
        print("\nEstadísticas Round-Robin:")
        total_requests = sum(self.request_counts.values())
        for server, count in self.request_counts.items():
            avg_response_time = (
                self.total_response_time[server] / count 
                if count > 0 else 0
            )
            print(f"{server}:")
            print(f"  Requests: {count} ({(count/total_requests)*100:.1f}%)")
            print(f"  Tiempo promedio de respuesta: {avg_response_time:.3f}s")

class LeastConnectionsBalancer:
    """Implementación del algoritmo Least Connections"""
    def __init__(self, servers):
        self.servers = servers
        self.active_connections = {server: 0 for server in servers}
        self.total_requests = {server: 0 for server in servers}
        self.total_response_time = {server: 0 for server in servers}

    def add_connection(self, server):
        self.active_connections[server] += 1
        self.total_requests[server] += 1

    def remove_connection(self, server):
        self.active_connections[server] = max(0, self.active_connections[server] - 1)

    def get_server(self):
        return min(self.active_connections.items(), key=lambda x: x[1])[0]

    def add_response_time(self, server, time):
        self.total_response_time[server] += time

    def print_stats(self):
        print("\nEstadísticas Least Connections:")
        total_requests = sum(self.total_requests.values())
        for server in self.servers:
            avg_response_time = (
                self.total_response_time[server] / self.total_requests[server] 
                if self.total_requests[server] > 0 else 0
            )
            print(f"{server}:")
            print(f"  Conexiones activas: {self.active_connections[server]}")
            print(f"  Requests totales: {self.total_requests[server]} "
                  f"({(self.total_requests[server]/total_requests)*100:.1f}%)")
            print(f"  Tiempo promedio de respuesta: {avg_response_time:.3f}s")

class WeightedRoundRobinBalancer:
    """Implementación del algoritmo Weighted Round-Robin"""
    def __init__(self, server_weights):
        self.server_weights = server_weights
        self.current_weights = {server: 0 for server in server_weights}
        self.request_counts = {server: 0 for server in server_weights}
        self.total_response_time = {server: 0 for server in server_weights}
    
    def get_next_server(self):
        total_weight = sum(self.server_weights.values())
        max_weight = -1
        selected_server = None
        
        for server in self.server_weights:
            self.current_weights[server] += self.server_weights[server]
            if self.current_weights[server] > max_weight:
                max_weight = self.current_weights[server]
                selected_server = server
        
        self.current_weights[selected_server] -= total_weight
        self.request_counts[selected_server] += 1
        return selected_server

    def add_response_time(self, server, time):
        self.total_response_time[server] += time

    def print_stats(self):
        print("\nEstadísticas Weighted Round-Robin:")
        total_requests = sum(self.request_counts.values())
        for server, count in self.request_counts.items():
            weight = self.server_weights[server]
            expected_ratio = weight / sum(self.server_weights.values())
            actual_ratio = count / total_requests if total_requests > 0 else 0
            avg_response_time = (
                self.total_response_time[server] / count 
                if count > 0 else 0
            )
            print(f"{server} (peso {weight}):")
            print(f"  Requests recibidos: {count}")
            print(f"  Porcentaje real: {actual_ratio*100:.1f}%")
            print(f"  Porcentaje esperado: {expected_ratio*100:.1f}%")
            print(f"  Tiempo promedio de respuesta: {avg_response_time:.3f}s")

def simulate_server_processing(server_name):
    """Simula el tiempo de procesamiento de un servidor"""
    if "Potente" in server_name:
        return random.uniform(0.01, 0.03)  # Servidor más rápido
    elif "Medio" in server_name:
        return random.uniform(0.02, 0.04)  # Servidor de velocidad media
    elif "Básico" in server_name:
        return random.uniform(0.03, 0.05)  # Servidor más lento
    else:
        # Para servidores sin clasificación específica
        return random.uniform(0.02, 0.04)

def run_comparative_test(num_requests=100):
    """Ejecuta pruebas comparativas de los tres algoritmos"""
    # Configuración de servidores
    servers_basic = ["Server-1", "Server-2", "Server-3"]
    server_weights = {
        "Server-Potente": 5,
        "Server-Medio": 3,
        "Server-Básico": 2
    }
    
    # Inicializar balanceadores
    rr_balancer = SimpleLoadBalancer(servers_basic)
    lc_balancer = LeastConnectionsBalancer(servers_basic)
    wrr_balancer = WeightedRoundRobinBalancer(server_weights)
    
    print(f"\n=== Iniciando prueba comparativa con {num_requests} requests ===")
    
    # Escenario 1: Carga normal
    print("\nEscenario 1: Carga normal")
    for i in range(num_requests):
        # Round Robin
        rr_server = rr_balancer.get_next_server()
        process_time = simulate_server_processing(rr_server)
        rr_balancer.add_response_time(rr_server, process_time)
        
        # Least Connections
        lc_server = lc_balancer.get_server()
        lc_balancer.add_connection(lc_server)
        process_time = simulate_server_processing(lc_server)
        lc_balancer.add_response_time(lc_server, process_time)
        if random.random() > 0.3:  # 70% de probabilidad de finalizar
            lc_balancer.remove_connection(lc_server)
        
        # Weighted Round Robin
        wrr_server = wrr_balancer.get_next_server()
        process_time = simulate_server_processing(wrr_server)
        wrr_balancer.add_response_time(wrr_server, process_time)
        
        # Simular tiempo de procesamiento
        time.sleep(0.01)  # Pequeña pausa para no saturar el sistema
        
        if (i + 1) % 20 == 0:  # Mostrar progreso cada 20 requests
            print(f"Procesados {i + 1} requests...")
    
    print("\n=== Resultados Finales ===")
    rr_balancer.print_stats()
    lc_balancer.print_stats()
    wrr_balancer.print_stats()

if __name__ == "__main__":
    # Ejecutar prueba con 100 requests
    run_comparative_test(100)