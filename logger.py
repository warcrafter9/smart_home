import pymongo
import datetime

from classes import Lamp, Thermostat


class Logger:
    def __init__(self, db_name):
        self.__client = pymongo.MongoClient('localhost', 27017)
        self.__db = self.__client[db_name]
        try:
            self.__client.server_info()  # Проверка соединения
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    def insert_sensor_data(self, room, sensor_type):
        result = {'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        if len([sensor for sensor in room.get_sensors() if sensor.get_type_value() == sensor_type]) != 0:
            for sensor in room.get_sensors():
                if sensor.get_type_value() == sensor_type:
                    result[sensor.get_name()] = sensor.get_value()
            return self.__db[f'Sensor {sensor_type} ' + room.get_name()].insert_one(result)

    def insert_focus_temperature(self, room):
        result = {'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        if len([device for device in room.get_devices() if isinstance(device, Thermostat)]) != 0:
            for device in room.get_devices():
                if isinstance(device, Thermostat):
                    result[f'{device.get_name()}_focus_temperature'] = device.get_focus_temperature()
            return self.__db['Focus temperatures ' + room.get_name()].insert_one(result)

    def insert_lamp(self, room):
        result = {'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        if len([device for device in room.get_devices() if isinstance(device, Lamp)]) != 0:
            for device in room.get_devices():
                if isinstance(device, Lamp):
                    result[device.get_name() + ' brightness: '] = device.get_brightness()
            return self.__db['Lamps work ' + room.get_name()].insert_one(result)

    def read_data(self, collection):
        return self.__db[collection].find()
