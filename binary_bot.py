import time
import requests
import yfinance as yf
from datetime import datetime, timedelta

# ==========================================
# 1. إعدادات التيليجرام والأصول
# ==========================================
TELEGRAM_BOT_TOKEN "8951753821:AAH_zaJnrEeCnTRpuKca-sCOvAtYwPtQudE"
BINARY_CHAT_ID "-100398434205"

# الأصول المتاحة في السوق الحي (Forex & Crypto)
ASSETS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTC-USD", "SOL-USD", "GC=F"]

# ==========================================
# 2. دالة إرسال الرسائل إلى التيليجرام
# ==========================================
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": BINARY_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"خطأ في إرسال الرسالة: {e}")

# ==========================================
# 3. حساب مؤشر الزخم RSI (14)
# ==========================================
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# ==========================================
# 4. تحليل الأصول وتوليد الإشارات
# ==========================================
def analyze_market():
    # توقيت ليبيا (GMT+2)
    now_gmt2 = datetime.utcnow() + timedelta(hours=2)
    entry_time = now_gmt2.strftime("%H:%M")
    
    for symbol in ASSETS:
        try:
            display_symbol = symbol.replace("=X", "").replace("-USD", "/USD").replace("GC=F", "XAU/USD")
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1d", interval="5m")
            
            if df.empty or len(df) < 15:
                continue

            last_close = df['Close'].iloc[-1]
            high_10 = df['High'].iloc[-10:-1].max()
            low_10 = df['Low'].iloc[-10:-1].min()
            current_rsi = calculate_rsi(df)

            signal = None
            reason = ""

            if last_close <= low_10 or current_rsi < 30:
                signal = "🟢 صعود (CALL)"
                reason = "ارتداد من مستوى دعم + تشبع بيعي (RSI)"
            elif last_close >= high_10 or current_rsi > 70:
                signal = "🔴 هبوط (PUT)"
                reason = "ارتداد من مستوى مقاومة + تشبع شرائي (RSI)"

            if signal:
                message = (
                    f"📊 **إشارة Quotex للخيارات الثنائية**\n\n"
                    f"💱 **الزوج:** `{display_symbol}`\n"
                    f"⏰ **وقت الدخول:** `{entry_time}` (بتوقيت ليبيا)\n"
                    f"🎯 **الاتجاه:** {signal}\n"
                    f"⏱ **مدة الصلاحية:** `5 دقائق` (M5)\n"
                    f"💡 **السبب الفني:** {reason}\n\n"
                    f"⚠️ *ملاحظة: ادخل مع بداية الشمعة القادمة مباشرة.*"
                )
                send_telegram_message(message)

        except Exception as e:
            print(f"خطأ أثناء تحليل {symbol}: {e}")

# ==========================================
# 5. تشغيل البوت بشكل مستمر كل 5 دقائق
# ==========================================
if __name__ == "__main__":
    print("بدء تشغيل بوت الخيارات الثنائية على المنصة...")
    send_telegram_message("🤖 **تم تفعيل بوت Quotex بنجاح على سيرفر التشغيل المستمر!**")
    
    while True:
        try:
            analyze_market()
        except Exception as e:
            print(f"خطأ عام في حلقة التحليل: {e}")
        
        # الانتظار لمدة 300 ثانية (5 دقائق) قبل الفحص القادم
        time.sleep(300)
