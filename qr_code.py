import PIL
import qrcode


def make_qr(arg):
    value_qr = str(arg)
    print('Запрошен: ' + value_qr)
    # Создание qr-кода
    img = qrcode.make(value_qr)
    # Сохранение qr-кода
    img.save('qrcode.png')
    return arg
