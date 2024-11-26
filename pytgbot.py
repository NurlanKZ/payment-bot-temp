import os
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
        # member_count = await context.bot.get_chat_member_count(CHANNEL_ID)
        # print(member_count)

        ids = [6758603584, 5947166770, 6466611647, 7092645251, 5520823656, 5956826960, 1287949472, 5614242720, 6765643375, 1425190445, 837041231, 6547018317, 1634087561, 6939905968, 6506577075, 5707279239, 7512820407, 6828228378, 1190692849, 7320032382, 7008173782, 867660472, 6177164722, 6134422115, 7109622879, 1551916111, 5758284511, 6294010466, 7434550062, 7600323393, 2086179719, 6997410304, 7435114850, 1694799926, 2094359263, 5154594415, 6958178892, 7142398617, 7491561943, 6366670827, 1441875516, 5020121669, 7558793785, 6731402242, 6948359765, 1997672999, 5726385006, 6393914545, 1412284728, 7349679323, 5607898962, 5705789590, 5943533507, 1858944706, 5056124188, 6512644307, 6227629414, 1775642171, 6729187922, 5163933849, 1024251348, 1997796314, 1539385226, 1386455987, 7834487802, 1668856445, 6284342573, 7932609501, 1676493833, 1042612119, 6675605837, 7045608928, 5908465838, 7876683655, 5064999684, 7510175508, 7439414948, 6984221369, 6148817866, 1113394114, 6671130836, 1007299635, 1685150951, 6845095637, 2004881578, 6531834183, 5253133098, 1827955409, 7481759680, 2023543256, 7026637659, 6520405649, 6081297933, 5923648132, 6459360772, 6076712261, 7479394304, 2136369254, 5900096352, 5880146492, 6836684451, 7107184317, 1174951709, 6773580934, 6498609448, 2124047401, 6415060483, 1316945589, 2035543996, 6834700693, 7477527660, 7306612509, 6156843797, 5035935391, 6214551591, 6549237282, 5951552212, 6578495997, 6500416598, 5176905920, 6176177145, 7424158872, 7529059572, 2022439286, 5891041291, 1095203735, 6169459708, 5527827286, 6301282528, 6485193722, 5753815116, 6380843071, 5636559311, 6737190544, 5665230142, 7216810794, 6134436957, 7038157190, 6672357197, 5800110063, 6604088972, 1745151337, 7105835809, 7253272071, 6612539410, 1597321444, 5449729517, 5223930291, 6284241949, 7416809862, 7005709612, 7585731431, 6677707030, 6955074557, 2085477013, 6876275875, 6136610058, 6747148759, 6780347661, 1412619183, 1392736376, 6921801578, 6673220552, 6713378120, 1430137545, 6777076596, 7142771389, 6173444002, 7105272199, 5812095426, 7003812144, 6307597795, 6895670703, 6653952549, 5909059139, 1617158850, 1988657259, 7957184970, 5972365024, 6870759684, 1077327448, 2008788753, 6471711035, 7136665357, 5981633250, 5972148966, 7633037356, 7029011837, 6018997927, 7020612943, 7135135355, 6677297104, 6419420466, 6291737702, 1387096071, 804195730, 1087328643, 1450920541, 6733387783, 1621535674, 6605848929, 1946802180, 5481260236, 1389234660, 1967669678, 5703143388, 7332842150, 5601637552, 6486417483, 6998638215, 6332332090, 2009916472, 7280695568, 7687993617, 5425644435, 6267586736, 5853312865, 7417489342, 7363702812, 1880981174, 5937843419, 6449696921, 1285618523, 7097437463, 6501048232, 6269251740, 6553642685, 5684590289, 7350892491, 5158904577, 5016236193, 5614905225, 1713490628, 6146809904, 6584420139, 6300626999, 7087099972, 5195322213, 1296396257, 5023603316, 5757723522, 1160415891, 6354301909, 5655632525, 7954983899, 1163498834, 6267980233, 1181621111, 5929103131, 7100208529, 1911143064, 6562497372, 1243633156, 5911066083, 5731732536, 7271218820, 924035036, 7499789831, 1413367919, 953047753, 6963750130, 6066124680, 6875210192, 6033096844, 6985182682, 7625871878, 1437117362, 1993211131, 6928046308, 2060929749, 1455987446, 6335580886, 1314048815, 1803457268, 1654836395, 5451711445, 7987085046, 5415016225, 6838553751, 6191482569, 7470084042, 1254285352, 6120828839, 5339660114, 1643524253, 6039509685, 1682097930, 6894896647, 1070996020, 5927013638, 5053673471, 1536178820, 6367266859, 5474505318, 6722431202, 2028972191, 6689144134, 6478443686, 6281020663, 7030541463, 5845052383, 6563358788, 5820237207, 6668793758, 1834186308, 6710472841, 1786098246, 6501874278, 6246337264, 5378523080, 5796829828, 6297575864, 6314206908, 6409660488, 1086162738, 6899963373, 5290410596, 1073336058, 5756934526, 7080962945, 7025644562, 5748954347, 5890269796, 5772291017, 5925223414, 1998703908, 1140005556, 8079317500, 6033167976, 7317225189, 6805665196, 1466770036, 6850924452, 8042655811, 7155754417, 1189078712, 6396377284, 7475049218, 5925271451, 1842812059, 1581463467, 6637983861, 7917094937, 6898777600, 6300879105, 5427378668, 5516699818, 1963875908, 5524964846, 1155264143, 1772814109, 6496206374, 1268555002, 7015170315, 1033101867, 5197226422, 5984507263, 5161111701, 7059721668, 6976070783, 6134526322, 1233548282, 6950292211, 5052360573, 6177202066, 7461180173, 7764301350, 7028253388, 5623215664, 6112387862, 6732654956, 6139280205, 6693586164, 6600904663, 6630335002, 6159762516, 6438662895, 7916780344, 2098428898, 6586350157, 6965741318, 6835646514, 7341851134, 1836990868, 6088373857, 6429142319, 6992592325, 5058213210, 6060145884, 7581602368, 1147155122, 1544401997, 6837399370, 2054640729, 5986554878, 6605939704, 5580853167, 7753157386, 6780601968, 7903129383, 1825236671, 6604766933, 5892262684, 6356704585, 7268008704, 5204850744, 6393909515, 5573928847, 6458280300, 6533028287, 6140717963, 7431487711, 1258884968, 1863601863, 5488978511, 6124043432, 6983798009, 5045871056, 1469299673, 5924302390, 410826424, 6517241250, 5543796116, 7287937978, 1378167354, 7175475213, 7936435059, 6986710106, 1225428881, 5781213058, 6944014293, 5286126234, 6847366530, 1228722472, 6143819348, 7453781831, 5061047559, 6828228873, 5502164516, 6619522703, 5489488719, 1790742463, 6151678147, 1997204984, 6214438954, 6374629613, 7348693568, 5375843563, 7218011984, 6393751604, 7058541581, 6601994070, 981386125, 6254190548, 5720478342, 5964331168, 5798152394, 6463003945, 5154027533, 5796494735, 5983570352, 6382084289, 5547351165, 6563697809, 5550255561, 5003260925, 1150163794, 7355645142, 5993834748, 1072201308, 5922293636, 6886501264, 5468206335, 7052201535, 7161923287, 7443542412, 6687348105, 7905803428, 7293550228, 7392530914, 6061264421, 7691043975, 6929359041, 7534082072, 7572587904, 7303636539, 2020900200, 7034928429, 6139241721, 5198525988, 6830224948, 5480684668, 6575045744, 6924251915, 2082595135, 7179608144, 1943252043, 6504973913, 6088954513, 1119545696, 7161738398, 6682695520, 1663823472, 5477707676, 6651079194, 7157874501, 5577321337, 5188342633, 6093144607, 6298895634, 6839441281, 2111265607, 5048431945, 1699250217, 5861488229, 5492592547, 6575678721, 1172709083, 6268255169, 7595767238, 7426016613, 5454202689, 6248515906, 2050203171, 7701845586, 6647738027, 2071558543, 1924765345, 5135661169, 5927990794, 6481329180, 1440846196, 6402087835, 7449536034, 7843608401, 1822275293, 997331670, 5833510969, 5051906468, 6503841545, 6930455567, 6681306582, 1714831345, 6539623155, 1966170563, 5865564547, 5852903165, 7632949671, 1975481099, 6716961917, 5896729054, 6181944481, 6211701170, 6940696186, 7100648763, 6118500588, 2058127800, 5037660370, 5819405520, 7110315338, 6075783646, 5800995890, 5849533106, 6437604550, 6679678661, 6595515509, 5772233763, 1386360960, 7148048363, 5372030430, 6600695486, 6197232349, 5310896213, 5839432490, 7178802791, 1463934888, 6672105079, 6130500805, 6375191511, 7274919126, 6455749257, 5033445542, 6992921517, 5142705405, 6633816189, 6599621674, 6661234395, 7480177287, 6000803089, 6625419577, 5600376096, 6246986434, 7486558799, 6061986580, 7473066504, 6680644293, 7566905536, 6025128888, 7667600163, 6346999495, 7016063206, 5298325452, 5796626972, 5970043174, 6607140467, 1671260426, 7080390926, 2142738443, 5560795185, 5311225777, 6885613681, 6891933268, 6219586567, 6475535862, 7323639401, 6465766959, 6399124143, 5871642716, 8108427577, 5254368581, 2041762909, 6683211606, 6384687408, 7107749222, 5831612622, 1906870090, 6870620343, 5195365886, 6297290027, 6509972039, 5445031591, 6507065500, 5862488783, 7033867549, 6034474054, 6180380547, 5714254370, 5226825575, 6518164026, 6068827043, 6471097297, 2075223867, 7908001112, 7293417972, 5424723935, 7310415548, 7692864122, 6866810978, 6544630232, 6504539614, 6046707871, 1391366856, 7341920513, 6428774717, 1776072913, 5408073129, 5413269606, 6595811550, 1727664330, 1759857668, 7039090180, 7195565936, 7292569558, 7183505339, 6360711216, 5254805300, 5479944116, 7444710304, 5810639466, 6639225150, 6269977047, 7916786919, 7577274191, 5950723910, 6427707057, 1600752363, 7476198809, 5115719344, 6314417788, 7305131906, 6708546768, 1483799023, 6311594267, 7217764862, 7355467990, 7162444268, 6464776666, 1205533006, 6887959915, 5848205163, 7436439963, 7574511762, 7197264098, 5555543059, 7711537384, 6358636721, 5725228421, 7420601716, 6647727833, 5373826464, 7825753294, 5917053712, 5776364348, 7696428722, 7777211291, 1720695426, 5678884396, 5931409177, 6819689602, 1748339734, 7170976508, 7583413923, 6575756736, 7357634329, 6233716740, 5202964654, 6330311515, 5354932694, 7050906829, 5136378841, 7003497982, 1514553040]
        await update.message.reply_text(len(ids))
        # for row in final_result.data:
        #     telegram_user_id = int(row["telegram_user_id"])
        #     await kick_user(telegram_user_id, context)

        # member_count = await context.bot.get_chat_member_count(CHANNEL_ID)
        # print(member_count)

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

    application.run_polling()