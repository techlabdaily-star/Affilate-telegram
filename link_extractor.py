from __future__ import annotations

import asyncio
import re
from typing import Iterable, List

import aiohttp

URL_REGEX = re.compile(
    r"(https?://[^\s]+)",
    re.IGNORECASE,
)

SUPPORTED_DOMAINS = {
    # Indian e-commerce and major shorteners
    "flipkart.com", "fkrt.co", "myntra.com", "myntr.it", "ajio.com", "ajio.in", "ajiio.co", "amazon.in", "amzn.to", "tatacliq.com", "snapdeal.com", "shopclues.com", "paytmmall.com", "reliancedigital.in", "croma.com", "bigbasket.com", "grofers.com", "jiomart.com", "nykaa.com", "purplle.com", "firstcry.com", "lenskart.com", "pepperfry.com", "urbanladder.com", "zivame.com", "clovia.com", "bewakoof.com", "fbb.co.in", "maxfashion.in", "pantaloons.com", "shoppersstop.com", "vijaysales.com", "spencers.in", "morestore.com", "dmart.in", "supermart.in", "medplusmart.com", "pharmeasy.in", "netmeds.com", "1mg.com", "healthkart.com", "bookmyshow.com", "makemytrip.com", "yatra.com", "goibibo.com", "redbus.in", "irctc.co.in", "cleartrip.com", "ixigo.com", "trivago.in", "agoda.com", "oyorooms.com", "zomato.com", "swiggy.com", "dominos.co.in", "pizzahut.co.in", "faasos.com", "freshmenu.com", "box8.in", "ubereats.com", "foodpanda.in", "magicpin.in", "nearbuy.com", "littleapp.in", "mobikwik.com", "freecharge.in", "phonepe.com", "paytm.com", "google.com", "apple.com", "samsung.com", "mi.com", "realme.com", "oneplus.in", "oppo.com", "vivo.com", "asus.com", "motorola.in", "nokia.com", "lenovo.com", "hp.com", "dell.com", "acer.com", "msi.com", "lg.com", "sony.co.in", "panasonic.com", "philips.co.in", "bajajfinserv.in", "hdfcbank.com", "icicibank.com", "axisbank.com", "kotak.com", "sbi.co.in", "yesbank.in", "indusind.com", "rblbank.com", "idfcfirstbank.com", "federalbank.co.in", "canarabank.com", "unionbankofindia.co.in", "bankofbaroda.in", "punjabandsindbank.co.in", "centralbankofindia.co.in", "ucoebanking.com", "bankofindia.co.in", "indianbank.in", "bankofmaharashtra.in", "dhanbank.in", "karurvysyabank.co.in", "southindianbank.com", "karnatakabank.com", "cityunionbank.com", "tmb.in", "lakshmivilasbank.com", "jandhan.in", "nsdl.co.in", "cdslindia.com", "groww.in", "zerodha.com", "upstox.com", "angelone.in", "icicidirect.com", "hdfcsec.com", "kotaksecurities.com", "motilaloswal.com", "sharekhan.com", "edelweiss.in", "5paisa.com", "sbicapsec.com", "axisdirect.in", "iifl.com", "mstock.com", "paytmmoney.com", "etmoney.com", "policybazaar.com", "coverfox.com", "bankbazaar.com", "paisabazaar.com", "creditmantri.com", "cred.club", "cibil.com", "experian.in", "crifhighmark.com", "equifax.co.in", "transunion.com", "amazon.com", "ebay.com", "aliexpress.com", "walmart.com", "bestbuy.com", "target.com", "homedepot.com", "lowes.com", "costco.com", "macys.com", "kohls.com", "jcpenney.com", "sears.com", "nordstrom.com", "gap.com", "oldnavy.com", "bananarepublic.com", "uniqlo.com", "hollisterco.com", "abercrombie.com", "aeropostale.com", "forever21.com", "hm.com", "zara.com", "ralphlauren.com", "tommy.com", "calvinklein.us", "levis.com", "dockers.com", "wrangler.com", "lee.com", "carters.com", "oshkosh.com", "childrensplace.com", "gymboree.com", "toysrus.com", "babiesrus.com", "buybuybaby.com", "bedbathandbeyond.com", "wayfair.com", "overstock.com", "ikea.com", "pier1.com", "crateandbarrel.com", "westelm.com", "potterybarn.com", "cb2.com", "ashleyfurniture.com", "rooms2go.com", "raymourflanigan.com", "la-z-boy.com", "staples.com", "officedepot.com", "officemax.com", "bhphotovideo.com", "adorama.com", "newegg.com", "microcenter.com", "gamestop.com", "steam.com", "epicgames.com", "origin.com", "gog.com", "greenmangaming.com", "humblebundle.com", "fanatical.com", "playstation.com", "xbox.com", "nintendo.com", "apple.com", "itunes.com", "appstore.com", "google.com", "play.google.com", "microsoft.com", "windows.com", "office.com", "adobe.com", "autodesk.com", "corel.com", "quicken.com", "intuit.com", "turbo.tax", "hrblock.com", "taxact.com", "creditkarma.com", "expedia.com", "booking.com", "hotels.com", "airbnb.com", "vrbo.com", "tripadvisor.com", "travelocity.com", "priceline.com", "orbitz.com", "cheaptickets.com", "agoda.com", "hostelworld.com", "kayak.com", "skyscanner.com", "trivago.com", "lonelyplanet.com", "viator.com", "getyourguide.com", "klook.com", "toursbylocals.com", "eatwith.com", "withlocals.com", "eventbrite.com", "ticketmaster.com", "stubhub.com", "seatgeek.com", "axs.com", "universe.com", "dice.fm", "songkick.com", "bandsintown.com", "festicket.com", "livenation.com", "goldstar.com", "todaytix.com", "groupon.com", "livingsocial.com", "retailmenot.com", "honey.com", "rakuten.com", "topcashback.com", "beFrugal.com", "slickdeals.net", "dealnews.com", "bradsdeals.com", "offers.com", "dealcatcher.com", "techbargains.com", "fatwallet.com", "wethrift.com", "couponcabin.com", "coupons.com", "smartsource.com", "redplum.com", "valpak.com", "shopathome.com", "ebates.com", "swagbucks.com", "myPoints.com", "inboxdollars.com", "shopkick.com", "ibotta.com", "checkout51.com", "savingstar.com", "receiptpal.com", "fetchrewards.com", "drop.com", "paribus.co", "camelcamelcamel.com", "keepa.com", "priceblink.com", "pricegrabber.com", "shopzilla.com", "bizrate.com", "nextag.com", "shopping.com", "shop.com", "jet.com", "boxed.com", "instacart.com", "shipt.com", "postmates.com", "doordash.com", "ubereats.com", "grubhub.com", "caviar.com", "seamless.com", "delivery.com", "eat24.com", "foodler.com", "menulog.com.au", "just-eat.co.uk", "hungryhouse.co.uk", "deliveroo.co.uk", "foodpanda.com", "zomato.com", "swiggy.com", "ubereats.com", "dominos.com", "pizzahut.com", "papaJohns.com", "littlecaesars.com", "bluedart.com", "dhl.com", "fedex.com", "ups.com", "usps.com", "canadapost.ca", "royalmail.com", "hermesworld.com", "dpd.com", "gls-group.eu", "tnt.com", "yodel.co.uk", "parcel2go.com", "shiprocket.in", "delhivery.com", "ekartlogistics.com", "ecomexpress.in", "xpressbees.com", "shadowfax.in", "wowexpress.in", "dotzot.in", "gati.com", "aramex.com", "firstflight.net", "trackon.in", "maruti.co.in", "mahindra.com", "tata.com", "ashokleyland.com", "bajajauto.com", "heromotocorp.com", "hondacarindia.com", "hyundai.com", "marutisuzuki.com", "toyotabharat.com", "ford.com", "chevrolet.com", "volkswagen.co.in", "skoda-auto.co.in", "renault.co.in", "nissan.in", "kia.com", "mgmotor.co.in", "jeep-india.com", "isuzu.in", "mercedes-benz.co.in", "bmw.in", "audi.in", "jaguar.in", "landrover.in", "porsche.com", "lamborghini.com", "ferrari.com", "maserati.com", "bentleymotors.com", "rolls-roycemotorcars.com", "bugatti.com", "tesla.com", "rimac-automobili.com", "lucidmotors.com", "rivian.com", "byd.com", "nio.com", "xpeng.com", "polestar.com", "volvocars.com", "saicmotor.com", "geely.com", "greatwall.com.cn", "cheryinternational.com", "baicintl.com", "dfmglobal.com", "jacen.com", "faw.com", "dongfeng-global.com", "gac.com.cn", "changan.com.cn", "haval-global.com", "wuling.com", "sgmw.com.cn", "maxus.com.cn", "zotye.com", "leopaard.com", "haima.com", "jinbei.com", "foton-global.com", "sinotruk.com", "yutong.com", "kinglong.com.cn", "higer.com", "zhongtong.com", "sunlongbus.com", "anhuijmc.com", "jmc.com.cn", "dfcv.com.cn", "shacman.com", "beiben-trucks.com", "sanygroup.com", "xcmg.com", "liugong.com", "zoomlion.com", "lonkinggroup.com", "sunward.com.cn", "yuchai.com", "weichai.com", "cummins.com", "cat.com", "volvoce.com", "hitachicm.com", "komatsu.com", "jcb.com", "terex.com", "doosan.com", "hyundai-ce.com", "bobcat.com", "kubota.com", "takeuchi-us.com", "yanmar.com", "sumitomokenki.com", "kobelco-kenki.co.jp", "tadano.com", "manitowoc.com", "liebherr.com", "demagmobilecranes.com", "grovecranes.com", "potain.com", "terexcranes.com", "zoomlioncranes.com", "sanycranes.com", "xcmgcranes.com", "fassi.com", "hiab.com", "palfinger.com", "effer.com", "pm-group.eu", "copma.com", "bonfiglioli.com", "cormach.com", "pesci.com", "heila.com", "hammar.com", "macgregor.com", "titancranes.com", "tadano.com", "kato-works.co.jp", "sumitomokenki.com", "kobelco-kenki.co.jp", "manitowoc.com", "liebherr.com", "demagmobilecranes.com", "grovecranes.com", "potain.com", "terexcranes.com", "zoomlioncranes.com", "sanycranes.com", "xcmgcranes.com", "fassi.com", "hiab.com", "palfinger.com", "effer.com", "pm-group.eu", "copma.com", "bonfiglioli.com", "cormach.com", "pesci.com", "heila.com", "hammar.com", "macgregor.com", "titancranes.com",
    # ...add more as needed for your use case
}


def extract_urls(text: str) -> List[str]:
    if not text:
        return []
    return [m.group(1).strip() for m in URL_REGEX.finditer(text)]


async def expand_url(url: str, timeout: float = 3.0) -> str:
    """Expand a short URL to its final destination asynchronously."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                return str(response.url)
    except Exception as e:
        # Log the error for debugging but return original URL
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Failed to expand URL {url}: {e}")
        return url

def filter_supported(urls: Iterable[str]) -> List[str]:
    result: List[str] = []
    for url in urls:
        lower = url.lower()
        if any(domain in lower for domain in SUPPORTED_DOMAINS):
            result.append(url)
    return result

async def extract_and_expand_urls(text: str) -> List[str]:
    """Extract all URLs from text and expand short links asynchronously."""
    urls = extract_urls(text)
    expanded = await asyncio.gather(*(expand_url(url) for url in urls))
    return expanded

# Example usage in your bot:
# urls = extract_and_expand_urls(message_text)
# If you want only the first link:
# link = urls[0] if urls else None

