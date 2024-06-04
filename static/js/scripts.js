function send_brightness(device_id) {
     const brightness = document.getElementById(`value_brightness_${device_id}`).value;
    $.ajax({
        type: 'GET', //тип запроса
        url: '/brightness', // адрес, на который отправлен запрос
        dataType: 'json', //тип данных, ожидаемый от сервера
        connectType: 'application/json', //тип передаваемых данных
        data: { //данные запроса
            "device_id": device_id,
            "value": brightness,
        },
        success: function (response) {
            console.log(response)
        }
    });
}

function send_room() {
    const roomName = document.getElementById("value").value;
    if (roomName) {
        $.ajax({
            type: 'POST',
            url: '/create_room',
            dataType: 'json',
            contentType: 'application/x-www-form-urlencoded',
            data: {"room_name": roomName},
            success: function (response) {
                if (response.error) {
                    alert(response.error);
                } else {
                    // Обновляем список комнат
                    $("#room-list-container").load("/ #room-list");
                    $('#value').val(''); // Очищаем поле ввода
                }
            },
            error: function (error) {
                alert('Ошибка при добавлении комнаты');
            }
        });
    } else {
        alert('Введите название комнаты');
    }
}


function send_focus_temperature(device_id) {
    const temperature = document.getElementById(`value_temp_${device_id}`).value;
    $.ajax({
        type: 'GET', //тип запроса
        url: '/focus_temperature', // адрес, на который отправлен запрос
        dataType: 'json', //тип данных, ожидаемый от сервера
        connectType: 'application/json', //тип передаваемых данных
        data: { //данные запроса
            "device_id": device_id,
            "value": temperature
        },
        success: function (response) {
            console.log(response)
        }
    });
}

function send_status_device(device_id,element,room_id) {
    $.ajax({
        type: 'GET', //тип запроса
        url: '/status_device', // адрес, на который отправлен запрос
        dataType: 'json', //тип данных, ожидаемый от сервера
        connectType: 'application/json', //тип передаваемых данных
        data: { //данные запроса
            "room_id":room_id,
            "device_id": device_id,
            "check": Number(document.getElementById(element.id).checked),
        },
        success: function (response) {
            console.log(response)
        }
    });
}
function set_automatic_threshold(device_id) {
    var threshold = document.getElementById('auto_threshold_' + device_id).value;
    fetch(`/set_automatic_threshold?device_id=${device_id}&threshold=${threshold}`)
        .then(response => {
            if (!response.ok) {
                console.error('Error setting automatic threshold');
            }
        });
}


