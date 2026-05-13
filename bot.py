import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone, timedelta
from flask import Flask
from threading import Thread

# =========================================================
# Flask (Render / UptimeRobot)
# =========================================================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_web():
    app.run(
        host="0.0.0.0",
        port=10000
    )

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# =========================================================
# TOKEN
# =========================================================
TOKEN = os.getenv("TOKEN")

# =========================================================
# サーバーID
# =========================================================
GUILD_ID = 1400465999744073770

# =========================================================
# 金庫履歴チャンネルID
# =========================================================
LOG_CHANNEL_ID = 1502441375927500901

# =========================================================
# Intents
# =========================================================
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

tree = bot.tree

# =========================================================
# ファイル
# =========================================================
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AWAKE_FILE = os.path.join(
    BASE_DIR,
    "awake_data.json"
)

INVENTORY_FILE = os.path.join(
    BASE_DIR,
    "inventory_data.json"
)

# =========================================================
# 起床データ
# =========================================================
awake_users = {}

life_panel_message_id = None
life_panel_channel_id = None

# =========================================================
# 金庫 / 在庫
# =========================================================
gang_balance = 0
dirty_balance = 0

inventory = {

    "リサセン:IRON": 0,
    "リサセン:PLASTIC": 0,
    "リサセン:COPPER": 0,
    "リサセン:GLASS": 0,
    "リサセン:METALSCRAP": 0,
    "リサセン:RUBBER": 0,
    "リサセン:ALUMINUM": 0,
    "リサセン:STEAL": 0,

    "素材:ガンパウダー": 0,

    "銃器:SCAR": 0,
    "銃器:5,56弾": 0,
    "銃器:UMP": 0,
    "銃器:UZI": 0,
    "銃器:MAC-10": 0,
    "銃器:TEC-9": 0,
    "銃器:PISTOLL": 0,

    "ギャング:スプレー": 0,
    "ギャング:スプレークリーナー": 0,

    "道具:LIGHT-BM-PHONE": 0,
    "道具:BM-PHONE": 0,
    "道具:タブレット": 0,
    "道具:C4": 0,
    "道具:C4EXPLOSIVE": 0,
    "道具:F-C4 BOMB": 0,
    "道具:テルミット": 0,
    "道具:ガスマスク": 0,
    "道具:催涙ガス": 0,
    "道具:カッター": 0,
    "道具:青かばん": 0,
    "道具:DRILL": 0,
    "道具:BIG DRILL": 0,
    "道具:LAPTOP": 0,
    "道具:SPOOFING CARD": 0,
    "道具:Yacht Drill（客船用）": 0,
    "道具:HACKING Device（客船用）": 0,
    "道具:ラジオエンコーダー": 0,
    "道具:USB STICK": 0,
    "道具:HACK USB": 0,
    "道具:TROJAN USB": 0,
    "道具:SCREWDRIVERSET": 0,
    "道具:ロックピック": 0,
    "道具:アドバンスドロックピック": 0,
    "道具:ダッフルバック": 0
}

inventory_panel_message_id = None
inventory_panel_channel_id = None


# =========================================================
# 時間
# =========================================================
def get_now_time():

    jst = timezone(timedelta(hours=9))

    return datetime.now(jst).strftime("%H:%M")


# =========================================================
# 起床保存
# =========================================================
def save_awake_data():

    data = {
        "awake_users": awake_users,
        "life_panel_message_id":
            life_panel_message_id,
        "life_panel_channel_id":
            life_panel_channel_id
    }

    temp_file = AWAKE_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    os.replace(temp_file, AWAKE_FILE)


# =========================================================
# 起床読込
# =========================================================
def load_awake_data():

    global awake_users
    global life_panel_message_id
    global life_panel_channel_id

    if not os.path.exists(AWAKE_FILE):
        return

    try:

        with open(
            AWAKE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read().strip()

            if not text:
                return

            data = json.loads(text)

        awake_users = data.get(
            "awake_users",
            {}
        )

        life_panel_message_id = data.get(
            "life_panel_message_id"
        )

        life_panel_channel_id = data.get(
            "life_panel_channel_id"
        )

    except Exception as e:

        print(f"awake読込エラー: {e}")


# =========================================================
# 在庫保存
# =========================================================
def save_inventory_data():

    data = {
        "gang_balance": gang_balance,
        "dirty_balance": dirty_balance,
        "inventory": inventory,
        "inventory_panel_message_id":
            inventory_panel_message_id,
        "inventory_panel_channel_id":
            inventory_panel_channel_id
    }

    temp_file = INVENTORY_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    os.replace(temp_file, INVENTORY_FILE)

# =========================================================
# 在庫読込
# =========================================================
def load_inventory_data():

    global gang_balance
    global dirty_balance
    global inventory
    global inventory_panel_message_id
    global inventory_panel_channel_id

    if not os.path.exists(INVENTORY_FILE):
        return

    try:

        with open(
            INVENTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            text = f.read().strip()

            if not text:
                return

            data = json.loads(text)

        gang_balance = data.get(
            "gang_balance",
            0
        )

        dirty_balance = data.get(
            "dirty_balance",
            0
        )

        inventory = data.get(
            "inventory",
            inventory
        )

        inventory_panel_message_id = data.get(
            "inventory_panel_message_id"
        )

        inventory_panel_channel_id = data.get(
            "inventory_panel_channel_id"
        )

    except Exception as e:

        print(f"inventory読込エラー: {e}")


# =========================================================
# BOTステータス
# =========================================================
async def update_bot_presence():

    count = len(awake_users)

    if count > 0:

        status = discord.Status.online

        activity = discord.CustomActivity(
            name=f"🌆 起床中: {count}人"
        )

    else:

        status = discord.Status.idle

        activity = discord.CustomActivity(
            name="🌙 誰も起きていません"
        )

    await bot.change_presence(
        status=status,
        activity=activity
    )


# =========================================================
# 起床Embed
# =========================================================
def create_life_embed():

    if awake_users:

        text = ""

        for uid, info in awake_users.items():

            text += (
                f"🟢 <@{uid}> "
                f"[{info['crime']}] "
                f"({info['wake_time']}〜)\n"
            )

    else:

        text = "🌙 現在誰も起きていません"

    embed = discord.Embed(
        title="🌆 起床パネル",
        description=text,
        color=0x2ecc71
    )

    embed.add_field(
        name="起床人数",
        value=f"{len(awake_users)}人",
        inline=False
    )

    return embed


# =========================================================
# 在庫Embed
# =========================================================
def create_inventory_embed():

    stock_text = ""

    for item, amount in inventory.items():

        stock_text += (
            f"📦 {item} × {amount}\n"
        )

    embed = discord.Embed(
        title="🏦 ギャング倉庫",
        color=0x2b2d31
    )

    embed.add_field(
        name="💰 ギャング金庫残高",
        value=f"```${gang_balance:,}```",
        inline=False
    )

    embed.add_field(
        name="🩸 ダーティー残高",
        value=f"```${dirty_balance:,}```",
        inline=False
    )

    embed.add_field(
        name="📦 在庫",
        value=f"```{stock_text}```",
        inline=False
    )

    return embed


# =========================================================
# 起床パネル更新
# =========================================================
async def update_life_panel():

    await update_bot_presence()

    if life_panel_message_id is None:
        return

    channel = bot.get_channel(
        life_panel_channel_id
    )

    if channel is None:
        return

    try:

        message = await channel.fetch_message(
            life_panel_message_id
        )

        await message.edit(
            embed=create_life_embed(),
            view=LifePanelView()
        )

    except Exception as e:

        print(e)


# =========================================================
# 在庫パネル更新
# =========================================================
async def update_inventory_panel():

    if inventory_panel_message_id is None:
        return

    channel = bot.get_channel(
        inventory_panel_channel_id
    )

    if channel is None:
        return

    try:

        message = await channel.fetch_message(
            inventory_panel_message_id
        )

        await message.edit(
            embed=create_inventory_embed(),
            view=InventoryView()
        )

    except Exception as e:

        print(e)


# =========================================================
# 金庫ログ
# =========================================================
async def send_gang_log(
    user,
    title,
    amount,
    color,
    note
):

    channel = bot.get_channel(
        LOG_CHANNEL_ID
    )

    if channel is None:
        return

    embed = discord.Embed(
        title=title,
        color=color
    )

    embed.add_field(
        name="実行者",
        value=user.mention,
        inline=False
    )

    embed.add_field(
        name="金額",
        value=f"${amount:,}",
        inline=False
    )

    embed.add_field(
        name="備考",
        value=note,
        inline=False
    )

    embed.add_field(
        name="現在残高",
        value=f"${gang_balance:,}",
        inline=False
    )

    await channel.send(embed=embed)

# =========================================================
# 起床View
# =========================================================
class LifePanelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="街起床/犯罪可",
        style=discord.ButtonStyle.green,
        custom_id="life_crime_on"
    )
    async def crime_on_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        uid = str(interaction.user.id)

        awake_users[uid] = {
            "wake_time": get_now_time(),
            "crime": "犯罪可"
        }

        save_awake_data()

        await update_life_panel()

        await interaction.response.defer()

    @discord.ui.button(
        label="街起床/犯罪不可",
        style=discord.ButtonStyle.red,
        custom_id="life_crime_off"
    )
    async def crime_off_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        uid = str(interaction.user.id)

        awake_users[uid] = {
            "wake_time": get_now_time(),
            "crime": "犯罪不可"
        }

        save_awake_data()

        await update_life_panel()

        await interaction.response.defer()

    @discord.ui.button(
        label="街就寝",
        style=discord.ButtonStyle.blurple,
        custom_id="life_sleep"
    )
    async def sleep_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        uid = str(interaction.user.id)

        if uid in awake_users:
            del awake_users[uid]

        save_awake_data()

        await update_life_panel()

        await interaction.response.defer()


# =========================================================
# 通常入金Modal
# =========================================================
class DepositModal(
    discord.ui.Modal,
    title="ギャング金庫入金"
):

    amount = discord.ui.TextInput(
        label="入金額",
        placeholder="100000"
    )

    note = discord.ui.TextInput(
        label="備考",
        placeholder="例: 売上金 / 回収金",
        required=False,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        global gang_balance

        value = int(self.amount.value)

        gang_balance += value

        save_inventory_data()

        await update_inventory_panel()

        await send_gang_log(
            interaction.user,
            "🟢 ギャング金庫入金",
            value,
            0x2ecc71,
            self.note.value if self.note.value else "なし"
        )

        await interaction.response.defer()


# =========================================================
# 通常出金Modal
# =========================================================
class WithdrawModal(
    discord.ui.Modal,
    title="ギャング金庫出金"
):

    amount = discord.ui.TextInput(
        label="出金額",
        placeholder="50000"
    )

    note = discord.ui.TextInput(
        label="備考",
        placeholder="例: 補填 / 支払い",
        required=False,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        global gang_balance

        value = int(self.amount.value)

        gang_balance -= value

        if gang_balance < 0:
            gang_balance = 0

        save_inventory_data()

        await update_inventory_panel()

        await send_gang_log(
            interaction.user,
            "🔴 ギャング金庫出金",
            value,
            0xe74c3c,
            self.note.value if self.note.value else "なし"
        )

        await interaction.response.defer()


# =========================================================
# ダーティー入金Modal
# =========================================================
class DirtyDepositModal(
    discord.ui.Modal,
    title="ダーティー入金"
):

    amount = discord.ui.TextInput(
        label="入金額",
        placeholder="100000"
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        global dirty_balance

        value = int(self.amount.value)

        dirty_balance += value

        save_inventory_data()

        await update_inventory_panel()

        await interaction.response.defer()

# =========================================================
# ダーティー出金Modal
# =========================================================
class DirtyWithdrawModal(
    discord.ui.Modal,
    title="ダーティー出金"
):

    amount = discord.ui.TextInput(
        label="出金額",
        placeholder="50000"
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        global dirty_balance

        value = int(self.amount.value)

        dirty_balance -= value

        if dirty_balance < 0:
            dirty_balance = 0

        save_inventory_data()

        await update_inventory_panel()

        await interaction.response.defer()


# =========================================================
# 在庫数量Modal
# =========================================================
class StockAmountModal(
    discord.ui.Modal
):

    def __init__(
        self,
        item_name,
        mode
    ):

        super().__init__(
            title=f"{item_name}/{mode}"
        )

        self.item_name = item_name
        self.mode = mode

        self.amount = discord.ui.TextInput(
            label="数量",
            placeholder="10"
        )

        self.add_item(self.amount)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        try:

            value = int(self.amount.value)

        except:

            await interaction.response.send_message(
                "数字を入力してください",
                ephemeral=True
            )
            return

        if self.mode == "入荷":

            inventory[self.item_name] += value

        else:

            inventory[self.item_name] -= value

            if inventory[self.item_name] < 0:
                inventory[self.item_name] = 0

        save_inventory_data()

        await update_inventory_panel()

        await interaction.response.defer()


# =========================================================
# 在庫カテゴリSelect
# =========================================================
class StockSelect(discord.ui.Select):

    def __init__(self, mode):

        self.mode = mode

        options = [
            discord.SelectOption(label="リサセン"),
            discord.SelectOption(label="素材"),
            discord.SelectOption(label="銃器"),
            discord.SelectOption(label="ギャング"),
            discord.SelectOption(label="道具")
        ]

        super().__init__(
            placeholder="カテゴリ選択",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        category = self.values[0]

        category_items = []

        for item in inventory.keys():

            if category == "銃器":

                if (
                    item.startswith("銃器:")
                    or item.startswith("銃器")
                ):

                    category_items.append(item)

            else:

                if item.startswith(f"{category}:"):

                    category_items.append(item)

        # =====================================
        # Discord25件制限
        # =====================================
        category_items = category_items[:25]

        await interaction.response.send_message(
            "商品選択",
            view=ItemView(
                category_items,
                self.mode
            )
        )

        # カテゴリメッセージ削除
        await interaction.message.delete()


# =========================================================
# 商品Select
# =========================================================
class ItemSelect(discord.ui.Select):

    def __init__(
        self,
        items,
        mode
    ):

        self.mode = mode

        options = []

        for item in items:

            options.append(
                discord.SelectOption(
                    label=item,
                    description=f"現在: {inventory[item]}個"
                )
            )

        super().__init__(
            placeholder="商品選択",
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_modal(
            StockAmountModal(
                self.values[0],
                self.mode
            )
        )

        # 商品リストメッセージ削除
        await interaction.message.delete()

# =========================================================
# 商品View
# =========================================================
class ItemView(discord.ui.View):

    def __init__(
        self,
        items,
        mode
    ):

        super().__init__(timeout=60)

        self.add_item(
            ItemSelect(
                items,
                mode
            )
        )


# =========================================================
# 在庫View
# =========================================================
class StockView(discord.ui.View):

    def __init__(self, mode):

        super().__init__(timeout=60)

        self.add_item(
            StockSelect(mode)
        )


# =========================================================
# 在庫View
# =========================================================
class InventoryView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="ギャング金庫入金",
        style=discord.ButtonStyle.green,
        custom_id="gang_deposit",
        row=0
    )
    async def deposit_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            DepositModal()
        )

    @discord.ui.button(
        label="ギャング金庫出金",
        style=discord.ButtonStyle.red,
        custom_id="gang_withdraw",
        row=0
    )
    async def withdraw_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            WithdrawModal()
        )

    @discord.ui.button(
        label="ダーティー入金",
        style=discord.ButtonStyle.green,
        custom_id="dirty_deposit",
        row=0
    )
    async def dirty_deposit_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            DirtyDepositModal()
        )

    @discord.ui.button(
        label="ダーティー出金",
        style=discord.ButtonStyle.red,
        custom_id="dirty_withdraw",
        row=0
    )
    async def dirty_withdraw_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            DirtyWithdrawModal()
        )

    @discord.ui.button(
        label="在庫/入荷",
        style=discord.ButtonStyle.green,
        custom_id="stock_add",
        row=1
    )
    async def stock_add_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "カテゴリ選択",
            view=StockView("入荷"),
            ephemeral=True
        )

    @discord.ui.button(
        label="在庫/取出",
        style=discord.ButtonStyle.red,
        custom_id="stock_remove",
        row=1
    )
    async def stock_remove_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "カテゴリ選択",
            view=StockView("取出"),
            ephemeral=True
        )

# =========================================================
# /lifepanel
# =========================================================
@tree.command(
    name="lifepanel",
    description="起床パネル",
    guild=discord.Object(id=GUILD_ID)
)
async def lifepanel(
    interaction: discord.Interaction
):

    global life_panel_message_id
    global life_panel_channel_id

    await interaction.response.send_message(
        embed=create_life_embed(),
        view=LifePanelView()
    )

    message = await interaction.original_response()

    life_panel_message_id = message.id
    life_panel_channel_id = message.channel.id

    save_awake_data()

    await update_bot_presence()


# =========================================================
# /inventorypanel
# =========================================================
@tree.command(
    name="inventorypanel",
    description="ギャング金庫パネル",
    guild=discord.Object(id=GUILD_ID)
)
async def inventorypanel(
    interaction: discord.Interaction
):

    global inventory_panel_message_id
    global inventory_panel_channel_id

    await interaction.response.send_message(
        embed=create_inventory_embed(),
        view=InventoryView()
    )

    message = await interaction.original_response()

    inventory_panel_message_id = message.id
    inventory_panel_channel_id = message.channel.id

    save_inventory_data()


# =========================================================
# 起動
# =========================================================
@bot.event
async def on_ready():

    load_awake_data()
    load_inventory_data()

    bot.add_view(LifePanelView())
    bot.add_view(InventoryView())

    try:

        guild = discord.Object(
            id=GUILD_ID
        )

        synced = await tree.sync(
            guild=guild
        )

        print(f"同期完了: {len(synced)}")

    except Exception as e:

        print(f"syncエラー: {e}")

    print("===================")
    print(f"ログイン完了: {bot.user}")
    print("===================")

    await update_life_panel()
    await update_inventory_panel()


# =========================================================
# Render Keep Alive
# =========================================================
keep_alive()

# =========================================================
# 起動
# =========================================================
bot.run(
    TOKEN,
    reconnect=True
)
