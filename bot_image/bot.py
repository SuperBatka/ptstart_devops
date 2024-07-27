import logging
import re
import paramiko
import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler


logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

load_dotenv()


host = os.getenv("RM_HOST")
port = os.getenv("RM_PORT")
username = os.getenv("RM_USER")
password = os.getenv("RM_PASSWORD")
usernameDB = os.getenv("DB_USER")
passwordDB = os.getenv("DB_PASSWORD")
hostDB = os.getenv("DB_HOST")
portDB = os.getenv("DB_PORT")
databaseDB = os.getenv("DB_DATABASE")
TOKEN = os.getenv("TOKEN")


def ssh_runcmd(command):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read().decode() + stderr.read().decode()
        data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
        return data
    except (Exception, Error) as error:
        return 'Ошибка подключения по SSH'
    finally:
        client.close()

def get_release(update: Update, context):
    cmd = 'lsb_release -a' 
    update.message.reply_text(ssh_runcmd(cmd))

def get_uname(update: Update, context):
    cmd = 'uname -mrn'
    update.message.reply_text(ssh_runcmd(cmd))

def get_uptime(update: Update, context):
    cmd = 'uptime' 
    update.message.reply_text(ssh_runcmd(cmd))

def get_df(update: Update, context):
    cmd = 'df -H' 
    update.message.reply_text(ssh_runcmd(cmd))

def get_free(update: Update, context):
    cmd = 'free -H' 
    update.message.reply_text(ssh_runcmd(cmd))

def get_mpstat(update: Update, context):
    cmd = 'mpstat' 
    update.message.reply_text(ssh_runcmd(cmd))

def get_w(update: Update, context):
    cmd = 'w' 
    update.message.reply_text(ssh_runcmd(cmd))

def get_auth(update: Update, context):
    cmd = 'last | head -n 10' 
    update.message.reply_text(ssh_runcmd(cmd))

def get_critical(update: Update, context):
    cmd = 'journalctl -p crit -n 5'
    update.message.reply_text(ssh_runcmd(cmd))

def get_ps(update: Update, context):
    cmd = 'ps'
    update.message.reply_text(ssh_runcmd(cmd))

def get_ss(update: Update, context):
    cmd = 'ss -tulnp'
    update.message.reply_text(ssh_runcmd(cmd))

  

def get_services(update: Update, context):
    cmd = "systemctl --type service"
    update.message.reply_text(ssh_runcmd(cmd))

def get_apt_list(update: Update, context):
    user_input = update.message.text 
    cmd = ''
    if user_input == 'ALL':
        cmd = 'dpkg --list | tail -n 10'
    else:
        cmd = 'dpkg -s '+user_input
    
    update.message.reply_text(ssh_runcmd(cmd)) 
    return ConversationHandler.END

def get_repl_logs(update: Update, context):
    #cmd = "cat /var/log/postgresql/* | grep repl | tail -n 20"
    cmd = "docker logs db-image 2>&1 | grep repl | tail -n 20"
    update.message.reply_text(ssh_runcmd(cmd))

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def AskAddingEmailToDB(update: Update, context):
    user_input = update.message.text
    if user_input == "ДА":
       connection = None
       try:
           connection = psycopg2.connect(user=usernameDB, password=passwordDB, host=hostDB, port=portDB, database=databaseDB)

           cursor = connection.cursor()
           listEmails = context.user_data["emails"].split('\n')
           listEmails = listEmails[:-1]
           for i in listEmails:
               cursor.execute("INSERT INTO emails (email) VALUES (%s);",(i,))
           connection.commit()
           logging.info("Команда успешно выполнена")
           update.message.reply_text( "Почтовые адреса записаны в базу данных")
       except (Exception, Error) as error:
           logging.error("Ошибка при работе с PostgreSQL: %s", error)
           update.message.reply_text( "Ошибка при работе с базой данных. Почтовые адреса не записаны в базу данных")
       finally:
            if connection is not None:
               cursor.close()
               connection.close()
               logging.info("Соединение с PostgreSQL закрыто")
            return ConversationHandler.END
    elif user_input == "НЕТ":
       update.message.reply_text( "Почтовые адреса не записаны в базу данных")
       return ConversationHandler.END
    else:
       update.message.reply_text( "Введен некорректный параметр! Введите 'ДА' или 'НЕТ'")
       return "AskAddingEmailToDB"

def AskAddingPhoneToDB(update: Update, context):
    user_input = update.message.text
    if user_input == "ДА":
       connection = None
       try:
           connection = psycopg2.connect(user=usernameDB, password=passwordDB, host=hostDB, port=portDB, database=databaseDB)

           cursor = connection.cursor()
           ListPhoneNumbers = context.user_data["phoneNumbers"].split('\n')
           ListPhoneNumbers = ListPhoneNumbers[:-1]
           for i in ListPhoneNumbers:
               cursor.execute("INSERT INTO phone_number (phone) VALUES (%s);",(i,))
           connection.commit()
           logging.info("Команда успешно выполнена")
           update.message.reply_text( "Номера телефонов записаны в базу данных")
       except (Exception, Error) as error:
           logging.error("Ошибка при работе с PostgreSQL: %s", error)
           update.message.reply_text( "Ошибка при работе с базой данных. Номера телефонов не записаны в базу данных")
       finally:
            if connection is not None:
               cursor.close()
               connection.close()
               logging.info("Соединение с PostgreSQL закрыто")
            return ConversationHandler.END
    elif user_input == "НЕТ":
       update.message.reply_text( "Номера телефонов не записаны в базу данных")
       return ConversationHandler.END
    else:
       update.message.reply_text( "Введен некорректный параметр! Введите 'ДА' или 'НЕТ'")
       return "AskAddingPhoneToDB"

def helpCommand(update: Update, context):
    update.message.reply_text('Доступные команды:\n /help\n/find_phone_number\n/find_email\n/verify_password')

def findAptListCommand(update: Update, context):
    update.message.reply_text('Введите ALL для поиска всех пакетов, или имя пакета для поиска конкретного ')
    return 'get_apt_list'

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'findPhoneNumbers'


def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email адресов: ')

    return 'findEmails'

def checkPasswordCommand(update: Update, context):
    update.message.reply_text('введите пароль для проверки сложности: ')

    return 'checkPassword'

def findPhoneNumbers (update: Update, context):
    user_input = update.message.text 

    phoneNumRegex = re.compile(r'(8-\d{3}-\d{3}-\d{2}-\d{2})|(8\d{10})|(8\(\d{3}\)\d{7})|(8 \d{3} \d{3} \d{2} \d{2})|(8 \(\d{3}\) \d{3} \d{2} \d{2})') 

    phoneNumberList = phoneNumRegex.findall(user_input) 

    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    
    phoneNumbers = '' 
    
    for i in range(len(phoneNumberList)):
        phoneNumbers +=f"{''.join(phoneNumberList[i])}\n"

    context.user_data["phoneNumbers"] = phoneNumbers
    update.message.reply_text(phoneNumbers) 
    update.message.reply_text("Добавить найденные данные в БД? ДА/НЕТ")
    return "AskAddingPhoneToDB" 


def findEmails (update: Update, context):
    user_input = update.message.text 
    emailRegex = re.compile(r'[\w\.-]+@[\w\.-]+\.[\w]+') 

    emailList = emailRegex.findall(user_input) 

    if not emailList: 
        update.message.reply_text('Email не найдены')
        return ConversationHandler.END
    
    emails = '' 
    for i in range(len(emailList)):
        emails += f'{emailList[i]}\n' 
    context.user_data["emails"] = emails    
    update.message.reply_text(emails) 
    update.message.reply_text("Добавить найденные данные в БД? ДА/НЕТ")
    return "AskAddingEmailToDB" 

def checkPassword(update: Update, context):
    user_input = update.message.text
    capitalRegex = re.compile('[A-Z]')
    lowerRegex = re.compile('[a-z]')
    numberRegex = re.compile(r'\d')
    specialsRegex = re.compile(r'!@#$%^&*()')
    if len(user_input)< 8:
        update.message.reply_text("Пароль меньше 8 символов")
        return ConversationHandler.END
    capitals = capitalRegex.findall(user_input)
    if not capitals:
        update.message.reply_text("Пароль не содержит заглавных букв")
        return ConversationHandler.END
    lowers = lowerRegex.findall(user_input)
    if not lowers:
        update.message.reply_text("Пароль не содержит строчных букв")
        return ConversationHandler.END
    numbers = numberRegex.findall(user_input)
    if not numbers:
        update.message.reply_text("Пароль не содержит цифр")
        return ConversationHandler.END
    specials = specialsRegex.findall(user_input)
    if not specials:
        update.message.reply_text("Пароль не содержит спецсимволов")
        return ConversationHandler.END
    update.message.reply_text("Пароль сложный")
    return ConversationHandler.END


def get_emails(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=usernameDB, password=passwordDB, host=hostDB, port=portDB, database=databaseDB)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        logging.info("Команда успешно выполнена")
        update.message.reply_text(data)
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def get_phone_numbers(update: Update, context):
    connection = None
    try:
        connection = psycopg2.connect(user=usernameDB, password=passwordDB, host=hostDB, port=portDB, database=databaseDB)

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone_number;")
        data = cursor.fetchall()
        logging.info("Команда успешно выполнена")
        update.message.reply_text(data)
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def echo(update: Update, context):
    update.message.reply_text("Для вывода доступных команд введите /help")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'AskAddingPhoneToDB':[MessageHandler(Filters.text, AskAddingPhoneToDB)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'AskAddingEmailToDB': [MessageHandler(Filters.text & ~Filters.command, AskAddingEmailToDB)],
        },
        fallbacks=[]
    )

    convHandlerCheckPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', checkPasswordCommand)],
        states={
            'checkPassword': [MessageHandler(Filters.text & ~Filters.command, checkPassword)],
        },
        fallbacks=[]
    )

    convHandlerFindAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', findAptListCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )
		
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auth", get_auth))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerCheckPassword)
    dp.add_handler(convHandlerFindAptList)	
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	
    updater.start_polling()

	
    updater.idle()


if __name__ == '__main__':
    main()