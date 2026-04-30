# Tum modelleri import et - db.create_all() oncesinde SQLAlchemy'nin
# tum tablolari bilmesi icin gereklidir.
from .roller import Rol
from .kullanicilar import Kullanici
from .kategoriler import Kategori
from .markalar import Marka
from .urunler import Urun
from .urun_ozellikleri import UrunOzelligi
from .magazalar import Magaza
from .magaza_sorumlulari import MagazaSorumlusu
from .stoklar import Stok
from .kampanyalar import Kampanya
from .bildirim_talepleri import BildirimTalebi
from .benzer_urunler import BenzerUrun
