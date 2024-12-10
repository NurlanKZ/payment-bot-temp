import os
import json
import pandas as pd
from supabase import create_client, Client
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
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
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
        response = supabase.table("records").select("*").order("timestamp", desc=True).limit(500).execute()
        records = response.data

        # save records to an excel file and send it
        df = pd.DataFrame(records)
        file_name = 'verification_logs.xlsx'
        df.to_excel(file_name, index=False)
        with open(file_name, 'rb') as f:
            await context.bot.send_document(update.message.chat.id, f, caption="Verification logs.")

async def get_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE and str(update.message.from_user.id) in ADMIN_IDS:
        response = supabase.table("tasks").select("*").limit(500).execute()
        tasks = response.data

        # save tasks to an excel file and send it
        df = pd.DataFrame(tasks)
        file_name = 'scheduled_tasks.xlsx'
        df.to_excel(file_name, index=False)
        with open(file_name, 'rb') as f:
            await context.bot.send_document(update.message.chat.id, f, caption="Scheduled tasks.")

async def ban_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE:         
        with open('a.json', 'r') as file:
            data = json.load(file)

        # Extract telegram_user_id values and convert them to integers
        telegram_user_ids = [entry["telegram_user_id"] for entry in data]

        for id in telegram_user_ids:
            await kick_user_by_id(id, context)

        member_count = await context.bot.get_chat_member_count(CHANNEL_ID)
        await update.message.reply_text(member_count)

async def get_member_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE:         
        member_count = await context.bot.get_chat_member_count(CHANNEL_ID)
        await update.message.reply_text(member_count)

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

async def kick_user_by_id(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.ban_chat_member(CHANNEL_ID, user_id)
    await context.bot.unban_chat_member(CHANNEL_ID, user_id)

async def remind_user(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(int(context.job.name), f"Напоминаем, что ваша подписка на официальный канал ALPHA TEAM истекает через {context.job.data} час(а).", reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Обновить подписку", callback_data="0"),
            ],]))
    if context.job.data == 24:
        context.job_queue.run_once(remind_user, SECONDS_IN_DAY-3600, name=context.job.name, data=1)

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.chat.type == update.message.chat.PRIVATE:
        # Check if the received document is a PDF
        document = update.message.document
        if document and document.mime_type == 'application/pdf':
            response = await update.message.reply_text("Файл жүктелуде...\nФайл загружается...")
            
            file = await context.bot.get_file(document.file_id)
            downloaded_file = await file.download_as_bytearray()

            # Verify the PDF
            result = verify_pdf(downloaded_file, supabase)
            if result['approved']:
                # Schedule user kick based on result['days_added']

                # CLEAR OLD KICKs and reminders
                # Check to remove previously scheduled kicks
                current_jobs = context.job_queue.get_jobs_by_name(str(update.message.from_user.id))
                if current_jobs:
                    for job in current_jobs:
                        job.schedule_removal()
                # also clear tasks db
                # CLEAR OLD KICKs and reminders
                # Check to remove previously scheduled kicks
                current_tasks = supabase.table("tasks").select("*").eq("telegram_user_id", str(update.message.from_user.id)).execute()
                if current_tasks.data:
                    for task in current_tasks.data:
                        supabase.table("tasks").delete().match({"id": task["id"]}).execute()

                # ADD NEW KICK
                # Add to tasks db
                supabase.table("tasks").insert({"telegram_user_id": str(update.message.from_user.id), "sub_expiry_time": int(update.message.date.timestamp() + result['days_added']*SECONDS_IN_DAY)}).execute()
                # Schedule a job
                seconds_added = result['days_added']*SECONDS_IN_DAY
                context.job_queue.run_once(kick_user, seconds_added, name=str(update.message.from_user.id))
                reminder_hours = -(-result['days_added']*4 // 5) # Used a Math.ceil alternative here
                context.job_queue.run_once(remind_user, seconds_added-reminder_hours*3600, name=str(update.message.from_user.id), data=reminder_hours)

                # Generate an invite link
                generated_link = await context.bot.create_chat_invite_link(CHANNEL_ID, expire_date=int(update.message.date.timestamp())+result['days_added']*SECONDS_IN_DAY, member_limit=1)
                invite_link = generated_link.invite_link
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=response.message_id,
                    text=f"Міне, сіздің бір реттік сілтемеңіз. Оны басқаларға жібермеңіз.\n\nВот ваша одноразовая ссылка. Не отправляйте ее третьим лицам.\n\n{invite_link}"
                )

                # Insert data into the table
                data = {
                    "telegram_user_id": update.message.from_user.id,
                    "telegram_username": update.message.from_user.username,
                    "timestamp": int(update.message.date.timestamp()),
                    "date_time": (update.message.date + timedelta(hours=5)).strftime('%d-%m-%Y %H:%M:%S'),
                    "company_name": result['company_name'],
                    "vendor_id": result['vendor_id'],
                    "payment": result['payment'],
                    "transaction_id": result['transaction_id'],
                    "customer_name": result['customer_name'],
                    "transaction_time": result['transaction_time'],
                    "status": 'Approved',
                    "reason": result['reason'],
                    "invite_link": invite_link
                }
                response = supabase.table("records").insert(data).execute()
            else:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=response.message_id,
                    text="Сіз жіберген PDF-файл тексеруден өтпеді.\n\nОтправленный вами PDF-файл не прошел проверку.")

                # Insert data into the table
                data = {
                    "telegram_user_id": update.message.from_user.id,
                    "telegram_username": update.message.from_user.username,
                    "timestamp": int(update.message.date.timestamp()),
                    "date_time": (update.message.date + timedelta(hours=5)).strftime('%d-%m-%Y %H:%M:%S'),
                    "company_name": result['company_name'],
                    "vendor_id": result['vendor_id'],
                    "payment": result['payment'],
                    "transaction_id": result['transaction_id'],
                    "customer_name": result['customer_name'],
                    "transaction_time": result['transaction_time'],
                    "status": 'Rejected',
                    "reason": result['reason'],
                    "invite_link": 'No link'
                }
                response = supabase.table("records").insert(data).execute()
        else:
            await update.message.reply_text("Төлемді растайтын құжатты PDF форматында жіберуіңізді өтінеміз.\n\nПожалуйста, отправьте квитанцию об оплате в формате PDF.")

if __name__ == '__main__':
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    response = supabase.table("tasks").select("telegram_user_id", "sub_expiry_time").execute()
    tasks = response.data
    for task in tasks:
        kick_time = task.get("sub_expiry_time") - int(datetime.now().timestamp())
        if kick_time > 0:
            application.job_queue.run_once(kick_user, kick_time, name=task.get("telegram_user_id"))
            if kick_time > SECONDS_IN_DAY:
                application.job_queue.run_once(remind_user, kick_time - SECONDS_IN_DAY, name=task.get("telegram_user_id"), data=24)
            elif kick_time > 3600:
                application.job_queue.run_once(remind_user, kick_time - 3600, name=task.get("telegram_user_id"), data=1)

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('logs', get_logs))
    application.add_handler(CommandHandler('tasks', get_tasks))
    application.add_handler(CommandHandler('membercount', get_member_count))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_docs))
    application.add_handler(CommandHandler('banwave', ban_users))
    application.add_handler(CommandHandler('kickinactive', kick_inactive_users))