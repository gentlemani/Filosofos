import time
import random

import threading
import os
from colorama import init, Fore, Back, Style
from pynput import keyboard as kb

"""
Problema productor-consumidor
El programa describe dos procesos, productor y consumidor,
ambos comparten un buffer de tamaño finito.
La tarea del productor es generar un producto, almacenarlo y comenzar nuevamente;
mientras que el consumidor toma (simultáneamente) productos uno a uno.
El problema consiste en que el productor no añada más productos que la capacidad del buffer
y que el consumidor no intente tomar un producto si el buffer está vacío.

Se detiene hasta que se presiona la tecla scape (Esc)
"""


class Buffer:
    def __init__(self):
        # To know the where are the producer and the consumer
        self.count_producer = 0
        self.count_consumer = 0
        # buffer with size of 25
        self.almacen = [""]*25
        self.stop_threads = False
        # It afects to the waiting time between the consumer and the producer and the visualization on the command prompt
        self.min_waiting_time = 2
        self.max_waiting_time = 15
        # Producer and consumer's states
        self.producer_state = 's'
        self.consumer_state = 's'
        # Semaphores
        self.buffer_semaphore = threading.BoundedSemaphore(1)
        self.state_semaphore = threading.BoundedSemaphore(1)
        self.producer_semaphore = threading.Semaphore(1)
        self.consumer_semaphore = threading.Semaphore(0)

    def producer(self):
        while not self.stop_threads:
            # Semaphore

            self.producer_semaphore.acquire()

            # Change status to trying to work
            self.producer_status_change('t')
            # Wait two seconds
            time.sleep(2)

            self.buffer_semaphore.acquire()
            # Critical Section
            self.producer_status_change('w')
            self.produce()
            time.sleep(2)
            self.buffer_semaphore.release()
            # Change producer state
            self.producer_status_change('s')
            # Waiting time to consume
            time_to_sleep = random.randint(
                self.min_waiting_time, self.max_waiting_time)
            # Sleeping time
            time.sleep(time_to_sleep)

    def consumer(self):
        while not self.stop_threads:
            # Semaphore

            # Waiting for a consumer release
            self.consumer_semaphore.acquire()

            self.consumer_status_change('t')
            # Wait two seconds
            time.sleep(2)
            # Waiting to join to the critical section
            self.buffer_semaphore.acquire()
            # Critical Section
            # Waiting time to consume

            self.consumer_status_change('w')
            self.consume()
            time.sleep(2)

            self.buffer_semaphore.release()
            # change consumer state
            self.consumer_status_change('s')

            # Waiting a random time to consume again
            time_to_sleep = random.randint(
                self.min_waiting_time, self.max_waiting_time)
            time.sleep(time_to_sleep)

    # To produce's function

    def produce(self):
        # Change producer status
        times_to_produces = random.randint(1, 5)
        i = 0
        while (i < times_to_produces):
            if not self.isBufferFull():
                if self.count_producer >= 24:
                    self.almacen[24] = '*'
                    self.count_producer = 0
                else:
                    self.almacen[self.count_producer] = '*'
                    self.count_producer += 1
                i += 1
            else:
                break
        self.update()
        if i != 0:
            print("Se obtuvo una producción de", i)
        else:
            print("Buffer lleno")
        if not self.isBufferFull() and self.producer_semaphore._value <= 0:
            self.producer_semaphore.release()
        self.consumer_check()
        print()
    # To consume's function

    def consume(self):
        # Change consumer status
        times_to_consume = random.randint(1, 5)
        i = 0
        while (i < times_to_consume):
            if not self.isBufferEmpty():
                if self.count_consumer >= 24:
                    self.almacen[24] = ''
                    self.count_consumer = 0
                else:
                    self.almacen[self.count_consumer] = ''
                    self.count_consumer += 1
                i += 1
            else:
                break
        self.update()

        if i != 0:
            print("Se consumió", i)
        else:
            print("Se intentó consumir pero el buffer está vacío")
        if not self.isBufferEmpty() and self.consumer_semaphore._value <= 0:
            self.consumer_semaphore.release()
        self.producer_check()

    def producer_check(self):
        if not self.isBufferFull() and self.producer_semaphore._value <= 0:
            self.producer_semaphore.release()

    def consumer_check(self):
        if not self.isBufferEmpty() and self.consumer_semaphore._value <= 0:
            self.consumer_semaphore.release()

    def producer_status_change(self, state):
        self.state_semaphore.acquire()
        self.producer_state = state
        print("-----------------------------------------------")
        self.semaphore_values()
        print("-----------------------------------------------")

        self.state_semaphore.release()

    def consumer_status_change(self, state):
        self.state_semaphore.acquire()
        self.consumer_state = state
        print("-----------------------------------------------")
        self.semaphore_values()
        print("-----------------------------------------------")
        self.state_semaphore.release()

    def semaphore_values(self):
        print("El consumidor está:", end=' ')
        self.semaphore_states(self.consumer_state)
        print("El productor está:", end=' ')
        self.semaphore_states(self.producer_state)

    def semaphore_states(self, state):
        # s = sleeping
        # w = working
        # t = trying to work
        if state == 's':
            print("Durmiendo")
        elif state == 'w':
            print("Trabajando")
        elif state == 't':
            print('Intentando trabajar')

    def update(self):
        # self.clean_window()
        print("********************************************************")
        for i in range(25):
            if i % 5 == 0 and i != 0:
                print('')
            if self.almacen[i] == '':
                print(Fore.GREEN+'-', end=" ")
            else:
                print(Fore.CYAN+'*', end=" ")
        print(Style.RESET_ALL+"\n")
        print("********************************************************")

    def clean_window(self):
        if os.name == "posix":
            os.system("clear")
        elif os.name == "ce" or os.name == "nt" or os.name == "dos":
            os.system("cls")

    def isBufferFull(self):
        return '' not in self.almacen

    def isBufferEmpty(self):
        return '*' not in self.almacen

    def stopAll(self, tecla):
        if tecla == kb.Key.esc:
            self.stop_threads = True
            return False


if __name__ == '__main__':
    # Inicialización para utilizar diferentes colores en la consola
    init()
    # Instancia del objeto
    buffer = Buffer()
    # Inicializaciión de los hilos
    thread_producer = threading.Thread(target=buffer.producer)
    thread_consumer = threading.Thread(target=buffer.consumer)
    thread_producer.start()
    thread_consumer.start()

    # Hilo para detener todo el programa
    with kb.Listener(buffer.stopAll) as escuchador:
        escuchador.join()

    if not thread_consumer.is_alive():
        print("consumidor fuera")
    if not thread_producer.is_alive():
        print("Productor fuera")
