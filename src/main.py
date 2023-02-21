import ipaddress
import time
import telebot
from telebot import types

bot = telebot.TeleBot('tokenid')

# Стартовое сообщение
@bot.message_handler(commands=['start'])
def startup(pm):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    netcalc = types.KeyboardButton("Калькулятор сетей")
    subnetcalc = types.KeyboardButton("Разделить сеть на подсети")
    markup.add(netcalc)
    markup.add(subnetcalc)
    bot.send_message(pm.chat.id,'Нажми: \nКалькулятор сетей, для того чтобы расчитать сеть \nРазделить сеть — для списка подсетей для введенной сети ',
                     reply_markup=markup)

# Выбор варианта, переход к сценарию 1 - калькулятор ip сети;  или сценарию 2-разделение сети по введенной маске
@bot.message_handler(content_types=["text"])
def handle_text(pm):
    if  pm.text.strip() == "Калькулятор сетей":
        sent_msg = bot.send_message(pm.chat.id, "Введите ip сети") #Ввод ip адреса, переход на следующий шаг - ввода маски
        bot.register_next_step_handler(sent_msg, ip_address_handler)
    elif pm.text.strip() == "Разделить сеть на подсети":
        sent_msg = bot.send_message(pm.chat.id, "Введите ip сети") # Ввод ip адреса, переход на следующий шаг - ввода маски для второго варианта
        bot.register_next_step_handler(sent_msg, subnets_ip_handler)

# преобразование сообщения с ip в переменную, ввод маски сети, передача переменной ip на следующий шаг
def subnets_ip_handler(pm):
    ip = pm.text
    sent_msg = bot.send_message(pm.chat.id, f"Сеть: {ip} Введите маску в формате CIDR или в обычном виде")
    bot.register_next_step_handler(sent_msg, subnets_mask_handler, ip)

# преобразование сообщения содержащего префикс в переменную, формирование переменной network,
# для работы с библиотекой ipaddress, ввод префикса делителя, переход на следующий шаг
def subnets_mask_handler(pm,ip):
    mask=pm.text
    network = str(ip + '/' + mask)
    sent_msg = bot.send_message(pm.chat.id, f"Cеть:{network}\nВыставите префикс маски на которые будут делится подсети")
    bot.register_next_step_handler(sent_msg, subnets_calc, network)

# Разделение сети на подсети посредству префикса
def subnets_calc(pm,network):
        try:
            prefix = int(pm.text)
            net = ipaddress.ip_network(network)
            sublist=list(net.subnets(new_prefix=prefix)) # Формирование списка из Ipv4Networks
            substring=('\n'.join(map(str, sublist))) # Преобразование в строку списка Ipv4Networks, удаляется ненужная информация, на вывод остается информаци типа ip/mask
            ip_list=substring.split('\n') # Обратное преобразование в читаемый список
            counter = 0 # Установка счетчика
            for ipnetwork in range(len(ip_list)): # Цикл перебора ip подсетей в списке ip_list, установка таймера на вывод сообщений для того чтобы избежать ошибок
                counter += 1
                net=ipaddress.ip_network(ip_list[ipnetwork])
                if (counter % 5) == 0:
                    time.sleep(5)
                    print(counter)
                else:
                    bot.send_message(pm.chat.id, f"Подсеть {counter}: {ip_list[ipnetwork]}\n"
                                                 f"кол-во доступных хостов подсети: {net.num_addresses - 2} \n"
                                                 f"Адрес сети: {net.network_address}\n"
                                                 f"Бродкаст: {net.broadcast_address}\n"
                                                 f"Диапазон доступных адресов: {net[1]} - {net[-2]}\n"
)
        except ValueError:
            bot.send_message(pm.chat.id, "Попробуйте другую комбинацию")
            startup(pm)
# преобразование сообщения с ip в переменную, ввод маски сети, передача переменной ip на следующий шаг
def ip_address_handler(pm):
    ip = pm.text
    sent_msg = bot.send_message(pm.chat.id, f"Сеть: {ip} Введите маску в формате CIDR или в обычном виде")
    bot.register_next_step_handler(sent_msg, calc_network, ip)

# Калькулятор сети
def calc_network(pm, ip):
    mask = pm.text
    network = str(ip + '/' + mask)
    bot.send_message(pm.chat.id, f"Ваша сеть:{network}")
    try:
        net = ipaddress.ip_network(network)
        bot.send_message(pm.chat.id, f"Маска и сеть: {net.with_netmask}\n"
                                     f"Адрес сети: {net.network_address}\n"
                                     f"Бродкаст: {net.broadcast_address}\n"
                                     f"Диапазон доступных адресов: {net[1]} - {net[-2]}\n"
                                     f"кол-во доступных хостов: {net.num_addresses - 2} \n")
    except ValueError:
        bot.send_message(pm.chat.id, "Попробуйте другой ip адрес/маску")
        startup(pm)
bot.polling(none_stop=True)
