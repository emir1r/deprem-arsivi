import requests
import json
import os
import time

# Dosya yolları (Senin bilgisayarına göre)
ANA_DOSYA = "C:/Users/emirhan/Code/earthquake/depremler.json"
GUNCEL_DOSYA = "C:/Users/emirhan/Code/earthquake/son_depremler.json"

def bosluk_doldur_loop():
    print("🚑 GELİŞMİŞ Boşluk Doldurma Operasyonu (Sayfalamalı) Başladı...")

    # 1. MEVCUT ARŞİVİ YÜKLE
    mevcut_veri = []
    if os.path.exists(ANA_DOSYA):
        try:
            with open(ANA_DOSYA, "r", encoding="utf-8") as f:
                mevcut_veri = json.load(f)
            print(f"📦 Mevcut arşivde {len(mevcut_veri)} kayıt var.")
        except Exception as e:
            print(f"🚨 Dosya okuma hatası: {e}")
            return
    else:
        print("🚨 Dosya bulunamadı!")
        return

    # ID Seti Oluştur (Hız için)
    mevcut_id_seti = set()
    for d in mevcut_veri:
        uid = f"{d.get('date')}_{d.get('title')}"
        mevcut_id_seti.add(uid)

    # 2. DÖNGÜ İLE VERİ ÇEK (Toplam 20 sayfa x 100 = 2000 veri)
    toplam_eklenen = 0
    
    # 0'dan 2000'e kadar 100'er 100'er atlayarak gideceğiz
    for skip_miktari in range(0, 2000, 100):
        print(f"\n🔄 İstek yapılıyor: Skip {skip_miktari} - {skip_miktari+100} arası...")
        
        # skip parametresini kullanıyoruz
        url = f"https://api.orhanaydogdu.com.tr/deprem/kandilli/archive?limit=100&skip={skip_miktari}"
        
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if response.status_code == 200 and "result" in data:
                ham_veriler = data["result"]
                gelen_adet = len(ham_veriler)
                print(f"   📡 Bu sayfadan {gelen_adet} veri geldi.")
                
                if gelen_adet == 0:
                    print("   🛑 Veri bitti, döngü sonlandırılıyor.")
                    break

                # Bu sayfadaki verileri işle
                sayfa_eklenen = 0
                for item in ham_veriler:
                    # Tarih düzeltmesi
                    if "date_time" in item:
                        item["date"] = item["date_time"]
                    
                    # Büyüklük Filtresi (3.0+)
                    try:
                        mag = float(item.get("mag", 0))
                        if mag >= 3.0:
                            # ID kontrolü
                            uid = f"{item.get('date')}_{item.get('title')}"
                            if uid not in mevcut_id_seti:
                                mevcut_veri.insert(0, item) # Başa ekle
                                mevcut_id_seti.add(uid)
                                sayfa_eklenen += 1
                                toplam_eklenen += 1
                    except:
                        continue
                
                print(f"   ✅ Bu sayfadan {sayfa_eklenen} yeni deprem eklendi.")
                
                # API'yi yormamak için azıcık bekle
                time.sleep(1)

            else:
                print("   ❌ Sayfa çekilemedi.")
                
        except Exception as e:
            print(f"   ❌ Bağlantı hatası: {e}")
            break

    # 3. SONUÇLARI KAYDET
    if toplam_eklenen > 0:
        print(f"\n🎉 OPERASYON TAMAM! Toplam {toplam_eklenen} eksik deprem bulundu ve eklendi.")
        
        with open(ANA_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri, f, ensure_ascii=False, indent=None)
        
        with open(GUNCEL_DOSYA, "w", encoding="utf-8") as f:
            json.dump(mevcut_veri[:500], f, ensure_ascii=False, indent=None)
            
        print("💾 Dosyalar başarıyla kaydedildi. GitHub'a Push etmeyi unutma!")
    else:
        print("\n💤 Hiç yeni veri bulunamadı. Arşiv zaten tam görünüyor.")

if __name__ == "__main__":
    bosluk_doldur_loop()
