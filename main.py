import datetime
import threading
from random import random, randint
from threading import Timer

import pymongo
from flask import Flask, render_template, request, jsonify, redirect, url_for
import classes
import numpy as np
from logger import Logger
import statistics

logger = Logger("IOT_Logger")

app = Flask(__name__)


def avg_focus_temp(room):
    cursor = logger.read_data('Focus temperatures ' + room.get_name())
    list_focus_temp = list()
    for item in cursor:
        list_focus_temp.append(list(item.values())[2])
    return int(np.average(list_focus_temp))


def favorite_brightness(room):
    cursor = logger.read_data('Lamps work ' + room.get_name())
    list_favorite_brightness = list()
    for device in room.get_devices():
        if isinstance(device, classes.Lamp):
            for item in cursor:
                list_favorite_brightness.append(item[device.get_name() + ' brightness: '])
    if len(list_favorite_brightness) == 0:
        return 100
    return statistics.mode(list_favorite_brightness)


def manage_thermostat(room):
    thermostats = [device for device in room.get_devices() if isinstance(device, classes.Thermostat)]
    if not thermostats:
        return
    cursor = logger.read_data('Sensor temperature ' + room.get_name())
    list_temps = []
    # получаем первую запись, отсорт. по времени
    recent_temp_record = cursor.sort([('timestamp', pymongo.DESCENDING)]).limit(1)
    for sensor in room.get_sensors():
        if sensor.get_type_value() == 'temperature':
            list_temps.extend(list(recent_temp_record[0].values())[2:])
    average_temp = int(np.average(list_temps))
    for thermostat in thermostats:
        if not thermostat.get_status():
            threshold = thermostat.get_automatic_threshold()
            if threshold is not None:
                if average_temp > threshold:
                    thermostat.set_focus_temperature(avg_focus_temp(room))
                    thermostat.turn_on()

    Timer(5, manage_thermostat, args=[room]).start()


@app.route('/set_lamp_off_time', methods=['POST'])
def set_lamp_off_time():
    device_id = int(request.form.get('device_id'))
    room_id = int(request.form.get('room_id'))
    off_time_str = request.form.get('off_time')
    try:
        off_time = datetime.datetime.strptime(off_time_str, "%H:%M").time()
    except ValueError:
        return "Неверный формат времени", 400

    device = next((device for device in classes.Device.get_devices() if device.get_id() == device_id), None)
    if device:
        device.set_off_time(off_time)
        if isinstance(device, classes.Lamp):
            threading.Thread(target=device.manage_lamp).start()

    return redirect(url_for('room_detail', room_id=room_id))


@app.route('/set_automatic_threshold')
def set_automatic_threshold():
    try:
        threshold = int(request.args.get('threshold'))
        device_id = int(request.args.get('device_id'))
        device = next(device for device in classes.Device.get_devices() if device.get_id() == device_id)
        if isinstance(device, classes.Thermostat):
            device.set_automatic_threshold(threshold)
    except:
        print("Invalid threshold value")
    return {}


def log_temperature(room):
    logger.insert_sensor_data(room, 'temperature')
    Timer(5, log_temperature, args=[room]).start()


def log_humidity(room):
    logger.insert_sensor_data(room, 'humidity')
    Timer(5, log_humidity, args=[room]).start()


def log_focus_temperature(room):
    logger.insert_focus_temperature(room)
    Timer(5, log_focus_temperature, args=[room]).start()


def log_work_lamp(room):
    logger.insert_lamp(room)
    Timer(5, log_work_lamp, args=[room]).start()


def all_logger_start(room):
    log_temperature(room)
    log_focus_temperature(room)
    log_work_lamp(room)
    log_humidity(room)
    manage_thermostat(room)


@app.route('/status_device')
def set_status():
    device_id = int(request.args.get('device_id'))
    room_id = int(request.args.get('room_id'))
    # Получение объекта Room по идентификатору
    room = next((room for room in classes.Room.get_rooms() if room.get_id() == room_id), None)
    device = next(device for device in classes.Device.get_devices() if device.get_id() == device_id)
    checkbox = (bool(int(request.args.get('check', ''))))
    if checkbox:
        device.turn_on()
        if isinstance(device, classes.Thermostat):
            device.set_focus_temperature(avg_focus_temp(room))
        elif isinstance(device, classes.Lamp):
            device.set_brightness(favorite_brightness(room))
    else:
        device.turn_off()
    return {}


@app.route('/focus_temperature')
def set_focus_temperature():
    try:
        focus_temperature = int(request.args.get('value'))
        device_id = int(request.args.get('device_id'))
        device = next(device for device in classes.Device.get_devices() if device.get_id() == device_id)
        if 15 <= focus_temperature <= 30:
            device.set_focus_temperature(focus_temperature)
        else:
            print("Укажите желаемую температуру в пределах 15-30 градусов")
    except:
        print("Invalid focus temperature value")
    return {}


@app.route('/brightness')
def brightness():
    device_id = int(request.args.get('device_id'))
    device = next(device for device in classes.Device.get_devices() if device.get_id() == device_id)
    try:
        brightness_value = int(request.args.get('value'))
        if 0 <= brightness_value <= 100:
            device.set_brightness(brightness_value)
        else:
            print("Значение яркости должно находится от 0 до 100")
    except:
        print("Invalid brightness value")
    return {}


@app.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.form.get('room_name')
    # Возвращаем JSON ответ с данными о новой комнате, если не прилетело исключения при создании комнаты
    try:
        new_room = classes.Room(room_name)
        all_logger_start(new_room)
        return jsonify({'status': 'success', 'room': {'id': new_room.get_id(), 'name': new_room.get_name()}})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/update_color', methods=['POST'])
def color():
    select_color = request.form.get('color')
    device_id = int(request.form.get('device_id'))
    device = next(device for device in classes.Device.get_devices() if device.get_id() == device_id)
    device.set_color(select_color)
    return {}


@app.route('/create_device', methods=['POST'])
def create_device():
    device_type = request.form.get('device_type')
    device_name = request.form.get('device_name')
    room_id = int(request.form.get('room_id'))
    room = next((room for room in classes.Room.get_rooms() if room.get_id() == room_id), None)

    if room and device_type and device_name:
        if device_type == 'thermostat':
            device = classes.Thermostat(device_name)
        elif device_type == 'lamp':
            device = classes.Lamp(device_name)
        elif device_type == 'sensor':
            type_value = request.form.get('type_value')
            device = classes.Sensor(device_name, type_value)
        else:
            return jsonify({"error": "Invalid device type"}), 400

        if device_type == 'sensor':
            room.add_sensor(device)
        else:
            room.add_device(device)
        return jsonify({"id": device.get_id(), "name": device.get_name()})

    return jsonify({"error": "Invalid data"}), 400


@app.route('/')
def start_page():
    rooms_list = [{"id": room.get_id(), "name": room.get_name()} for room in classes.Room.get_rooms()]
    # проверка на AJAX-запрос (т.е. если http, то просто грузим страницу, а если ajax, то рендерим новый список комнат
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('rooms_list.html', rooms=rooms_list)  # для обновления без рефреша страницы
    return render_template('start_page.html', rooms=rooms_list)


@app.route('/rooms/<int:room_id>')
def room_detail(room_id):
    room = next((room for room in classes.Room.get_rooms() if room.get_id() == room_id), None)
    if room:
        devices = room.get_devices()
        sensors = room.get_sensors()
        thermostats = [device for device in room.get_devices() if isinstance(device, classes.Thermostat)]
        sensor_results = result_to_sensor(thermostats, sensors)
        sensor_humidity = random_humidity(sensors)
        return render_template('room_detail.html', room=room, devices=devices, sensor_temp=sensor_results
                               , sensor_humidity=sensor_humidity)
    else:
        return "Room not found", 404


def result_to_sensor(heaters_at_room, sensors):
    for heater in heaters_at_room:
        heater.heat_or_cooling(*sensors)
    result = {}
    for sensor in sensors:
        if sensor.get_type_value() == 'temperature':
            result[sensor.get_name()] = sensor.get_value()
    return result


def random_humidity(sensors):
    list_humidity_sensors = {}
    for sensor in sensors:
        if sensor.get_type_value() == 'humidity':
            sensor.set_value(randint(1, 100))
            list_humidity_sensors[sensor.get_name()] = sensor.get_value()
    return list_humidity_sensors


if __name__ == '__main__':
    app.run()
