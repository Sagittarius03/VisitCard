import socket
import sys

from .settings import ALLOWED_HOSTS

def get_current_port():
    """
    Получает порт из аргументов командной строки runserver
    """
    port = 8000  # Порт по умолчанию Django
    
    # Ищем runserver в аргументах
    if 'runserver' in sys.argv:
        runserver_index = sys.argv.index('runserver')
        
        # Следующий аргумент после runserver может содержать порт
        if len(sys.argv) > runserver_index + 1:
            next_arg = sys.argv[runserver_index + 1]
            
            # Проверяем, содержит ли аргумент порт (например, "8000" или "0.0.0.0:8000")
            if ':' in next_arg:
                # Формат: адрес:порт
                port = int(next_arg.split(':')[-1])
            elif next_arg.isdigit():
                # Только порт
                port = int(next_arg)
            else:
                # Может быть имя хоста без порта или другое
                pass
    
    return port

def get_bind_address():
    """
    Получает полный адрес и порт
    """
    address = '127.0.0.1'  # По умолчанию
    port = 8000
    
    if 'runserver' in sys.argv:
        runserver_index = sys.argv.index('runserver')
        
        if len(sys.argv) > runserver_index + 1:
            next_arg = sys.argv[runserver_index + 1]
            
            if ':' in next_arg:
                # Формат: адрес:порт
                parts = next_arg.split(':')
                address = parts[0]
                port = int(parts[1])
            elif next_arg.isdigit():
                # Только порт
                port = int(next_arg)
    
    return address, port

def is_port_in_use(port, host='127.0.0.1'):
    """
    Проверяет, используется ли порт
    
    Args:
        port: Номер порта
        host: Хост для проверки
    
    Returns:
        bool: True если порт используется
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True

def get_project_urls():
    """
    Получает все URL для доступа к проекту
    """
    host, port = get_bind_address()
    urls = []
    
    # Локальный адрес
    urls.append(f"http://localhost:{port}")
    urls.append(f"http://127.0.0.1:{port}")
    
    # Если хост указан явно
    if host not in ['127.0.0.1', 'localhost']:
        urls.append(f"http://{host}:{port}")
    
    # Добавляем все разрешенные хосты из ALLOWED_HOSTS
    if 'ALLOWED_HOSTS' in globals():
        for allowed_host in ALLOWED_HOSTS:
            if allowed_host != '*':
                if ':' not in allowed_host:  # Не IP с портом
                    urls.append(f"http://{allowed_host}:{port}")
    
    # Удаляем дубликаты
    return list(dict.fromkeys(urls))

__all__ = ['get_current_port', 'get_bind_address', 'get_project_urls', 'is_port_in_use']