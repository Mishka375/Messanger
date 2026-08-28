import socket

from .log import log

class IP:
    IPv4:       int = socket.AF_INET            # IPv4 (сеть на основе протокола IP версии 4). Адрес — пара (host, port)
    IPv6:       int = socket.AF_INET6           # IPv6. Адрес — кортеж (host, port, flowinfo, scope_id)

    LOCAL:      int = socket.AF_UNIX            # UNIX-доменные сокеты (внутри одной ОС). Адрес — строка пути к файлу

    BLUETOOTH:  int = socket.AF_BLUETOOTH       # Bluetooth-сокеты (L2CAP, RFCOMM, HCI)

    PACKET:     int = socket.AF_PACKET          # Низкоуровневый доступ к сетевым устройствам (Linux)
    NETLINK:    int = socket.AF_NETLINK         # Связь ядра Linux с процессами
    CAN:        int = socket.AF_CAN             # CAN-интерфейс (Controller Area Network)

    QIPCRTR:    int = socket.AF_QIPCRTR         # Обмен с сопроцессорами в чипах Qualcom)
    UNSPEC:     int = socket.AF_UNSPEC          # Семейство не указано — используется в getaddrinfo() для автоматического выбора
    V_SOCK:     int = socket.AF_VSOCK           # Обмен между виртуальными машинами и хостом
    ALG:        int = socket.AF_ALG             # Интерфейс к криптографическому ядру Linux

class Sockets ():
    TCP:        int = socket.SOCK_STREAM        # Потоковый сокет (TCP) — надёжная передача с установкой соединения
    UDP:        int = socket.SOCK_DGRAM         # Дейтаграммный сокет (UDP) — ненадёжная передача без соединения
    RAW_SOCKET: int = socket.SOCK_RAW           # Сырой сокет — прямой доступ к IP-пакетам
    RDM:        int = socket.SOCK_RDM           # Надёжная дейтаграммная передача
    SEQ_PACKET: int = socket.SOCK_SEQPACKET     # Последовательная пакетная передача

    CLOSE_EXEC: int = socket.SOCK_CLOEXEC       # Флаг закрытия сокета при exec() (Linux)
    NON_BLOCK:  int = socket.SOCK_NONBLOCK      # Создание неблокирующего сокета (Linux)

class Protocols ():
    SOCKET:     int = socket.SOL_SOCKET
    TCP:        int = socket.IPPROTO_TCP        # Надёжное соединение
    UDP:        int = socket.IPPROTO_UDP        # Быстрые пакеты
    IP:         int = socket.IPPROTO_IP         # Общий IP уровень
    ICMP:       int = socket.IPPROTO_ICMP       # Ping, диагностика
    IPv6:       int = socket.IPPROTO_IPV6       # IPv6 протокол

class Special_address ():
    ANY:        int = socket.INADDR_ANY          # Принимать соединения на всех интерфейсах
    LOCAL:      int = socket.INADDR_LOOPBACK     # Локальный компьютер
    BROADCAST:  int = socket.INADDR_BROADCAST    # Широковещание

class Sockets_options ():
    REUSE_ADDRESS:    int = socket.SO_REUSEADDR  # Позволяет повторно использовать адрес
    REUSE_PORT:       int = socket.SO_REUSEPORT  # Несколько процессов на одном порту
    TCP_CHECK:        int = socket.SO_KEEPALIVE  # Проверка живости TCP соединения
    BROADCAST:        int = socket.SO_BROADCAST  # Разрешает broadcast
    GET_BUFFER:       int = socket.SO_RCVBUF     # Размер буфера приёма
    SEND_BUFFER:      int = socket.SO_SNDBUF     # Размер буфера отправки
    GET_TIMEOUT:      int = socket.SO_RCVTIMEO   # Таймаут получения
    SEND_TIMEOUT:     int = socket.SO_SNDTIMEO   # Таймаут отправки
    LOCK_CONNECT:     int = socket.SO_LINGER     # Управление закрытием соединения
    GET_SOCKET_ERROR: int = socket.SO_ERROR      # Получение ошибки сокета

class TCP_parameters ():
    NODELAY:            int = socket.TCP_NODELAY   # Отключает алгоритм Нейгла
    KEEPALIVE_WAIT:     int = socket.TCP_KEEPIDLE  # Время ожидания перед keepalive
    KEEPALIVE_INTERVAL: int = socket.TCP_KEEPINTVL # Интервал keepalive
    CHECK_COUNT:        int = socket.TCP_KEEPCNT   # Количество попыток проверки

class Flags ():
    TIME_DATA:                 int = socket.MSG_OOB      # Срочные данные
    CHECK_DATA_WITHOUT_DELETE: int = socket.MSG_PEEK     # Посмотреть данные без удаления
    WAIT_ALL:                  int = socket.MSG_WAITALL  # Ждать полный объём данных
    NOT_BLOCK:                 int = socket.MSG_DONTWAIT # Не блокировать
    NOT_SEND_SIGPIPE:          int = socket.MSG_NOSIGNAL # Не посылать SIGPIPE

class Off_part ():
    READ:             int = socket.SHUT_RD       # Только чтение
    WRITE:            int = socket.SHUT_WR       # Только запись
    ALL:              int = socket.SHUT_RDWR     # Всё

class Server:
    def __init__ (self,
                  ip_type:      int  = IP.IPv4,
                  socket_type:  int  = Sockets.TCP):

        try:
            self._sock = socket.socket(ip_type, socket_type)
            self._ip_type = ip_type

            self.clients = []

            log.debug('server has been create')
        except Exception as error:
            log.error(error)

    def setting (self,
                 protocol:       int,
                 socket_options: int,
                 value):

        self._sock.setsockopt(protocol, socket_options, value)

    def create_socket (self,
                       address:  str | list | None = None,
                       host:     str               = Special_address.ANY,
                       port:     int | None        = None,
                       flowinfo: str | int | None  = None,
                       scope_id: str | int | None  = None):

        try:
            if address is not None:
                self._sock.bind(address)
                return

            if self._ip_type == IP.IPv4:
                self._sock.bind((host, port))
            elif self._ip_type == IP.IPv6:
                self._sock.bind((host, port, flowinfo, scope_id))

            log.debug('socket has been create')
        except Exception as error:
            log.error(error)

    def start (self,
               backlog: int = 5):

        try:
            self._sock.listen(backlog)
            log.debug('server was started')
        except Exception as error:
            log.error(error)

    def accept (self):

        try:
            user, addr = self._sock.accept()
            self.clients.append(user)
            log.debug(f'user <{user}> was connected')
            return user
        except Exception as error:
            log.error(error)

    def send_to_address (self,
                 message: str        = '',
                 address: str | list = ()):

        try:
            if type(message) is not bytes:
                message = message.encode()
            self._sock.sendto(message, address)
            log.debug(f'user send message <{message}> to <{address}>')
        except Exception as error:
            log.error(error)

    def send (self,
                 message: str,
                 user = None):

        try:
            if type(message) is not bytes:
                message = message.encode()
            user.send(message)
            log.debug(f'server send message <{message}> to <{user}>')
        except Exception as error:
            log.error(error)

    def send_all (self,
                  message: str,
                  user):

            try:            
                if type(message) is not bytes:
                    message = message.encode()
                user.sendall(message)
                log.debug(f'server send message <{message}> to <{user}>')
            except Exception as error:
                log.error(error)

    def get_message (self,
                     bufsize: int = 1024,
                     user = None):

        try:
            _text = user.recv(bufsize).decode()
            # log.debug(f'message <{_text}> has been get')
            return _text
        except Exception as error:
            log.error(error)

    def from_get_message (self,
                          buffsize: int = 1024,
                          user = None):

        try:
            _text = self._sock.recvfrom(buffsize)
            log.debug(f'message <{_text[0]}> has been get from <{_text[1]}>')
            return _text
        except Exception as error:
            log.error(error)

    def end (self):

        try:
            self._sock.close()
            log.debug('server has been close')
        except Exception as error:
            log.error(error)

    def set_timeout (self,
                     timeout: float = 3.0):

        try:
            self._sock.settimeout(timeout)
            log.debug(f"new server's timeout <{timeout}>")
        except Exception as error:
            log.error(error)

    def disconnect_user (self,
                         user = None):

        try:
            if user is None:
                for i in self.clients:
                    i.close()
                log.debug('all users has been disconnect')
            else:
                user.close()

                log.debug(f'user <{user}> has been disconnect')
        except Exception as error:
            log.error(error)

    def off_part (self,
                  read:  bool = False,
                  write: bool = True):

        try:
            if read and not write:
                self._sock.shutdown(Off_part.READ)

            elif not read and write:
                self._sock.shutdown(Off_part.WRITE)

            elif read and write:
                self._sock.shutdown(Off_part.ALL)

            log.debug(f'part {"read"*read} {"write"*write} has been off')
        except Exception as error:
            log.error(error)