/**
 * AVM Akıllı Ürün Bulma Sistemi — Ana JavaScript Dosyası
 * NFR-3.2: Kritik işlemler için onay pop-up
 * NFR-3.3: Kullanıcı dostu Türkçe hata mesajları
 */

'use strict';

/* ─────────────────────────────────────────────
   ONAY POP-UP (NFR-3.2)
   Kullanım:
     onayPopup('Ürünü silmek istediğinizden emin misiniz?', function() {
         // onaylandığında çalışacak kod
     });
   veya data attribute ile:
     <button data-onay="true" data-onay-mesaj="Silmek istediğinizden emin misiniz?"
             data-onay-hedef="/manager/products/5/delete" data-onay-method="POST">
         Sil
     </button>
   ───────────────────────────────────────────── */

/**
 * Onay modalını gösterir.
 * @param {string} mesaj      - Modal gövdesinde gösterilecek mesaj
 * @param {Function} onayFn   - Kullanıcı "Evet, Devam Et" tıkladığında çağrılır
 * @param {string} [baslik]   - Opsiyonel modal başlığı
 */
function onayPopup(mesaj, onayFn, baslik) {
    var modal = document.getElementById('onayModal');
    if (!modal) {
        // Modal HTML yoksa direkt onayla (güvenli fallback)
        if (confirm(mesaj)) {
            onayFn();
        }
        return;
    }

    // İçerikleri ayarla
    var baslikEl = document.getElementById('onayModalLabel');
    var bodyEl   = document.getElementById('onayModalBody');
    var onaylaEl = document.getElementById('onayModalOnayla');

    if (baslikEl) {
        baslikEl.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>' +
            (baslik || 'İşlemi Onayla');
    }
    if (bodyEl) {
        bodyEl.textContent = mesaj;
    }

    // Önceki event listener'ı temizle (clone trick)
    var yeniOnaylaEl = onaylaEl.cloneNode(true);
    onaylaEl.parentNode.replaceChild(yeniOnaylaEl, onaylaEl);

    yeniOnaylaEl.addEventListener('click', function() {
        var bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) bsModal.hide();
        onayFn();
    });

    // Modalı aç
    var bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/* ─────────────────────────────────────────────
   DATA ATTRIBUTE İLE OTOMATIK ONAY POP-UP
   <button data-onay="true"
           data-onay-mesaj="..."
           data-onay-hedef="/url"
           data-onay-method="POST"
           [data-onay-form="form-id"]>
   ───────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function() {

    // data-onay="true" olan tüm buton/linklere dinleyici ekle
    document.querySelectorAll('[data-onay="true"]').forEach(function(el) {
        el.addEventListener('click', function(e) {
            e.preventDefault();

            var mesaj   = el.dataset.onayMesaj   || 'Bu işlemi gerçekleştirmek istediğinizden emin misiniz?';
            var hedef   = el.dataset.onayHedef;
            var method  = (el.dataset.onayMethod || 'POST').toUpperCase();
            var formId  = el.dataset.onayForm;
            var baslik  = el.dataset.onayBaslik;

            onayPopup(mesaj, function() {
                if (formId) {
                    // Belirtilen form ID'sini gönder
                    var form = document.getElementById(formId);
                    if (form) form.submit();
                } else if (hedef) {
                    // Gizli form oluştur ve gönder
                    var gizliForm = document.createElement('form');
                    gizliForm.method = method === 'GET' ? 'GET' : 'POST';
                    gizliForm.action = hedef;

                    // CSRF token varsa ekle
                    var csrfMeta = document.querySelector('meta[name="csrf-token"]');
                    if (csrfMeta) {
                        var csrfInput = document.createElement('input');
                        csrfInput.type  = 'hidden';
                        csrfInput.name  = 'csrf_token';
                        csrfInput.value = csrfMeta.content;
                        gizliForm.appendChild(csrfInput);
                    }

                    // Method override (PUT, DELETE, PATCH için)
                    if (['PUT','DELETE','PATCH'].includes(method)) {
                        var methodInput = document.createElement('input');
                        methodInput.type  = 'hidden';
                        methodInput.name  = '_method';
                        methodInput.value = method;
                        gizliForm.appendChild(methodInput);
                    }

                    document.body.appendChild(gizliForm);
                    gizliForm.submit();
                } else if (el.tagName === 'A' && el.href) {
                    window.location.href = el.href;
                }
            }, baslik);
        });
    });

    /* ── Flash mesajları 5 saniye sonra kapat ── */
    setTimeout(function() {
        document.querySelectorAll('.flash-container .alert').forEach(function(alert) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        });
    }, 5000);

    /* ── Aktif sidebar linkini işaretle ── */
    markaAktifSidebarLink();

    /* ── Form doğrulama feedback'i (Bootstrap validation) ── */
    document.querySelectorAll('.needs-validation').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

});

/* ─────────────────────────────────────────────
   SIDEBAR AKTİF LİNK
   ───────────────────────────────────────────── */
function markaAktifSidebarLink() {
    var mevcutYol = window.location.pathname;
    document.querySelectorAll('.sidebar .nav-link').forEach(function(link) {
        if (link.getAttribute('href') === mevcutYol) {
            link.classList.add('active');
        }
    });
}

/* ─────────────────────────────────────────────
   STOK GÜNCELLEME — Hızlı Form (Manager)
   ───────────────────────────────────────────── */

/**
 * Hızlı stok güncelleme popup'ını gösterir.
 * Eğer sayfada #hizliStokModal varsa (manager/products.html) modal kullanır,
 * yoksa onayPopup ile prompt tabanlı güncelleme yapar (NFR-3.2 uyumlu).
 * @param {number} urunId    - Ürün ID
 * @param {string} urunAdi   - Ürün adı (gösterim için)
 * @param {number} mevcutStok - Mevcut stok adedi
 */
function hizliStokGuncelle(urunId, urunAdi, mevcutStok) {
    // Eğer sayfada modal varsa (manager/products.html), onu kullan
    var modalEl = document.getElementById('hizliStokModal');
    if (modalEl) {
        document.getElementById('hizli-stok-urun-adi').textContent = urunAdi;
        document.getElementById('hizli-stok-mevcut').value = mevcutStok;
        document.getElementById('hizli-stok-yeni').value = mevcutStok;
        document.getElementById('hizli-stok-form').action = '/manager/products/' + urunId + '/stock';
        var bsModal = new bootstrap.Modal(modalEl);
        bsModal.show();
        return;
    }

    // Fallback: prompt + onayPopup (NFR-3.2 uyumlu)
    var yeniStok = prompt(
        '"' + urunAdi + '" ürünü için yeni stok adedini girin:\n(Mevcut: ' + mevcutStok + ')',
        mevcutStok
    );

    if (yeniStok === null) return;

    yeniStok = parseInt(yeniStok, 10);

    if (isNaN(yeniStok) || yeniStok < 0) {
        bildirimiGoster('Lütfen geçerli bir stok adedi girin (0 veya daha büyük bir sayı).', 'danger');
        return;
    }

    // NFR-3.2: Onay pop-up göster
    onayPopup(
        '"' + urunAdi + '" ürününün stoğunu ' + mevcutStok + ' adetten ' + yeniStok + ' adede güncellemek istediğinizden emin misiniz?',
        function() {
            var form = document.createElement('form');
            form.method = 'POST';
            form.action = '/manager/products/' + urunId + '/stock';

            var alanlar = {
                'stok_adedi':      yeniStok,
                'guncelleme_turu': 'Manuel'
            };

            var csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta) {
                alanlar['csrf_token'] = csrfMeta.content;
            }

            Object.keys(alanlar).forEach(function(isim) {
                var input = document.createElement('input');
                input.type  = 'hidden';
                input.name  = isim;
                input.value = alanlar[isim];
                form.appendChild(input);
            });

            document.body.appendChild(form);
            form.submit();
        },
        'Stok Güncelleme Onayı'
    );
}

/* ─────────────────────────────────────────────
   BİLDİRİM GÖSTERİCİ — Programatik Toast/Alert
   ───────────────────────────────────────────── */

/**
 * Sayfanın üstünde geçici bildirim gösterir.
 * @param {string} mesaj    - Bildirim metni
 * @param {string} tur      - Bootstrap renk tipi: 'success','danger','warning','info'
 * @param {number} [sure]   - Otomatik kapanma süresi ms (default 4000)
 */
function bildirimiGoster(mesaj, tur, sure) {
    tur  = tur  || 'info';
    sure = sure || 4000;

    var ikonlar = {
        success: 'bi-check-circle-fill',
        danger:  'bi-exclamation-triangle-fill',
        warning: 'bi-exclamation-circle-fill',
        info:    'bi-info-circle-fill'
    };

    var ikon = ikonlar[tur] || 'bi-info-circle-fill';

    var alert = document.createElement('div');
    alert.className = 'alert alert-' + tur + ' alert-dismissible fade show mb-0 rounded-0 fade-in';
    alert.setAttribute('role', 'alert');
    alert.innerHTML =
        '<div class="container-fluid">' +
            '<i class="bi ' + ikon + ' me-2"></i>' + mesaj +
        '</div>' +
        '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Kapat"></button>';

    var container = document.querySelector('.flash-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-container';
        var navbar = document.getElementById('main-navbar');
        if (navbar && navbar.nextSibling) {
            navbar.parentNode.insertBefore(container, navbar.nextSibling);
        } else {
            document.body.insertAdjacentElement('afterbegin', container);
        }
    }

    container.appendChild(alert);

    setTimeout(function() {
        var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
    }, sure);
}

/* ─────────────────────────────────────────────
   FİLTRE PANELİ MOBİL TOGGLE
   ───────────────────────────────────────────── */
function filtrePaneliToggle() {
    var panel = document.getElementById('filtre-panel');
    if (!panel) return;
    panel.classList.toggle('d-none');
}

/* ─────────────────────────────────────────────
   BİLDİRİM MODAL (Müşteri — BR-1.2)
   ───────────────────────────────────────────── */

/**
 * Stok bildirim talebini görmek için modal açar.
 * Kayıtsız kullanıcılar giriş sayfasına yönlendirilir (BR-1.2).
 * @param {number}  urunId       - Ürün ID
 * @param {string}  urunAdi      - Ürün adı
 * @param {boolean} girisYapildi - Kullanıcı oturumu açık mı?
 */
function bildirimTalebiAc(urunId, urunAdi, girisYapildi) {
    if (!girisYapildi) {
        // BR-1.2: Kayıtsız ziyaretçi bildirim oluşturamaz
        onayPopup(
            '"Stok Gelince Haber Ver" özelliğini kullanmak için giriş yapmanız gerekmektedir. ' +
            'Giriş sayfasına yönlendirilmek ister misiniz?',
            function() {
                window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
            },
            'Giriş Yapmanız Gerekiyor'
        );
        return;
    }

    // Bildirim modalını doldur ve aç
    var urunAdiEl = document.getElementById('bildirim-urun-adi');
    var urunIdEl  = document.getElementById('bildirim-urun-id');

    if (urunAdiEl) urunAdiEl.textContent = urunAdi;
    if (urunIdEl)  urunIdEl.value        = urunId;

    var modal = document.getElementById('bildirimModal');
    if (modal) {
        var bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
}

/* ─────────────────────────────────────────────
   YOL TARİFİ (Müşteri — Ürün Detay)
   ───────────────────────────────────────────── */

/**
 * AVM içi yol tarifleri için konum bilgisini gösterir.
 * @param {string} konumKodu - Mağaza konum kodu
 * @param {string} kat       - Mağaza katı
 * @param {string} magazaAdi - Mağaza adı
 */
function yolTarifiGoster(konumKodu, kat, magazaAdi) {
    var mesaj = magazaAdi + ' mağazası ' + kat + '. katta bulunmaktadır.\n' +
                'Konum Kodu: ' + konumKodu + '\n\n' +
                'AVM haritasındaki yönlendirme tabelalarını takip ediniz.';

    var modal = document.getElementById('yolTarifiModal');
    if (modal) {
        var icerik = modal.querySelector('#yolTarifi-icerik');
        if (icerik) {
            icerik.innerHTML =
                '<div class="text-center mb-3">' +
                    '<i class="bi bi-geo-alt-fill text-primary" style="font-size:3rem;"></i>' +
                '</div>' +
                '<div class="d-flex justify-content-center gap-3 flex-wrap">' +
                    '<div class="badge-kat px-3 py-2 rounded">' +
                        '<i class="bi bi-layers me-1"></i>' + kat + '. Kat' +
                    '</div>' +
                    '<div class="badge-konum px-3 py-2 rounded">' +
                        '<i class="bi bi-pin-map me-1"></i>' + konumKodu +
                    '</div>' +
                '</div>' +
                '<p class="mt-3 text-center text-muted">' + magazaAdi + '</p>' +
                '<p class="text-center small text-muted">AVM içindeki yönlendirme tabelalarını takip ediniz.</p>';
        }
        var modalBaslik = modal.querySelector('#yolTarifiModalLabel');
        if (modalBaslik) {
            modalBaslik.innerHTML = '<i class="bi bi-compass me-2"></i>Yol Tarifi';
        }
        var bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    } else {
        alert(mesaj);
    }
}

/* ─────────────────────────────────────────────
   SAYFA YÜKLENİYOR SPINNER
   ───────────────────────────────────────────── */
function yukleniyor(goster) {
    var spinner = document.getElementById('spinner-overlay');
    if (!spinner && goster) {
        spinner = document.createElement('div');
        spinner.id = 'spinner-overlay';
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = '<div class="spinner-border text-primary" role="status">' +
            '<span class="visually-hidden">Yükleniyor...</span></div>';
        document.body.appendChild(spinner);
    } else if (spinner && !goster) {
        spinner.remove();
    }
}

/* ─────────────────────────────────────────────
   GENEL YARDIMCILAR
   ───────────────────────────────────────────── */

/**
 * Tarih nesnesini Türkçe formatla biçimlendir.
 * @param {string|Date} tarih
 * @returns {string} 'GG.AA.YYYY SS:DD'
 */
function tarihBicimle(tarih) {
    var d = tarih instanceof Date ? tarih : new Date(tarih);
    if (isNaN(d.getTime())) return '—';
    var gun  = String(d.getDate()).padStart(2, '0');
    var ay   = String(d.getMonth() + 1).padStart(2, '0');
    var yil  = d.getFullYear();
    var saat = String(d.getHours()).padStart(2, '0');
    var dak  = String(d.getMinutes()).padStart(2, '0');
    return gun + '.' + ay + '.' + yil + ' ' + saat + ':' + dak;
}

/**
 * Para değerini Türk Lirası formatında biçimlendir.
 * @param {number} miktar
 * @returns {string} '1.234,56 ₺'
 */
function paraBicimle(miktar) {
    return Number(miktar).toLocaleString('tr-TR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + ' ₺';
}

/**
 * XSS önlemi için HTML özel karakterlerini kaçır.
 * @param {string} metin
 * @returns {string}
 */
function htmlKacis(metin) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(String(metin)));
    return div.innerHTML;
}
