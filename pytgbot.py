import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from pypdf_parse import verify_pdf

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID_1 = os.environ.get('ADMIN_ID_1')
ADMIN_ID_2 = os.environ.get('ADMIN_ID_2')
ADMIN_ID_3 = os.environ.get('ADMIN_ID_3')
ADMIN_IDS = [ADMIN_ID_1, ADMIN_ID_2, ADMIN_ID_3]
CHANNEL_ID = os.environ.get('CHANNEL_ID')
PAYMENT_URL = os.environ.get('PAYMENT_URL')
SECONDS_IN_DAY = 86400


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE:            
        await update.message.reply_text("Сәлеметсіз бе! Тарифты таңдаңыз.\n\nЗдравствуйте! Выберите тариф.", 
                                        reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Подписка на МЕСЯЦ", callback_data="30"),
            ],
            [
                InlineKeyboardButton("Подписка на ДЕНЬ", callback_data="1"),
            ],]))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button clicks."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    match query.data:
        case "30":
            await query.edit_message_text(text="Срок подписки: 30 дней\n\nСтоимость: 1499 тг", 
                                    reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💳 ОПЛАТИТЬ", callback_data="130"),
                ],
                [
                    InlineKeyboardButton("⬅️ НАЗАД", callback_data="0"),
                ],]))
        case "1":
            await query.edit_message_text(text="Срок подписки: 1 день\n\nСтоимость: 499 тг", 
                                    reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💳 ОПЛАТИТЬ", callback_data="101"),
                ],
                [
                    InlineKeyboardButton("⬅️ НАЗАД", callback_data="0"),
                ],]))
        case "0":
            await query.edit_message_text(text="Сәлеметсіз бе! Тарифты таңдаңыз.\n\nЗдравствуйте! Выберите тариф.", 
                                            reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Подписка на МЕСЯЦ", callback_data="30"),
                ],
                [
                    InlineKeyboardButton("Подписка на ДЕНЬ", callback_data="1"),
                ],]))
        case "130":
            await query.edit_message_text(text="Способ оплаты: Kaspi\n\nК оплате: 1499 тг", 
                                            reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ ПЕРЕЙТИ К ОПЛАТЕ", url=PAYMENT_URL),
                ],
                [
                    InlineKeyboardButton("🧾 Я ОПЛАТИЛ(A)", callback_data="230"),
                ],
                [
                    InlineKeyboardButton("⬅️ НАЗАД", callback_data="30"),
                ],]))
        case "101":
            await query.edit_message_text(text="Способ оплаты: Kaspi\n\nК оплате: 499 тг", 
                                            reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ ПЕРЕЙТИ К ОПЛАТЕ", url=PAYMENT_URL),
                ],
                [
                    InlineKeyboardButton("🧾 Я ОПЛАТИЛ(A)", callback_data="201"),
                ],
                [
                    InlineKeyboardButton("⬅️ НАЗАД", callback_data="1"),
                ],]))
        case "230":
            await query.edit_message_text(text="Төлемді растайтын құжатты PDF форматында жіберуіңізді өтінеміз.\n\nПожалуйста, отправьте квитанцию о платеже в формате PDF.", 
                                    reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⬅️ НАЗАД", callback_data="130"),
                ],]))
        case "201":
            await query.edit_message_text(text="Төлемді растайтын құжатты PDF форматында жіберуіңізді өтінеміз.\n\nПожалуйста, отправьте квитанцию о платеже в формате PDF.", 
                                    reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⬅️ НАЗАД", callback_data="101"),
                ],]))

async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == 'private' and str(update.message.from_user.id) in ADMIN_IDS:
        db = sqlite3.connect('records_and_tasks.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Records ORDER BY timestamp DESC")
        records = cursor.fetchall()

        # save records to an excel file and send it
        df = pd.DataFrame(records)
        file_name = 'verification_logs.xlsx'
        df.to_excel(file_name, index=False)
        with open(file_name, 'rb') as f:
            await context.bot.send_document(update.message.chat.id, f, caption="Verification logs.")
        db.close()

async def get_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE and str(update.message.from_user.id) in ADMIN_IDS:
        db = sqlite3.connect('records_and_tasks.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Tasks")
        tasks = cursor.fetchall()

        # save tasks to an excel file and send it
        df = pd.DataFrame(tasks)
        file_name = 'scheduled_tasks.xlsx'
        df.to_excel(file_name, index=False)
        with open(file_name, 'rb') as f:
            await context.bot.send_document(update.message.chat.id, f, caption="Scheduled tasks.")
        db.close()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE:
        await update.message.reply_text("Сәлеметсіз бе! Тарифты таңдаңыз.\n\nЗдравствуйте! Выберите тариф.", 
                                        reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Подписка на МЕСЯЦ", callback_data="30"),
            ],
            [
                InlineKeyboardButton("Подписка на ДЕНЬ", callback_data="1"),
            ],]))

async def kick_user(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.ban_chat_member(CHANNEL_ID, context.job.name)
    await context.bot.unban_chat_member(CHANNEL_ID, context.job.name)

async def remind_user(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(int(context.job.name), f"Напоминаем, что ваша подписка на официальный канал ALPHA TEAM истекает через {context.job.data} час(а).", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Обновить подписку", callback_data="0"),
            ],]))
    if context.job.data == 24:
        context.job_queue.run_once(remind_user, 60*60, name=context.job.name, data=1)

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE:
        # Check if the received document is a PDF
        document = update.message.document
        if document and document.mime_type == 'application/pdf':
            response = await update.message.reply_text("Файл жүктелуде...\nФайл загружается...")
            
            file = await context.bot.get_file(document.file_id)
            downloaded_file = await file.download_as_bytearray()

            # Verify the PDF
            result = verify_pdf(downloaded_file)
            if result['approved']:
                # Schedule user kick based on result['days_added']

                # CLEAR OLD KICKs and reminders
                # Check to remove previously scheduled kicks
                current_jobs = context.job_queue.get_jobs_by_name(str(update.message.from_user.id))
                if current_jobs:
                    for job in current_jobs:
                        job.schedule_removal()
                # also clear tasks db
                db = sqlite3.connect('records_and_tasks.db')
                cursor = db.cursor()
                cursor.execute('''
                    DELETE FROM Tasks WHERE telegram_user_id = ?
                ''', (str(update.message.from_user.id),))

                # ADD NEW KICK
                # Add to tasks db
                cursor.execute('''
                    INSERT INTO Tasks (telegram_user_id, sub_expiry_time) VALUES (?, ?)
                ''', (str(update.message.from_user.id), update.message.date.timestamp() + result['days_added']*SECONDS_IN_DAY))
                db.commit()
                # Schedule a job
                context.job_queue.run_once(kick_user, result['days_added']*SECONDS_IN_DAY, name=str(update.message.from_user.id))
                reminder_hours = -(-result['days_added']*4 // 5) # Used a Math.ceil alternative here
                context.job_queue.run_once(remind_user, reminder_hours*3600, name=str(update.message.from_user.id), data=reminder_hours)

                # Generate an invite link
                generated_link = await context.bot.create_chat_invite_link(CHANNEL_ID, expire_date=int(update.message.date.timestamp())+result['days_added']*SECONDS_IN_DAY, member_limit=1)
                invite_link = generated_link.invite_link
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=response.message_id,
                    text=f"Міне, сіздің бір реттік сілтемеңіз. Оны басқаларға жібермеңіз.\n\nВот ваша одноразовая ссылка. Не отправляйте ее третьим лицам.\n\n{invite_link}"
                )

                # Insert data into the table
                cursor.execute('''
                    INSERT INTO Records (telegram_user_id, telegram_username, timestamp, date_time, company_name, vendor_id, payment, transaction_id, customer_name, transaction_time, status, reason, invite_link)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (update.message.from_user.id, 
                      update.message.from_user.username,
                      update.message.date.timestamp(), 
                      (update.message.date + timedelta(hours=5)).strftime('%d-%m-%Y %H:%M:%S'), 
                      result['company_name'],
                      result['vendor_id'],
                      result['payment'],
                      result['transaction_id'],
                      result['customer_name'],
                      result['transaction_time'],
                      'Approved',
                      result['reason'],
                      invite_link))
                db.commit()
                db.close()
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=response.message_id,
                    text="Сіз жіберген PDF-файл тексеруден өтпеді.\n\nОтправленный вами PDF-файл не прошел проверку.")

                # Insert data into the table
                db = sqlite3.connect('records_and_tasks.db')
                cursor = db.cursor()
                cursor.execute('''
                    INSERT INTO Records (telegram_user_id, telegram_username, timestamp, date_time, company_name, vendor_id, payment, transaction_id, customer_name, transaction_time, status, reason, invite_link)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                ''', (update.message.from_user.id, 
                      update.message.from_user.username,
                      update.message.date.timestamp(), 
                      (update.message.date + timedelta(hours=5)).strftime('%d-%m-%Y %H:%M:%S'), 
                      result['company_name'],
                      result['vendor_id'],
                      result['payment'],
                      result['transaction_id'],
                      result['customer_name'],
                      result['transaction_time'],
                      'Rejected',
                      result['reason'],
                      'No link'))
                db.commit()
                db.close()
        else:
            await update.message.reply_text("Төлемді растайтын құжатты PDF форматында жіберуіңізді өтінеміз.\n\nПожалуйста, отправьте квитанцию о платеже в формате PDF.")

if __name__ == '__main__':
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Connect to the database (creates if it doesn't exist)
    db = sqlite3.connect('records_and_tasks.db')
    cursor = db.cursor()

    # Create a table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Records (
            id INTEGER PRIMARY KEY,
            telegram_user_id INTEGER,
            telegram_username TEXT,
            timestamp DATETIME,
            date_time TEXT,
            company_name TEXT,
            vendor_id TEXT,
            payment TEXT,
            transaction_id TEXT,
            customer_name TEXT,
            transaction_time TEXT,
            status TEXT,
            reason TEXT,
            invite_link TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY,
            telegram_user_id TEXT,
            sub_expiry_time DATETIME
        )
    ''')

    cursor.execute('''
            INSERT INTO Records (telegram_user_id, telegram_username, timestamp, date_time, company_name, vendor_id, payment, transaction_id, customer_name, transaction_time, status, reason, invite_link)
            SELECT ?,?,?,?,?,?,?,?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM Records);
        ''', (0, 
                'Username',
                2147483647, 
                'Time of verification', 
                'Company name', 
                'Vendor ID', 
                'Payment', 
                'Transaction ID', 
                'Customer name', 
                'Time of transaction',
                'Status', 
                'Reason', 
                'Invite Link'))
    db.commit()

    cursor.execute("SELECT telegram_user_id, sub_expiry_time FROM Tasks")
    tasks = cursor.fetchall()
    for task in tasks:
        kick_time = task[1] - int(datetime.now().timestamp())
        if kick_time > 0:
            application.job_queue.run_once(kick_user, kick_time, name=task[0])
            if kick_time > SECONDS_IN_DAY:
                application.job_queue.run_once(remind_user, kick_time - SECONDS_IN_DAY, name=task[0], data=24)
            elif kick_time > 3600:
                application.job_queue.run_once(remind_user, kick_time - 3600, name=task[0], data=1)

    db.close()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('logs', get_logs))
    application.add_handler(CommandHandler('tasks', get_tasks))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_docs))

    application.run_polling()