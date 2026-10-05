import streamlit as st
from supabase import create_client, Client
from datetime import datetime, date, timedelta
import pandas as pd

# -------------------------------------------------------------
# 1. BULUT VERİTABANI BAĞLANTISI (SUPABASE)
# -------------------------------------------------------------
SUPABASE_URL = "https://cdjpcxiexelglvyvysys.supabase.co"
SUPABASE_KEY = "sb_publishable_Tr3LwHky4LVsq0iV-jNtDA_lWxVxwLp"

@st.cache_resource
def veritabanina_baglan():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

db = veritabanina_baglan()

# -------------------------------------------------------------
# 2. VERİTABANI YARDIMCI FONKSİYONLARI
# -------------------------------------------------------------
def log_yaz(oda_kodu, kisi, islem):
    try:
        db.table("audit_log").insert({
            "oda_kodu": str(oda_kodu),
            "kisi": kisi,
            "islem": islem
        }).execute()
    except Exception as e:
        st.error(f"Log hatası: {e}")

def oda_bilgisi_al_veya_olustur(oda_kodu):
    res = db.table("odalar").select("*").eq("id", str(oda_kodu)).execute()
    if not res.data:
        db.table("odalar").insert({"id": str(oda_kodu), "pin": "6070"}).execute()
        return "6070"
    return res.data[0].get("pin", "6070")

def sakinleri_getir(oda_kodu):
    res = db.table("sakinler").select("*").eq("oda_kodu", str(oda_kodu)).execute()
    return res.data or []

def harcamalari_getir(oda_kodu):
    res = db.table("harcamalar").select("*").eq("oda_kodu", str(oda_kodu)).order("id", desc=True).execute()
    return res.data or []

def temizlikleri_getir(oda_kodu):
    res = db.table("temizlik_gorevleri").select("*").eq("oda_kodu", str(oda_kodu)).execute()
    return res.data or []

def anonim_notlari_getir(oda_kodu):
    res = db.table("anonim_notlar").select("*").eq("oda_kodu", str(oda_kodu)).order("id", desc=True).limit(30).execute()
    return res.data or []

def loglari_getir(oda_kodu):
    res = db.table("audit_log").select("*").eq("oda_kodu", str(oda_kodu)).order("id", desc=True).limit(50).execute()
    return res.data or []

# -------------------------------------------------------------
# 3. GÜVENLİK VE SOL MENÜ (ÇİFT KATMANLI PIN)
# -------------------------------------------------------------
st.set_page_config(page_title="KYK Dijital Oda Protokolü", page_icon="🏠", layout="wide")

with st.sidebar:
    st.header("🔑 Güvenli Oda Erişimi")
    oda_kodu = st.text_input("Oda Kodu", value="607")
    girilen_oda_pin = st.text_input("Oda PIN Kodu", value="6070", type="password", help="Varsayılan: 6070")
    
    gercek_oda_pin = oda_bilgisi_al_veya_olustur(oda_kodu)
    
    if girilen_oda_pin != gercek_oda_pin:
        st.error("🚫 Hatalı Oda PIN'i! Yan odaların veya yabancıların erişimi engellendi.")
        st.stop()
    
    st.success("🔓 Oda Güvenliği Doğrulandı")
    st.divider()

    # Sakin Seçimi ve Kişisel PIN Doğrulama
    sakinler = sakinleri_getir(oda_kodu)
    sakin_isimleri = [f"{s['emoji']} {s['ad']}" for s in sakinler]

    st.subheader("👤 Aktif Sakin")
    kisi_yetkili = False
    aktif_kisi = None

    if sakinler:
        secilen_etiket = st.selectbox("Profiliniz:", sakin_isimleri)
        aktif_kisi = [s for s in sakinler if f"{s['emoji']} {s['ad']}" == secilen_etiket][0]
        
        girilen_kisi_pin = st.text_input(
            f"{aktif_kisi['ad']} Kişisel PIN:",
            type="password",
            value="1234",
            help="İşlem yapmak için kendi 4 haneli PIN'inizi girin (Varsayılan: 1234)."
        )
        
        kayitli_kisi_pin = str(aktif_kisi.get("pin") or "1234")
        if girilen_kisi_pin == kayitli_kisi_pin:
            kisi_yetkili = True
            st.caption("✅ Profil doğrulandı. İşlem yapabilirsiniz.")
        else:
            st.warning("⚠️ Kişisel PIN hatalı! İşlem butonları kilitli.")
    else:
        st.warning("Bu odada kayıtlı sakin bulunmuyor.")

    st.divider()

    # Yeni Kişi Ekleme
    with st.expander("➕ Odaya Yeni Sakin Ekle"):
        with st.form("yeni_kisi_formu", clear_on_submit=True):
            yeni_ad = st.text_input("İsim")
            yeni_emoji = st.selectbox("Emoji", ["🌸", "🐱", "🥑", "⚡", "🌿", "✨", "🎨", "🦊", "☕", "🚀"])
            yeni_renk = st.color_picker("Temsili Renk", "#FF69B4")
            yeni_pin = st.text_input("4 Haneli Kişisel PIN Belirleyin", value="1234", max_chars=4)
            kisi_ekle_btn = st.form_submit_button("Odaya Ekle")

            if kisi_ekle_btn:
                if not yeni_ad.strip():
                    st.error("Lütfen bir isim yazın!")
                elif any(s["ad"].lower() == yeni_ad.strip().lower() for s in sakinler):
                    st.error("Bu isimde biri odada zaten var!")
                else:
                    db.table("sakinler").insert({
                        "oda_kodu": str(oda_kodu),
                        "ad": yeni_ad.strip(),
                        "emoji": yeni_emoji,
                        "renk": yeni_renk,
                        "pin": yeni_pin if len(yeni_pin) == 4 else "1234",
                        "oda_cop": 0,
                        "banyo_cop": 0
                    }).execute()
                    log_yaz(oda_kodu, yeni_ad.strip(), f"Odaya sakin olarak katıldı ({yeni_emoji}).")
                    st.success(f"{yeni_ad} odaya kaydedildi!")
                    st.rerun()

# -------------------------------------------------------------
# 4. ANA PANEL & TÜM SEKMELER
# -------------------------------------------------------------
st.title(f"🏠 Oda {oda_kodu} Dijital Yaşam Protokolü")

if not sakinler:
    st.info("👈 Başlamak için sol menüden odanın ilk sakinlerini ekleyin.")
    st.stop()

tab_pano, tab_temizlik, tab_cop, tab_borc, tab_liste, tab_log = st.tabs([
    "📌 Anonim Not Panosu",
    "🧹 Temizlik Takvimi",
    "🗑️ Çöp Skor Tahtası",
    "💰 Borç Bölüşümü",
    "🛒 İhtiyaç Listesi",
    "📜 Kara Kaplı Defter (Log)"
])

# -------------------------------------------------------------
# SEKME 1: ANONİM NOT PANOSU
# -------------------------------------------------------------
with tab_pano:
    st.subheader("📌 Anonim Oda Duvarı (Dijital Post-it)")
    st.caption("Yüz yüze söylemekte zorlandığınız durumları kimliğiniz görünmeden yapıcı bir şekilde odaya iletin.")

    with st.expander("✍️ Panoya Anonim Not Bırak", expanded=False):
        with st.form("anonim_not_formu", clear_on_submit=True):
            kategori = st.selectbox(
                "Kategori / Başlık",
                [
                    "🤫 Gürültü / Uyku Düzeni",
                    "💡 Işık & Erken Uyanma",
                    "🪟 Havalandırma & Oda Sıcaklığı",
                    "🧹 Ortak Alan Temizliği",
                    "🚿 Lavabo & Banyo Düzeni",
                    "💬 Genel Hatırlatma"
                ]
            )
            mesaj = st.text_area("Mesajınız", placeholder="Örn: Kızlar sabah erken dersi olanlar dolap kapaklarını biraz daha sessiz kapatabilirse harika olur 🌿")
            not_gonder = st.form_submit_button("Anonim Olarak Paylaş")

            if not_gonder:
                if not mesaj.strip():
                    st.error("Boş not paylaşılamaz!")
                else:
                    db.table("anonim_notlar").insert({
                        "oda_kodu": str(oda_kodu),
                        "kategori": kategori,
                        "mesaj": mesaj.strip()
                    }).execute()
                    log_yaz(oda_kodu, "Anonim Sakin", f"Panoya yeni bir not bıraktı ({kategori}).")
                    st.success("Notunuz panoya anonim olarak eklendi!")
                    st.rerun()

    notlar = anonim_notlari_getir(oda_kodu)
    if notlar:
        cols = st.columns(2)
        for idx, n in enumerate(notlar):
            zaman_kisa = n["zaman"][:16].replace("T", " ")
            with cols[idx % 2]:
                st.markdown(
                    f"<div style='background-color: #2b303a22; border: 1px solid #444; border-left: 5px solid #FFB703; padding: 12px; border-radius: 8px; margin-bottom: 12px;'>"
                    f"<div style='display:flex; justify-content:space-between;'>"
                    f"<b>{n['kategori']}</b>"
                    f"<small style='color:#888;'>{zaman_kisa}</small>"
                    f"</div>"
                    f"<p style='margin-top: 8px; margin-bottom: 0;'>{n['mesaj']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
    else:
        st.info("Oda panosunda henüz bir not yok. İlk notu siz bırakabilirsiniz!")

# -------------------------------------------------------------
# SEKME 2: ESNEK TEMİZLİK TAKVİMİ
# -------------------------------------------------------------
with tab_temizlik:
    st.subheader("🧹 Haftalık Temizlik Takvimi")
    
    # Oda İçi Dinamik Kural Ayarı
    c_ay1, c_ay2 = st.columns(2)
    with c_ay1:
        dongu = st.selectbox("Haftalık Temizlik Yoğunluğu:", ["Haftada 1 Büyük Temizlik", "Haftada 2 Temizlik (Detaylı)"])
    with c_ay2:
        nobetci_sayisi = st.selectbox("Nöbetçi Kişi Sayısı:", ["Haftada 2 Kişi Görevli", "Haftada 1 Kişi Görevli"])

    sakin_adlari = [s["ad"] for s in sakinler]
    c_n1, c_n2 = st.columns(2)
    with c_n1:
        gorevli_1 = st.selectbox("1. Görevli:", sakin_adlari, index=0 if len(sakin_adlari) > 0 else 0)
    with c_n2:
        gorevli_2 = st.selectbox("2. Görevli:", sakin_adlari, index=1 if len(sakin_adlari) > 1 else 0)

    st.info(f"🎯 **Bu Haftanın Nöbetçileri:** {gorevli_1} {'& ' + gorevli_2 if '2 Kişi' in nobetci_sayisi else ''} | Müsait olduğunuz gün temizliği tamamlayıp gününüzü renklendirin.")

    bugun = date.today()
    pazartesi = bugun - timedelta(days=bugun.weekday())
    haftanin_gunleri = [pazartesi + timedelta(days=i) for i in range(7)]
    gun_isimleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

    mevcut_temizlikler = temizlikleri_getir(oda_kodu)
    temizlik_haritasi = {t["tarih"]: t for t in mevcut_temizlikler}

    gun_kolonlari = st.columns(7)
    for i in range(7):
        g_tarih = haftanin_gunleri[i].strftime("%Y-%m-%d")
        g_isim = gun_isimleri[i]
        kayit = temizlik_haritasi.get(g_tarih)

        with gun_kolonlari[i]:
            if kayit and kayit.get("tamamlandi"):
                yapan = next((s for s in sakinler if s["ad"] == kayit["kisi"]), None)
                renk = yapan["renk"] if yapan else "#4CAF50"
                emoji = yapan["emoji"] if yapan else "✨"

                st.markdown(
                    f"<div style='background-color:{renk}33; border: 2px solid {renk}; border-radius: 8px; padding: 10px; text-align: center; min-height: 140px;'>"
                    f"<b>{g_isim}</b><br><small>{g_tarih[5:]}</small><br><br>"
                    f"<span style='font-size: 20px;'>{emoji}</span><br>"
                    f"<b style='color:{renk};'>{kayit['kisi']}</b><br><small>Temizledi ✅</small>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div style='border: 1px dashed #888; border-radius: 8px; padding: 10px; text-align: center; min-height: 140px;'>"
                    f"<b>{g_isim}</b><br><small>{g_tarih[5:]}</small><br><br>"
                    f"<span style='color: #888;'>Boş</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                if st.button("Temizledim", key=f"temiz_{g_tarih}", use_container_width=True, disabled=not kisi_yetkili):
                    db.table("temizlik_gorevleri").insert({
                        "oda_kodu": str(oda_kodu),
                        "kisi": aktif_kisi["ad"],
                        "tarih": g_tarih,
                        "tamamlandi": True
                    }).execute()
                    log_yaz(oda_kodu, aktif_kisi["ad"], f"{g_isim} günü temizliğini tamamladı.")
                    st.success(f"{g_isim} kaydedildi!")
                    st.rerun()

# -------------------------------------------------------------
# SEKME 3: ÇÖP SKOR TAHTASI
# -------------------------------------------------------------
with tab_cop:
    st.subheader("Adalet Sayacı: Çöp İstatistikleri")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Oda Çöpünü Boşalttım (+1)", use_container_width=True, disabled=not kisi_yetkili):
            yeni = aktif_kisi["oda_cop"] + 1
            db.table("sakinler").update({"oda_cop": yeni}).eq("id", aktif_kisi["id"]).execute()
            log_yaz(oda_kodu, aktif_kisi["ad"], "Oda çöpünü döktü (+1).")
            st.success("Oda çöpü hanenize eklendi!")
            st.rerun()

    with c2:
        if st.button("🚿 Banyo Çöpünü Boşalttım (+1)", use_container_width=True, disabled=not kisi_yetkili):
            yeni = aktif_kisi["banyo_cop"] + 1
            db.table("sakinler").update({"banyo_cop": yeni}).eq("id", aktif_kisi["id"]).execute()
            log_yaz(oda_kodu, aktif_kisi["ad"], "Banyo çöpünü döktü (+1).")
            st.success("Banyo çöpü hanenize eklendi!")
            st.rerun()

    st.divider()

    kolonlar = st.columns(len(sakinler))
    for i, s in enumerate(sakinler):
        with kolonlar[i]:
            st.markdown(
                f"<div style='background-color:{s['renk']}22; border-left: 5px solid {s['renk']}; padding: 12px; border-radius: 8px;'>"
                f"<h4>{s['emoji']} {s['ad']}</h4>"
                f"<p style='margin:0;'>🗑️ <b>Oda:</b> {s['oda_cop']}</p>"
                f"<p style='margin:0;'>🚿 <b>Banyo:</b> {s['banyo_cop']}</p>"
                f"<p style='margin:0; font-size: 1.1em;'>⭐ <b>Toplam:</b> {s['oda_cop'] + s['banyo_cop']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

# -------------------------------------------------------------
# SEKME 4: BORÇ & HARCAMA BÖLÜŞÜMÜ
# -------------------------------------------------------------
with tab_borc:
    st.subheader("Ortak Masraflar & Borç Netleştirme")
    
    with st.expander("💳 Yeni Ortak Harcama Gir"):
        with st.form("harcama_formu", clear_on_submit=True):
            urun = st.text_input("Ürün Başlığı", placeholder="Örn: Sıvı Sabun, Bulaşık Deterjanı")
            tutar = st.number_input("Tutar (TL)", min_value=1.0, step=1.0)
            dahil_olanlar = st.multiselect(
                "Masrafa Katılanlar:",
                options=[s["ad"] for s in sakinler],
                default=[s["ad"] for s in sakinler]
            )
            harcama_btn = st.form_submit_button("Harcamayı Kaydet", disabled=not kisi_yetkili)
            
            if harcama_btn:
                if not urun.strip() or not dahil_olanlar:
                    st.error("Eksik bilgi girdiniz!")
                else:
                    db.table("harcamalar").insert({
                        "oda_kodu": str(oda_kodu),
                        "alan_kisi": aktif_kisi["ad"],
                        "urun": urun.strip(),
                        "tutar": float(tutar),
                        "dahil_olanlar": dahil_olanlar
                    }).execute()
                    pay = round(tutar / len(dahil_olanlar), 2)
                    log_yaz(oda_kodu, aktif_kisi["ad"], f"'{urun}' için {tutar} TL harcadı. Kişi başı: {pay} TL.")
                    st.success("Harcama kaydedildi!")
                    st.rerun()

    harcamalar = harcamalari_getir(oda_kodu)
    if harcamalar:
        isimler = [s["ad"] for s in sakinler]
        borc_matrisi = {a: {b: 0.0 for b in isimler} for a in isimler}

        for h in harcamalar:
            odeyen = h["alan_kisi"]
            tutar = float(h["tutar"])
            dahil = h["dahil_olanlar"]
            if not dahil or odeyen not in isimler:
                continue
            pay = tutar / len(dahil)
            for kisi in dahil:
                if kisi in isimler and kisi != odeyen:
                    borc_matrisi[kisi][odeyen] += pay

        st.markdown("#### ⚖️ Netleşmiş Borç Listesi")
        net_transferler = []
        for i in range(len(isimler)):
            for j in range(i + 1, len(isimler)):
                p1, p2 = isimler[i], isimler[j]
                fark = borc_matrisi[p1][p2] - borc_matrisi[p2][p1]
                if fark > 0.5:
                    net_transferler.append((p1, p2, round(fark, 2)))
                elif fark < -0.5:
                    net_transferler.append((p2, p1, round(-fark, 2)))

        if net_transferler:
            for borclu, alacakli, miktar in net_transferler:
                c_sol, c_sag = st.columns([4, 1])
                with c_sol:
                    st.warning(f"👉 **{borclu}**, **{alacakli}** kişisine **{miktar} TL** ödemeli.")
                with c_sag:
                    if st.button("Ödendi", key=f"ode_{borclu}_{alacakli}", disabled=not kisi_yetkili):
                        db.table("harcamalar").insert({
                            "oda_kodu": str(oda_kodu),
                            "alan_kisi": borclu,
                            "urun": f"Borç Kapatma -> {alacakli}",
                            "tutar": float(miktar),
                            "dahil_olanlar": [alacakli]
                        }).execute()
                        log_yaz(oda_kodu, borclu, f"{alacakli} kişisine {miktar} TL borcunu ödedi.")
                        st.success("Borç düşüldü!")
                        st.rerun()
        else:
            st.success("🎉 Odada kimsenin kimseye netleşmiş borcu yok.")

# -------------------------------------------------------------
# SEKME 5: İHTİYAÇ LİSTESİ
# -------------------------------------------------------------
with tab_liste:
    st.subheader("Oda Ortak İhtiyaç Listesi")
    c_iht1, c_iht2 = st.columns([4, 1])
    with c_iht1:
        yeni_iht = st.text_input("Alınacak İhtiyaç", placeholder="Örn: 30'lu Çöp Torbası", label_visibility="collapsed")
    with c_iht2:
        if st.button("Listeye Ekle", use_container_width=True, disabled=not kisi_yetkili):
            if yeni_iht.strip():
                log_yaz(oda_kodu, aktif_kisi["ad"], f"İhtiyaç listesine '{yeni_iht.strip()}' ekledi.")
                st.success("Eklendi!")
                st.rerun()

# -------------------------------------------------------------
# SEKME 6: ŞEFFAF DENETİM GÜNLÜĞÜ (AUDIT LOG)
# -------------------------------------------------------------
with tab_log:
    st.subheader("📜 Şeffaf Oda Günlüğü (Kara Kaplı Defter)")
    st.caption("Bu odada yapılan her eylem saat saat silinemez biçimde buraya kaydedilir.")
    loglar = loglari_getir(oda_kodu)
    if loglar:
        for l in loglar:
            zaman_str = l["zaman"][:16].replace("T", " ")
            st.markdown(f"`{zaman_str}` | **{l['kisi']}**: {l['islem']}")
    else:
        st.info("Henüz bir kayıt bulunmuyor.")