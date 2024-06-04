import abc
import datetime
import time


class Device(abc.ABC):
    __id_device = 0
    __devices = []

    @abc.abstractmethod
    def __init__(self, name):
        if self.is_name_unique(name):
            Device.__id_device += 1
            self.__device_id = Device.__id_device
            self.__name = name
            self.__status = False
            self.__off_time = None
            Device.__devices.append(self)
            print(f"Создано устройство: id: {self.__device_id}, название: {self.__name}")
        else:
            raise ValueError(f"Устройство с именем - {name} уже существует.")

    @staticmethod
    def is_name_unique(name):
        return all(device.get_name() != name for device in Device.__devices)

    @staticmethod
    def get_devices():
        return Device.__devices

    @abc.abstractmethod
    def print_info(self):
        print(f' Устройство: {self.__name},id: {self.__device_id}, статус: {self.__status}')

    def set_off_time(self, off_time):
        self.__off_time = off_time
        print(f'Уставновлено время выключения устройства {self.__name}: {self.__off_time}')

    def get_off_time(self):
        return self.__off_time

    def turn_on(self):
        self.__status = True
        print(self.get_name() + ' turned on')

    def turn_off(self):
        self.__status = False
        print(self.get_name() + ' turned off')

    def get_status(self):
        return self.__status

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__device_id


class Room:
    __id_room = 0
    __rooms = []

    def __init__(self, name):
        if self.is_name_unique(name):
            Room.__id_room += 1
            self.__name = name
            self.__devices = []
            self.__sensors = []
            self.__id = Room.__id_room
            Room.__rooms.append(self)
            print(f'Создана комната {self.__id_room}, {self.__name}')
        else:
            raise ValueError(f"Комната с именем {name} уже существует.")

    @staticmethod
    def is_name_unique(name):
        return all(room.get_name() != name for room in Room.__rooms)

    @staticmethod
    def get_rooms():
        return Room.__rooms

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def add_device(self, device):
        self.__devices.append(device)

    def add_sensor(self, sensor):
        self.__sensors.append(sensor)

    def get_devices(self):
        return self.__devices

    def get_sensors(self):
        return self.__sensors


class Sensor(Device):
    def __init__(self, name, type_value):
        super().__init__(name)
        self.__value = 0
        self.__type_value = type_value  # тип значения, собираемой информации
        print(f"Создан датчик {name}, тип собираемой информации: {type_value}")

    def print_info(self):
        super().print_info() + 'f, снимаемое значение "{self.__type_value}": {self.__value}'

    def increment_value(self):
        self.__value += 1

    def decrement_value(self):
        self.__value -= 1

    def set_value(self, new_value):
        self.__value = new_value

    def get_value(self):
        return self.__value

    def get_type_value(self):
        return self.__type_value


class Thermostat(Device):
    def __init__(self, name):
        super().__init__(name)
        self.__focus_temperature = 20
        self.__automatic_threshold = 30

    def set_automatic_threshold(self, threshold):
        self.__automatic_threshold = threshold
        print(f'Установлена пороговая температура {self.__automatic_threshold}')

    def get_automatic_threshold(self):
        return self.__automatic_threshold

    def set_focus_temperature(self, focus_temperature):
        if focus_temperature is not None:
            self.__focus_temperature = focus_temperature
            print(self.get_name() + f': установлена температура {self.__focus_temperature}')

    def get_focus_temperature(self):
        return self.__focus_temperature

    def print_info(self):
        super().print_info()

    def heat_or_cooling(self, *sensors):
        if self.get_status():
            for sensor in sensors:
                if sensor.get_type_value() == 'temperature':
                    if sensor.get_value() < self.__focus_temperature:
                        sensor.increment_value()
                    else:
                        sensor.decrement_value()


class Lamp(Device):
    def __init__(self, name):
        super().__init__(name)
        self.__brightness = 100
        self.__rgb_color = (255, 255, 255)  # Белый

    def set_color(self, rgb_string):
        if self.get_status():
            # Строка тип rgb(255,255,255) преобразуется в 255,255,255 и делится по запятой и пробелу
            rgb_values = rgb_string[4:-1].split(", ")
            # Преобразуем строки в целые числа
            try:
                rgb_values = [int(value) for value in rgb_values]
            except:
                print("Цвет должен быть представлен только целыми числами от 0 до 255")
                return
            if isinstance(rgb_values, (tuple, list)) and len(self.__rgb_color) == 3:
                for component in self.__rgb_color:
                    if not isinstance(component, int):
                        raise ValueError("RGB значение должно быть целочисленным.")
                    if not 0 <= component <= 255:
                        raise ValueError("RGB значение должно лежать в пределах 0-255.")
                self.__rgb_color = rgb_values
                print(f'{self.get_name()}. Значение цвета обновлено: {self.__rgb_color}')
            else:
                raise ValueError("Цвет должен быть представлен тремя целыми числами от 0 до 255.")

    def set_brightness(self, brightness):
        if brightness is not None:
            if self.get_status():
                if 0 <= brightness <= 100:
                    self.__brightness = brightness
                    print(f'{self.get_name()}: яркость установлена: {self.__brightness}')
                else:
                    raise ValueError("Значение яркости должно находится в пределе от 0 до 100.")

    def manage_lamp(self):
        while True:
            current_time = datetime.datetime.now().time()
            off_time = self.get_off_time()
            if off_time and current_time >= off_time:
                self.turn_off()
                print(f"Лампа {self.get_name()} выключена в {current_time}")
                self.set_off_time(None)
            time.sleep(30)

    def get_brightness(self):
        return self.__brightness

    def get_rgb_color(self):
        return self.__rgb_color

    def print_info(self):
        super().print_info()
