from app.adapters.base import BaseAdapter, SourceConfig


APARTMENT_SOURCES = [
    SourceConfig("НАШ.ДОМ.РФ", "https://наш.дом.рф", ("https://наш.дом.рф/новостройки/краснодар/",), "apartment", "official_registry", "dom_rf"),
    SourceConfig("Домострой Краснодар", "https://krasnodar.domostroyrf.ru", ("https://krasnodar.domostroyrf.ru/",), "apartment", "aggregator", "domostroy"),
    SourceConfig("ССК", "https://sskuban.ru", ("https://sskuban.ru/",), "apartment", "developer", "ssk"),
    SourceConfig("ВКБ-Новостройки", "https://vkbn.ru", ("https://vkbn.ru/",), "apartment", "developer", "vkb"),
    SourceConfig("ГК ТОЧНО", "https://tochno.life", ("https://tochno.life/complexes/",), "apartment", "developer", "tochno"),
    SourceConfig("DOGMA", "https://dogma.ru", ("https://dogma.ru/kvartiry",), "apartment", "developer", "dogma"),
    SourceConfig("СК Семья", "https://family-yug.ru", ("https://family-yug.ru/novostroyki/",), "apartment", "developer", "family"),
    SourceConfig("Неометрия", "https://neometria.ru", ("https://neometria.ru/krasnodar/kupit-kvartiru",), "apartment", "developer", "neometria"),
    SourceConfig("НВМ", "https://gk-nvm.ru", ("https://gk-nvm.ru/",), "apartment", "developer", "nvm"),
    SourceConfig("ЕкатеринодарИнвест-Строй", "https://ek-invest.ru", ("https://ek-invest.ru/",), "apartment", "developer", "ek_invest"),
    SourceConfig("Novostroyka123", "https://novostroyka123.ru", ("https://novostroyka123.ru/new-buildings/",), "apartment", "aggregator", "novostroyka123"),
    SourceConfig("Novostrojki-KRD", "https://novostrojki-krd.ru", ("https://novostrojki-krd.ru/",), "apartment", "aggregator", "novostrojki_krd"),
    SourceConfig("23kvartiri", "https://23kvartiri.ru", ("https://23kvartiri.ru/",), "apartment", "aggregator", "23kvartiri"),
    SourceConfig("Krasdom", "https://krasdom.ru", ("https://krasdom.ru/novostroyki/krasnodar/",), "apartment", "aggregator", "krasdom"),
]


HOUSE_SOURCES = [
    SourceConfig("Doma-kr", "https://doma-kr.ru", ("https://doma-kr.ru/",), "house", "house_catalog", "doma_kr"),
    SourceConfig("КП Краснодар", "https://kp-krd.ru", ("https://kp-krd.ru/doma-kottedzhi-taunkhausy",), "house", "house_catalog", "kp_krd"),
    SourceConfig("Поселки Краснодара", "https://поселки-краснодара.рф", ("https://поселки-краснодара.рф/",), "house", "house_catalog", "poselki_krd"),
    SourceConfig("23kvartiri", "https://23kvartiri.ru", ("https://23kvartiri.ru/",), "house", "aggregator", "23kvartiri_house"),
    SourceConfig("Novostrojki-KRD", "https://novostrojki-krd.ru", ("https://novostrojki-krd.ru/",), "house", "aggregator", "novostrojki_krd_house"),
]


class DomRfAdapter(BaseAdapter):
    pass


class DomostroyAdapter(BaseAdapter):
    pass


class SskAdapter(BaseAdapter):
    pass


class VkbAdapter(BaseAdapter):
    pass


class TochnoAdapter(BaseAdapter):
    pass


class DogmaAdapter(BaseAdapter):
    pass


class FamilyAdapter(BaseAdapter):
    pass


class NeometriaAdapter(BaseAdapter):
    pass


class DomaKrAdapter(BaseAdapter):
    pass


class KpKrdAdapter(BaseAdapter):
    pass


def build_adapters(property_type: str) -> list[BaseAdapter]:
    sources = HOUSE_SOURCES if property_type == "house" else APARTMENT_SOURCES
    return [BaseAdapter(source) for source in sources]
