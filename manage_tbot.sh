#!/bin/bash

# Название Python-скрипта
APP="tbot.py"

# Лог-файл для записи вывода
LOGFILE="tbot.log"

# PID-файл для хранения ID процесса
PIDFILE="tbot.pid"

start() {
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "Скрипт уже запущен (PID: $(cat "$PIDFILE"))."
    else
        echo "Запускаем $APP..."
        nohup python3 "$APP" > "$LOGFILE" 2>&1 &
        echo $! > "$PIDFILE"
        echo "$APP запущен (PID: $(cat "$PIDFILE"))."
    fi
}

stop() {
    if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then
        echo "Останавливаем $APP (PID: $(cat "$PIDFILE"))..."
        kill $(cat "$PIDFILE") && rm -f "$PIDFILE"
        echo "$APP остановлен."
    else
        echo "$APP не запущен."
    fi
}

restart() {
    echo "Перезапускаем $APP..."
    stop
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    *)
        echo "Использование: $0 {start|stop|restart}"
        exit 1
        ;;
esac
