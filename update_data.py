import requests
import json
import os

# GitHub Actions sanal makinesinde dosya yolları klasörün kendisidir.
ANA_DOSYA = "depremler.json"
GUNCEL_DOSYA = "son_depremler.json"

def verileri_guncelle():
    print("🤖 Actions Robotu Devrede...")
    
    # 1. MEVCUT DOSYAYI OKU
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Arşivde şu an {len(mevcut_veri)} kayıt var.")
        except Exception as e:
            print(f"🚨 Dosya okuma hatası: {e}")
            # Dosya bozuksa boş liste ile devam et
            mevcut_veri = []
    
    # 2. API'DEN VERİ ÇEK (Canlı - Limit 500)
    # Actions sık çalıştığı için limit 500 gayet yeterlidir.
    url = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live?limit=500"
    
    yeni_gelenler = []
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                for item in data["result"]:
                    # --- KRİTİK DÜZELTME: İsim Kontrolü ---
                    # API bazen 'date', bazen 'date_time' veriyor.
                    if "date_time" in item:
                        item["date"] = item["date_time"]
                    
                    # 3.0 ve Üzeri Filtresi
                    try:
                        mag = float(item.get("mag", 0))
                        if mag >= 3.0:
                            yeni_gelenler.append(item)
                    except:
                        continue
            else:
                print("⚠️ API yanıtında veri yok.")
        else:
            print(f"❌ API Hatası: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return

    # 3. BİRLEŞTİR (ESKİ + YENİ)
    # ID Seti oluştur (Hızlı kontrol için)
    mevcut_id_seti = set()
    for d in mevcut_veri:
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    eklenen = 0
    # Yenileri tersten (eskiden yeniye) ekle ki sıralama bozulmasın
    for deprem in reversed(yeni_gelenler):
        uid = f"{deprem.get('date')}_{deprem.get('title')}"
        
        if uid not in mevcut_id_seti:
            mevcut_veri.insert(0, deprem) # En başa ekle
            mevcut_id_seti.add(uid)
            eklenen += 1

    # 4. KAYDET (Sadece değişiklik varsa)
    if eklenen > 0:
        print(f"✅ {eklenen} YENİ DEPREM TESPİT EDİLDİ.")
        
        try:
            # Büyük dosya (Hepsi)
            with open(ANA_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
            
            # Küçük dosya (Son 500 - Uygulama için)
            with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
                json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
                
            print("💾 Dosyalar güncellendi. (Git push işlemini YAML dosyası yapacak)")
        except Exception as e:
            print(f"❌ Yazma hatası: {e}")
            # Python hatayla çıksın ki Actions fail versin, haberdar olalım
            exit(1)
    else:
        print("💤 Yeni veri yok. Dosyalar değiştirilmedi.")

if __name__ == "__main__":
    verileri_guncelle()
