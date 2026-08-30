import socket
from . import log


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

class Client:
    def __init__ (self,
                  ip_type:     int = IP.IPv4,
                  socket_type: int = Sockets.TCP,
                  sock             = None):

        try:
            self._connected = False

            log.log.debug('client has been create')

            if sock is None:
                self._sock = socket.socket(ip_type, socket_type)
                return

            self._sock = sock
        except Exception as error:
            log.log.error(error)

    def connect (self,
                 host:    str               = '127.0.0.1',
                 port:    int               = '128',
                 address: str | list | None = None):

        try:
            if address is None:
                self._sock.connect((host, port))
            else:
                self._sock.connect(address)

            self._connected = True

            log.log.debug('client was connected')
        except Exception as error:
            log.log.error(error)

    def connect_ex (self,
                 host:    str,
                 port:    int,
                 address: str | list | None = None):

        try:
            if address is None:
                err = self._sock.connect_ex((host, port))
            else:
                err = self._sock.connect_ex(address)

            if err == 0:
                self._connected = True
                log.log.debug('client was connected')
            else:
                log.log.debug(f"client's error in connect <{err}>")
                return err
        except Exception as error:
            log.log.error(error)

    def send (self,
              message: str = ''):

        try:
            if self._connected:
                if type(message) is not bytes:
                    message = message.encode("utf-8", errors='replace')
                self._sock.send(message)
                log.log.debug(f'client send message <{message}>')
        except Exception as error:
            log.log.error(error)

    def send_all (self,
                  message: str = ''):

        try:
            if self._connected:
                if type(message) is not bytes:
                    message = message.encode("utf-8", errors='replace')
                self._sock.sendall(message)
                log.log.debug(f'client send message <{message}>')
        except Exception as error:
            log.log.error(error)

    def send_to (self,
                 message: str        = '',
                 address: str | list = ()):

        try:
            if self._connected:
                if type(message) is not bytes:
                    message = message.encode("utf-8", errors='replace')
                self._sock.sendto(message, address)
            log.log.debug(f'client send message <{message}> to <{address}>')
        except Exception as error:
            log.log.error(error)

    def get_message (self,
                     bufsize: int = 1024):

        try:
            _text = self._sock.recv(bufsize)
            log.log.debug(f'client was get message <{_text}>')
            return _text
        except Exception as error:
            log.log.error(error)

    def from_get_message (self,
                          buffsize: int = 1024):

        try:
            _text = self._sock.recvfrom(buffsize)
            log.log.debug(f'client was get message <{_text}>')
            return _text
        except Exception as error:
            log.log.error(error)

    def disconnect (self):

        try:
            self._sock.close()
            self._connected = False
            log.log.debug('client has been disconnect')
        except Exception as error:
            log.log.error(error)

    def set_timeout(self,
                    timeout: float = 3.0):

        try:
            self._sock.settimeout(timeout)
            log.log.debug(f"new client's timeout <{timeout}>")
        except Exception as error:
            log.log.error(error)