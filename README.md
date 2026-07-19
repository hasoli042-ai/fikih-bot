# İslami Bilgi Botu (Telegram)

Her gün 09:00-21:00 arası (İstanbul saati), saat başı sırayla hadis / fıkıh bilgisi gönderen,
tamamen ücretsiz GitHub Actions üzerinde çalışan bir Telegram botu.

## 1) Telegram tarafında yapılacaklar

1. Telegram'da **@BotFather** ile konuşun, `/newbot` yazın, bir isim ve kullanıcı adı verin.
   Size bir **BOT_TOKEN** verecek (örn: `123456789:AAExxxxx...`). Bunu saklayın.
2. Botu mesaj göndereceğiniz sohbete (kendinize, bir gruba veya kanala) ekleyin.
3. **CHAT_ID**'nizi öğrenin:
   - Kendinize göndermek istiyorsanız: bota Telegram'dan `/start` yazın, sonra tarayıcıda
     `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` adresine gidin, dönen JSON içindeki
     `"chat":{"id": ... }` alanındaki sayıyı alın.
   - Bir gruba göndermek istiyorsanız: botu gruba ekleyin, grupta bir mesaj yazın, aynı
     `getUpdates` adresinden grup id'sini alın (grup id'leri genelde eksi (-) işaretlidir).
   - Bir kanala göndermek istiyorsanız: botu kanala **yönetici** olarak ekleyin, kanal id'si
     genelde `-100` ile başlar.

## 2) GitHub tarafında yapılacaklar

1. GitHub'da yeni bir **repository** oluşturun (public veya private, ikisi de olur;
   public repolarda GitHub Actions dakika kotası pratikte hiç bitmez).
2. Bu klasördeki tüm dosyaları ve klasör yapısını **birebir aynı hiyerarşiyle** repoya yükleyin:

   ```
   fikih-telegram-bot/
   ├── bot.py
   ├── requirements.txt
   ├── config.py
   ├── state.json
   ├── README.md
   ├── data/
   │   ├── fikih.json
   │   └── hadis.json
   └── .github/
       └── workflows/
           └── bot.yml
   ```

   > Önemli: `.github/workflows/bot.yml` dosyasının repo kök dizininde `.github/workflows/`
   > klasörü içinde olması **zorunludur**, GitHub Actions bu yolu arar. Eğer bu içeriği bir
   > zip olarak indirdiyseniz, klasör yapısını bozmadan GitHub'ın web arayüzünden
   > "Add file → Upload files" ile veya `git` komutlarıyla yükleyin.

3. Repo ayarlarına gidin: **Settings → Secrets and variables → Actions → New repository secret**
   - `BOT_TOKEN` adında bir secret oluşturup BotFather'dan aldığınız token'ı yapıştırın.
   - `CHAT_ID` adında bir secret oluşturup az önce bulduğunuz chat id'yi yapıştırın.
4. **Settings → Actions → General → Workflow permissions** kısmına gidin, "Read and write
   permissions" seçeneğini işaretleyip kaydedin. (Bot her gönderimden sonra `state.json`
   dosyasını güncelleyip repoya otomatik commit atacağı için bu izin gereklidir.)

## 3) Test etme

1. Repo'nuzda **Actions** sekmesine gidin, "Islami Bilgi Botu" workflow'unu seçin.
2. Sağ üstte **"Run workflow"** butonuna basın. İsterseniz "force_hour" alanına 9 veya 10 gibi
   bir saat yazıp belirli bir içerik türünü test edebilirsiniz (boş bırakırsanız gerçek saat
   kullanılır ve saat 09-21 dışındaysa hiçbir şey göndermez).
3. Telegram'a mesaj gelip gelmediğini kontrol edin. Hata olursa Actions sekmesindeki log
   çıktısına bakın (BOT_TOKEN/CHAT_ID yanlışsa burada görürsünüz).

## 4) Otomatik çalışma

Hiçbir şey yapmanıza gerek yok — `.github/workflows/bot.yml` içindeki

```yaml
schedule:
  - cron: "0 9-21 * * *"
    timezone: "Europe/Istanbul"
```

satırı sayesinde bot her gün saat 09:00-21:00 arası, saat başı otomatik çalışır.
Bilgisayarınızın açık olmasına gerek yoktur; iş tamamen GitHub'ın sunucularında yürür.

**Bilinmesi gereken önemli bir teknik gerçek:** GitHub Actions'ın zamanlı (cron) tetikleyicisi
"best-effort"tür; GitHub'ın kendi yoğunluğuna göre mesajlar bazen 5-30 dakika (nadiren daha
fazla) gecikmeli gelebilir. Bu, GitHub'ın ücretsiz sunduğu bir hizmetin doğal sınırıdır, botun
kodundan kaynaklanmaz. Dakika hassasiyeti kritikse (bu proje için gerekli değil) alternatif
olarak ücretsiz bir dış servis (örn. cron-job.org) ile workflow'u API üzerinden tetiklemek
mümkündür.

`state.json` dosyası her gönderimden sonra bot tarafından otomatik güncellenip repoya commit
edilir; bu commit aynı zamanda GitHub'ın "60 gün hareketsiz kalan repoda zamanlı görevleri
otomatik durdurma" kuralına karşı da koruma sağlar, çünkü repo saatte bir zaten güncellenmiş
olacaktır.

## 5) İçerikleri genişletme (500 kayda çıkarma)

`data/hadis.json` ve `data/fikih.json` şu an **başlangıç seti** olarak sınırlı sayıda (12-20
civarı), doğruluğuna güvendiğim, yaygın bilinen kayıtlarla geldi — 500'e tamamlanmadı.
Bunun sebebi teknik değil, içerik güvenilirliği: yüzlerce hadisi ravi, bab başlığı ve tam
metniyle, ya da yüzlerce Hanefî fıkıh meselesini kaynak sayfa numarasıyla hatasız şekilde
üretmek, gerçek bir kaynaktan tek tek doğrulama gerektiren bir iştir. Yanlış bir hadis
atfı veya hatalı bir fıkıh detayı, "az ama doğru" bir listeden çok daha zararlıdır.

Genişletme için önerilen yol:
- Hadisler için: diyanet'in `hadislerle-islam` projesini, `sunnah.com` üzerindeki
  Riyad as-Salihin bölümünü veya Riyâzü's-Sâlihîn'in matbu bir tercümesini kaynak alıp,
  aynı JSON formatında (`title, hadith, narrator, source, comment`) elle veya yarı-otomatik
  olarak ekleyin.
- Fıkıh için: Ömer Nasuhi Bilmen'in *Büyük İslam İlmihali* ve Diyanet İslam Ansiklopedisi
  maddelerini konu konu tarayıp aynı formatta (`title, text, source`) ekleyin.
- Her iki dosya da düz JSON listesi olduğu için, yeni kayıtları listenin sonuna eklemeniz
  yeterlidir; `bot.py` kayıt sayısını otomatik algılar, kod tarafında değişiklik gerekmez.

## 6) Dosya rolleri özeti

| Dosya | Görevi |
|---|---|
| `bot.py` | Saat kaç, hangi içerik türü gönderilecek, hangi kayıt sırada — hepsine karar verip Telegram'a gönderir |
| `config.py` | Secrets'tan gelen `BOT_TOKEN`/`CHAT_ID`'yi okur |
| `state.json` | "Kaldığım yer" hafızası; her gönderimden sonra otomatik güncellenir |
| `data/hadis.json` | Hadis kayıtları |
| `data/fikih.json` | Fıkıh kayıtları |
| `.github/workflows/bot.yml` | GitHub'a "her saat başı bunu çalıştır" talimatı |
