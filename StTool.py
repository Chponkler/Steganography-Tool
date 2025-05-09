from PIL import Image

def string_to_bits(data):
    """Преобразование строки в список битов"""
    bits = []
    for byte in data:
        bits += [int(bit) for bit in format(byte, '08b')]
    return bits

def bits_to_bytes(bits):
    """Преобразование списка битов в байты"""
    bytes_list = []
    for i in range(0, len(bits), 8):
        chunk = bits[i:i+8]
        if len(chunk) < 8:
            break
        bytes_list.append(int(''.join(map(str, chunk)), 2))
    return bytes(bytes_list)

def encrypt_message(message, key):
    """Шифрование сообщения с использованием XOR"""
    key_bytes = key.encode('utf-8')
    encrypted = []
    for i, char in enumerate(message.encode('utf-8')):
        encrypted.append(char ^ key_bytes[i % len(key_bytes)])
    return bytes(encrypted)

def decrypt_message(data, key):
    """Дешифрование сообщения с использованием XOR"""
    key_bytes = key.encode('utf-8')
    decrypted = []
    for i, byte in enumerate(data):
        decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
    return bytes(decrypted).decode('utf-8', errors='ignore')

def embed_message(img_path, message, key):
    """Встраивание сообщения в изображение"""
    try:
        # Шифруем сообщение
        encrypted_msg = encrypt_message(message, key)
        # Преобразуем в биты
        message_bits = string_to_bits(encrypted_msg)
        # Добавляем маркер окончания (32 нулевых бита)
        message_bits += [0] * 32

        # Открываем изображение
        img = Image.open(img_path)
        pixels = img.load()
        width, height = img.size

        # Проверяем вместимость
        max_bits = width * height * 3
        if len(message_bits) > max_bits:
            print("Ошибка: Сообщение слишком длинное для этого изображения")
            return

        # Встраиваем биты в изображение
        bit_index = 0
        for y in range(height):
            for x in range(width):
                if bit_index >= len(message_bits):
                    break

                r, g, b = pixels[x, y][:3]

                # Модифицируем младшие биты
                if bit_index < len(message_bits):
                    r = (r & 0xFE) | message_bits[bit_index]
                    bit_index += 1
                if bit_index < len(message_bits):
                    g = (g & 0xFE) | message_bits[bit_index]
                    bit_index += 1
                if bit_index < len(message_bits):
                    b = (b & 0xFE) | message_bits[bit_index]
                    bit_index += 1

                pixels[x, y] = (r, g, b)

        # Сохраняем результат
        new_path = img_path.split('.')[0] + '_encrypted.png'
        img.save(new_path)
        print(f"Сообщение успешно встроено в {new_path}")

    except Exception as e:
        print(f"Ошибка при шифровании: {str(e)}")

def extract_message(img_path, key):
    """Извлечение сообщения из изображения"""
    try:
        img = Image.open(img_path)
        pixels = img.load()
        width, height = img.size

        extracted_bits = []
        separator = [0] * 32  # Маркер окончания

        # Собираем биты из изображения
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y][:3]
                extracted_bits.append(r & 1)
                extracted_bits.append(g & 1)
                extracted_bits.append(b & 1)

                # Проверяем маркер окончания
                if len(extracted_bits) >= len(separator):
                    if extracted_bits[-len(separator):] == separator:
                        extracted_bits = extracted_bits[:-len(separator)]
                        break
            else:
                continue
            break

        # Преобразуем биты в байты
        encrypted_data = bits_to_bytes(extracted_bits)
        # Дешифруем сообщение
        decrypted_msg = decrypt_message(encrypted_data, key)
        print("\nРасшифрованное сообщение:")
        print(decrypted_msg)

    except Exception as e:
        print(f"Ошибка при дешифровании: {str(e)}")

def main():
    print("Steganography Tool")
    print("1. Зашифровать сообщение")
    print("2. Расшифровать сообщение")

    choice = input("Выберите действие (1/2): ")

    if choice == '1':
        img_path = input("Путь к исходному изображению: ")
        message = input("Введите сообщение для шифрования: ")
        key = input("Введите ключ шифрования: ")
        embed_message(img_path, message, key)

    elif choice == '2':
        img_path = input("Путь к зашифрованному изображению: ")
        key = input("Введите ключ дешифрования: ")
        extract_message(img_path, key)

    else:
        print("Неверный выбор")

if __name__ == "__main__":
    main()
