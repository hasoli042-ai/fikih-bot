import os

# Bu değerler GitHub Secrets üzerinden ortam değişkeni (environment variable)
# olarak workflow tarafından buraya enjekte edilir. Kodun içine asla
# doğrudan token yazmayın.

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN ortam değişkeni bulunamadı. GitHub Secrets'i kontrol edin.")
if not CHAT_ID:
    raise RuntimeError("CHAT_ID ortam değişkeni bulunamadı. GitHub Secrets'i kontrol edin.")
