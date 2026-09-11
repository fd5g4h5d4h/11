# -*- coding: utf-8 -*-
"""دانلودر مستقیم - ویژه اجرا در GitHub Codespaces (آپدیت شده: دانلود موازی + Resume)"""

import os
import re
import shutil
import subprocess
import sys
import time
import json
import logging
import urllib3
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse, unquote

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 🎛️ تنظیمات پارامترها و کنترل لاگ
# ==========================================
MAX_CONCURRENT_DOWNLOADS = 10  # تعداد دانلود و پردازش همزمان
DISABLE_LOGS = False

S3_ACCESS_KEY = "94C16B40AC90748F13D6"
S3_SECRET_KEY = "60d73f03a2dda7b425187f80fc77a1f03477fc25"
S3_ENDPOINT_URL = "https://us-east-1.storage.eudatavault.eu"
S3_BUCKET_NAME = "fit43"
S3_REGION_NAME = "us-east-1"
S3_TARGET_PREFIX = "Movaghat2/"
S3_END_PREFIX = "END-iran2/"

S3_LOCK_PREFIX = "DL/1MohemFTP/LOCKS/"
S3_FOLDER_LOCK_PREFIX = "DL/1MohemFTP/FOLDER_LOCKS/"

PCLOUD_ENABLED = True
PCLOUD_ACCESS_TOKEN = "5wtmZOvQ9JJ0KePRZn0s7JkZ8SEQ0lbrsvkHyVoKq66W3u2yI9ay"
PCLOUD_FOLDER_ID = 21009615698
PCLOUD_API_HOST = "https://eapi.pcloud.com"

CREDIT_TEXT = " *** ارائه شده توسط وبسایت FitoFilm.ir ***"
VIDEO_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.ts', '.m4v', '.webm', '.flv', '.wmv')
VIDEO_EXT_PRIORITY = {'.mkv': 1, '.mp4': 2, '.avi': 3, '.m4v': 4, '.mov': 5, '.webm': 6, '.flv': 7, '.wmv': 8, '.ts': 9}
SKIP_TEXT_FILES = {'kfamov.txt', 'mydramalist.txt'}

replacement_dict = {
    'شوفیلیکس': 'فیتوفیلم', 'showfilix': 'FitoFilm.ir', 'Showfilix': 'FitoFilm.ir',
    'SHOWFILIX': 'FitoFilm.ir', 'showfilix.com': 'FitoFilm.ir', 'Showfilix.com': 'FitoFilm.ir', 'showfilix.ir': 'FitoFilm.ir',
    'Golchindl.Org':'FitoFilm.ir', '[DownloadRooz-com]':'FitoFilm.ir', 'DownloadRooz-com':'FitoFilm.ir', 'DownloadRooz':'FitoFilm.ir',
    '9movie.co':'FitoFilm.ir', 'Film2Movie_Asia':'FitoFilm.ir', 'AvaMovive':'FitoFilm.ir', 'cinematika':'FitoFilm.ir',
    'MetalMovieS':'FitoFilm.ir', 'Baharatmovie':'FitoFilm.ir', 'Asrejavan.com':'FitoFilm.ir', 'filmha.top':'FitoFilm.ir',
    'Film2Movie_li':'FitoFilm.ir', 'Film2Movie':'FitoFilm.ir', 'ZarFilm':'FitoFilm.ir', '9Movie':'FitoFilm.ir',
    'SaberFun':'FitoFilm.ir', '9Movie.Wiki':'FitoFilm.ir', 'DibaMovie':'FitoFilm.ir', 'Filmkio.com':'FitoFilm.ir',
    'ValaMovie.Com':'FitoFilm.ir', 'king-movie.Net':'FitoFilm.ir', 'MoviePovie':'FitoFilm.ir', 'KoreFaair':'FitoFilm.ir',
    'UPTV.co':'FitoFilm.ir', 'TopMoviez.net':'FitoFilm.ir', 'topmovieznet':'FitoFilm.ir', 'barcodesub.ir':'FitoFilm.ir',
    'arirangland.in':'FitoFilm.ir', 'kalicloob.com':'FitoFilm.ir', 'Golchindlz.Top':'FitoFilm.ir', 'Golchindls.Site':'FitoFilm.ir',
    'AsianCenter.iR':'FitoFilm.ir', 'WWW.30NAMATAK.US':'FitoFilm.ir', 'Bia2Movies.Bid':'FitoFilm.ir', 'Saber-Fun.Com':'FitoFilm.ir',
    'NightMovie.Co':'FitoFilm.ir', 'ZarFilm.com':'FitoFilm.ir', 'TinyMoviez.co':'FitoFilm.ir', 'ir-mo.com':'FitoFilm.ir',
    'HexDL.com':'FitoFilm.ir', 'StarkMoviez':'FitoFilm.ir', 'Movie Star':'FitoFilm.ir', 'NightMovie.Top':'FitoFilm.ir',
    'AvaMovie.in':'FitoFilm.ir', 'king-movie.info':'FitoFilm.ir', 'TinyMoviez.us':'FitoFilm.ir', 'MyGolchindl.Top':'FitoFilm.ir',
    'KINGMOVIE.BIZ':'FitoFilm.ir', 'DigiMoviez.Com':'FitoFilm.ir', 'Golchindownload.Site':'FitoFilm.ir', 'Haraj-Serial.Com':'FitoFilm.ir',
    'telegram.me/mykimo':'FitoFilm.ir', 'DibaMoviez.Com':'FitoFilm.ir', 'H E X D L . C O M':'FitoFilm.ir', 'flixdrama.sbs':'FitoFilm.ir',
    'MoboMovies':'FitoFilm.ir', 'MoboMovies.co':'FitoFilm.ir', 'myanimes.ir':'FitoFilm.ir', 'King-Movie.Co':'FitoFilm.ir',
    'Bia2Movies.Com':'FitoFilm.ir', 'Golchindl.Vip':'FitoFilm.ir', 'sisimovi.xyz':'FitoFilm.ir', '2film2.asia':'FitoFilm.ir',
    'MarzFun.ir':'FitoFilm.ir', 'IMDb-DL':'FitoFilm.ir', 'iMovie-DL.Co':'FitoFilm.ir', 'Mshd-Film.Co':'FitoFilm.ir',
    'Filmonix.Org':'FitoFilm.ir', 'KoreFaa.ir':'FitoFilm.ir', 'Golchindlz.xyz':'FitoFilm.ir', 'Golchindl.Fun':'FitoFilm.ir',
    'LiLMedia.TV':'FitoFilm.ir', 'Filmonix.Net':'FitoFilm.ir', 'Arirangland.me':'FitoFilm.ir', 'FOrum.KOrean-Dream.ir':'FitoFilm.ir',
    'AsianMoviee.ir':'FitoFilm.ir', 'www.farsisubtitle.com':'FitoFilm.ir', 'www.sunflowermag.site':'FitoFilm.ir', 'WWW.KING-MOVIE.NET':'FitoFilm.ir',
    'www.aryan-translators.pro':'FitoFilm.ir', 'ProMovi.ir':'FitoFilm.ir', 'Www.barcodesub.ir':'FitoFilm.ir', 'flixdrama.tv':'FitoFilm.ir',
    'moonriverteam.mihanblog.com':'FitoFilm.ir', 'wWw.F2M.top':'FitoFilm.ir', 'KOrean-Dream.ir':'FitoFilm.ir', 'FOrum.KOreanDream.in':'FitoFilm.ir',
    'koreafan.ir':'FitoFilm.ir', 'generaleshop.com/forum':'FitoFilm.ir', 'Dramafa.com':'FitoFilm.ir', 'karanMovie.co':'FitoFilm.ir',
    'TvshOw.Ir':'FitoFilm.ir', 'sunflowermag.com':'FitoFilm.ir', 'koreafan.xyz':'FitoFilm.ir', 'EasyTV.Site':'FitoFilm.ir',
    'SaFun':'FitoFilm.ir', 'se7enDL.ir':'FitoFilm.ir', 'Film2serial.ir':'FitoFilm.ir', 'FitoFilm.irSite':'FitoFilm.ir',
    'www.2pm-persian-ho-ttest.mihanblog.com':'FitoFilm.ir', 'bia2kore.blog.ir':'FitoFilm.ir', 'MyMoviz':'FitoFilm.ir',
    'NightMovie':'FitoFilm.ir', 'KoreFaa.com':'FitoFilm.ir', '@MyGolchindl':'@FitoFilms', '@KINGMOVIE.CO':'@FitoFilms',
    '@SaberFun':'@FitoFilms', '@SaberFunOfficial':'@FitoFilms', 'MetaLMovieS':'FitoFilms', '@ZarFilm_com':'@FitoFilms',
    '@KaranMovie':'@FitoFilms', '@Sample':'@FitoFilms', '@Film2Media_Plus':'@FitoFilms', '@AvaMovie_in':'@FitoFilms',
    '@AioFilmcom':'@FitoFilms', '@AioSub':'@FitoFilms', '@DigiMoviez':'@FitoFilms', '@AjummaWatches':'@FitoFilms',
    '@barcodesubtitle':'@FitoFilms', '@subforu':'@FitoFilms', '@sunflowermag':'@FitoFilms', '@AirenTeam':'@FitoFilms',
    '@ianTeam':'@FitoFilms', '@Northsubtitle':'@FitoFilms', '@moonriverteam':'@FitoFilms', '@moonriverteam_sns':'@FitoFilms',
    '.KIMO':'.FitoFilm.ir', 'KING-MOVIE.Net':'FitoFilm.ir', '@StarDrama':'@FitoFilms', '@kddll':'@FitoFilms', '@kddll88':'@FitoFilms',
    '@KoreanAngels':'@FitoFilms', '@DingoSub':'@FitoFilms', '@KTteam':'@FitoFilms', '@CINAMATAK':'@FitoFilms',
    '@CINAMASUB':'@FitoFilms', '@SAMUELIRN':'@FitoFilms', '@SULBINI':'@FitoFilms', '@ianteam':'@FitoFilms',
    '@_KTteam':'@FitoFilms', '@WEi_IR':'@FitoFilms', '@PersianDreamTeam':'@FitoFilms', '@DramaDLL':'@FitoFilms',
    '@CIX_IRAN':'@FitoFilms', '@MyDAY6Club':'@FitoFilms', '@EPEX_Official':'@FitoFilms', '@programmkorean':'@FitoFilms',
    '@korepedia':'@FitoFilms', '@koreanFaOffice':'@FitoFilms', '@zarfilmz':'@FitoFilms', '@Arirangland':'@FitoFilms',
    '@SmilingPhoenix9':'@FitoFilms', 'hezar-dar.in/forum':'FitoFilm.ir', 'KoreFa.ir':'FitoFilm.ir',
    '30nama.com':'FitoFilm.ir', 'Arirangland. me':'FitoFilm.ir', 'music2sub.mihanblog.com':'FitoFilm.ir', 'wei_ir':'FitoFilm.ir',
    'aryan-translators.ir':'FitoFilm.ir', 'تاپ مُویز':'فيتوفيلم', 'تاپ مویز':'فيتوفيلم', 'سینما تیکا':'فيتوفيلم',
    'سینماتیکا':'فيتوفيلم', 'سینما-تیکا':'فیتوفیلم', 'TopMoviezNet':'FitoFilm.ir', 'ganjdl.ir':'FitoFilm.ir',
    'گنج دانلود':'فیتوفیلم', 'TopMoviez.Net':'FitoFilm.ir', 'TopMoviez . Net':'FitoFilm.ir', 'MoviePovie. Com':'FitoFilm.ir',
    'والا مووي':'فيتوفيلم', 'کــره فا':'فيتوفيلم', 'کينگ مووي':'فيتوفيلم', 'گلچين دانلود':'فیتوفيلم',
    'اينستاگرام گلچين دانلود':'فيتوفيلم', 'روبیکسفا':'فيتوفيلم', 'بياتوموويز':'فيتوفيلم', 'صابرفان':'فيتوفيلم',
    'مووي استار':'فيتوفيلم', 'نایت مووی':'فيتوفيلم', 'تايتي موويز':'فيتوفيلم', 'ايرمو':'فيتوفيلم', 'مرزفان':'فيتوفيلم',
    'دوستي ها':'فيتوفيلم', 'روبـیـکـسـفـا':'فيتوفيلم', 'آوا مووي':'فيتوفيلم', 'آيوفيلم':'فيتوفيلم', 'متال موویز':'فيتوفيلم',
    'مووی پووی':'فيتوفيلم', 'آوامووي':'فيتوفيلم', 'والامووي':'فيتوفيلم', 'دیبا مووی':'فيتوفيلم', 'زرفيلم':'فيتوفيلم',
    'فليکس دراما':'فيتوفيلم', 'موبو فیلم':'فيتوفيلم', 'مشهد فيلم':'فيتوفيلم', 'فيلمونیكس':'فيتوفيلم', 'فيلمو نیکس':'فيتوفيلم',
    'کـره فـا':'فيتوفيلم', 'asiama':'FitoFilm.ir', 'اسيامووي':'فيتوفيلم', 'تیم ترجمه بارکد':'فيتوفيلم',
    'پرشین دریم تیم':'فيتوفيلم', 'تیم ترجمه ی بارکد':'فيتوفيلم', 'وبسایت رسانه کوچک':'فيتوفيلم', '9مووي':'فيتوفيلم',
    'دراما دي ال':'فيتوفيلم', 'کافــــه درامــا':'فیتو فیلم', 'تیم ترجمه پرومووي':'فیتوفیلم', 'تیم ترجمه پروموو':'فيتوفيلم',
    'مون ريور':'فيتوفيلم', 'تیم ترجمه کي تی تیم':'فيتوفيلم', 'پرشـین دريــم تیم':'فيتوفيلم', 'مجله گل آفتابگردان':'فيتوفيلم',
    'کره فا':'فیتوفیلم', 'ناین مووی':'فيتوفيلم', "کره فا":"فيتوفيلم", "کــره فا":"فيتوفيلم", "کـره فا":"فيتوفيلم",
    "کـره فـا":"فيتوفيلم", "کــره fـا":"فیتوفيلم", 'تيـــم ترجـــمه آيــــرن':'فيتوفيلم', 'آیــــ(ما همه مردیم)ــــرن':'فيتوفيلم',
    'تیم ترجمه دینگو':'فیتوفيلم', 'کاری از تیم ترجمه دینگو':'فيتوفيلم', 'بارو مووی':'فیتو فیلم', 'KT Team تیم ترجمه':'فيتوفيلم',
    'هکس دانلود':'فیتوفیلم', 'مای موویز':'فيتوفيلم', 'آسیما مووی':'فیتو فیلم', 'ایان تیم':'فيتوفيلم',
    'تیم ترجمه " کره فن " تقدیم می‌کند':'فيتوفيلم', 'سون دی ال':'فيتوفيلم', 'فـیلــم2mـدیـا':'فیتوفیلم',
    'سینماتک':'فيتوفيلم', 'ایزی تی ویز':'فيتوفيلم', 'ایزی تی وی':'فيتوفيلم', 'پروموو یـز':'فيتوفيلم', 'آوا مووی':'فيتوفيلم',
    'پرشـین دريــم':'فيتوفيلم', 'تـیم تـرجمه کــره فا':'فيتوفيلم', 'Golchindl':'FitoFilm.ir', 'Film2Media':'FitoFilm.ir',
    'DigiMoviez':'FitoFilm.ir', 'AvaMovie':'FitoFilm.ir', 'wWw.F2M.top':'FitoFilm.ir', 'EasyTV':'FitoFilm.ir',
    'Doostihaa.com':'Updoc.ir', 'mkvking.vom':'FitoFilm.ir', 'ديـ جـ _ي مـ _وويـ _ز':'فيتوفيلم',
    'ديجی موویوز':'فيتوفيلم', 'دیجی‌موویز':'FitoFilm.ir',
}

# ==========================================
# لاگ
# ==========================================
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IranDownloader")
logger.handlers.clear()

file_log_handler = logging.FileHandler("process_log.txt", mode='a', encoding='utf-8')
file_log_handler.setFormatter(log_formatter)
logger.addHandler(file_log_handler)

if DISABLE_LOGS:
    logger.setLevel(logging.ERROR)
else:
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)

S3_CONFIG = {
    "ACCESS_KEY": S3_ACCESS_KEY,
    "SECRET_KEY": S3_SECRET_KEY,
    "ENDPOINT_URL": S3_ENDPOINT_URL,
    "BUCKET_NAME": S3_BUCKET_NAME,
    "REGION_NAME": S3_REGION_NAME,
    "TARGET_PREFIX": S3_TARGET_PREFIX,
    "END_PREFIX": S3_END_PREFIX,
    "LOCK_PREFIX": S3_LOCK_PREFIX,
    "FOLDER_LOCK_PREFIX": S3_FOLDER_LOCK_PREFIX
}

def install_requirements():
    stdout_target = subprocess.DEVNULL if DISABLE_LOGS else None
    subprocess.run("sudo apt-get update -qq && sudo apt-get install aria2 ffmpeg curl unzip -y -qq", shell=True, stdout=stdout_target, stderr=stdout_target)
    reqs = ["boto3", "botocore", "requests", "pysrt", "langdetect"]
    for req in reqs:
        try:
            __import__(req)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req, "-q", "--no-warn-script-location"], stdout=stdout_target, stderr=stdout_target)

install_requirements()

import boto3
from botocore.client import Config
import requests
import pysrt

s3_client = boto3.client(
    's3',
    endpoint_url=S3_CONFIG["ENDPOINT_URL"],
    aws_access_key_id=S3_CONFIG["ACCESS_KEY"],
    aws_secret_access_key=S3_CONFIG["SECRET_KEY"],
    region_name=S3_CONFIG["REGION_NAME"],
    config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4', max_pool_connections=100)
)

# ==========================================
# 🧩 توابع پردازش نام و زیرنویس
# ==========================================
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def extract_season_episode(text):
    if not text:
        return None
    m = re.search(r's(\d{1,2})\s*e(\d{1,2})', text, re.IGNORECASE) or re.search(r'(\d{1,2})x(\d{1,2})', text, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r'(?:ep|e|episode)[\s\._-]*(\d{1,3})', text, re.IGNORECASE)
    return (1, int(m.group(1))) if m else None

def clean_name_for_matching(text):
    if not text:
        return ""
    name = Path(text).stem.lower()
    se = extract_season_episode(name)
    se_str = f"s{se[0]:02d}e{se[1]:02d}" if se else ""
    name = re.sub(r's\d{1,2}\s*e\d{1,2}|\d{1,2}x\d{1,2}|(?:ep|episode)[\s\._-]*\d{1,3}', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(19|20)\d{2}\b', '', name)
    name = re.sub(r'\b(2160p|1080p|720p|480p|360p|240p|brrip|bluray|web-dl|webdl|webrip|hdtv|hdrip|dvdrip|x264|x265|hevc|avc|extended|unrated|remastered)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(ss|softsub|soft-sub|hardsub|hard-sub|hs|fansub|dubbed|dub|farsi|persian|eng|english|arabic|korean|kor)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(com|org|net|info|biz|co|ir|us|in|site|top|vip|xyz|sbs|tv|me|bid|asia|pro)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\b(korefaa|korefa|fitofilm|film2movie|golchindl|showfilix|barcodesub|zarfilm|avamovie|digimoviez|tinymoviez|kingmovie|nightmovie|starkmoviez|topmoviez|9movie|hexdl|se7endl|mygolchindl|asianmovie|iranmovie|diba|vala|marz|saber|mobo|lilmedia|pro|asia|metal|baharat|ava|filmkio|uptv|easytv|doostiha|ganj|flx|flix|drama|serial|imdb|mshd|filmonix|arirang|persian|dream|team|sub|subtitle|translate|trans)\b', '', name, flags=re.IGNORECASE)
    clean = re.sub(r'[^a-z0-9]', '', name)
    return f"{clean}{se_str}"

def is_subtitle_url(url):
    path = urlparse(url).path.lower()
    if any(path.endswith(ext) for ext in VIDEO_EXTS):
        return False
    if any(path.endswith(ext) for ext in ['.srt', '.vtt', '.ass', '.ssa', '.sub']):
        return True
    if 'format=srt' in url.lower():
        return True
    return False

def is_series(key_path, filename):
    return bool(re.search(r'(season|\bs\d{1,2}\b|\bs\d{1,2}e\d{1,2}\b|\bep\d{1,3}\b)', f"{key_path} {filename}", re.IGNORECASE))

def is_dubbed_file(text):
    return bool(re.search(r'(dubbed|farsi\.dub|dub|دوبله)', text, re.IGNORECASE))

def replace_in_text(t):
    if not t:
        return ""
    for k, v in replacement_dict.items():
        t = re.sub(re.escape(k), v, t, flags=re.IGNORECASE)
    return re.sub(r'(FitoFilm\.ir[\s\.]?){2,}', 'FitoFilm.ir', t).replace('..', '.')

def fix_tag_format(filename, is_ser=False, is_dubbed=False, has_subtitle=False):
    stem, ext = Path(filename).stem, Path(filename).suffix
    for k, v in sorted(replacement_dict.items(), key=lambda x: len(x[0]), reverse=True):
        if len(k) > 3:
            stem = re.sub(re.escape(k), v, stem, flags=re.IGNORECASE)
    if is_ser:
        stem = re.sub(r'\b(19|20)\d{2}\b', '', stem)
    stem = re.sub(r'[\._\s]?(SS|Softsub|soft-sub|softsub)', '', stem, flags=re.IGNORECASE)
    stem = re.sub(r'\.{2,}', '.', stem).strip('. -_')

    if is_dubbed:
        tag = " (FitoFilm.ir)"
    elif has_subtitle:
        tag = f".{'SS' if is_ser else 'Softsub'} (FitoFilm.ir)"
    else:
        tag = " (FitoFilm.ir)"
    return f"{stem}{tag}{ext}"

def check_and_extract_embedded_subtitles(video_path, work_dir):
    extracted_srt_paths = []
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "s", "-show_entries", "stream=index:stream_tags=language", "-of", "json", video_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        for idx, stream in enumerate(json.loads(result.stdout).get("streams", [])):
            out_srt = os.path.join(work_dir, f"extracted_sub_{random.randint(1000, 9999)}_{idx}.srt")
            if subprocess.run(["ffmpeg", "-y", "-i", video_path, "-map", f"0:{stream.get('index')}", out_srt],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120).returncode == 0 and os.path.getsize(out_srt) > 0:
                extracted_srt_paths.append(out_srt)
    except Exception:
        pass
    return extracted_srt_paths

def convert_srt_to_vtt(srt_path):
    vtt_path = str(Path(srt_path).with_suffix('.vtt'))
    try:
        pysrt.open(srt_path, encoding='utf-8').save(vtt_path, encoding='utf-8')
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(vtt_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n" + content)
        return vtt_path
    except Exception:
        return None

def upload_to_pcloud(local_file_path, custom_filename=None):
    if not PCLOUD_ENABLED or not os.path.exists(local_file_path):
        return False
    target_filename = custom_filename if custom_filename else os.path.basename(local_file_path)
    try:
        with open(local_file_path, 'rb') as f:
            res = requests.post(
                f"{PCLOUD_API_HOST}/uploadfile",
                params={'access_token': PCLOUD_ACCESS_TOKEN, 'folderid': PCLOUD_FOLDER_ID, 'filename': target_filename},
                files={'file': f}, timeout=60
            ).json()
            return res.get('result') == 0
    except Exception:
        return False

def process_and_clean_subtitle_file(local_path):
    if not local_path.lower().endswith('.srt') or not os.path.exists(local_path):
        return local_path
    subs = None
    for enc in ['utf-8', 'utf-8-sig', 'windows-1256', 'cp1252']:
        try:
            subs = pysrt.open(local_path, encoding=enc)
            if subs:
                break
        except Exception:
            continue
    if not subs:
        return local_path
    try:
        for sub in subs:
            sub.text = replace_in_text(sub.text)
        subs.insert(0, pysrt.SubRipItem(1, pysrt.SubRipTime(0, 0, 0, 0), pysrt.SubRipTime(0, 0, 2, 500), CREDIT_TEXT))
        subs.clean_indexes()
        subs.save(local_path, encoding='utf-8')
        return local_path
    except Exception:
        return local_path

def get_matching_srts(video_name, group_srts):
    v_clean = clean_name_for_matching(video_name)
    v_se = extract_season_episode(video_name)
    matched = []
    for s in group_srts:
        if not os.path.exists(s):
            continue
        s_base = os.path.basename(s)
        s_clean = clean_name_for_matching(s_base)
        s_se = extract_season_episode(s_base)
        same_episode = (v_se and s_se and v_se == s_se)
        v_title = re.sub(r's\d+e\d+$', '', v_clean)
        s_title = re.sub(r's\d+e\d+$', '', s_clean)
        same_title = (v_title in s_title or s_title in v_title or v_title == s_title) if (v_title and s_title) else False
        if (same_episode and same_title) or (v_clean and s_clean and (v_clean in s_clean or s_clean in v_clean or v_clean == s_clean)):
            matched.append(s)
    return matched

# ==========================================
# 🛠️ توابع مدیریت قفل S3 و چک فایل موجود
# ==========================================
def is_file_locked_on_s3(lock_key):
    try:
        s3_client.head_object(Bucket=S3_CONFIG["BUCKET_NAME"], Key=lock_key)
        return True
    except Exception:
        return False

def check_file_exists_on_s3(s3_key):
    try:
        s3_client.head_object(Bucket=S3_CONFIG["BUCKET_NAME"], Key=s3_key)
        return True
    except Exception:
        return False

def create_s3_lock(lock_key):
    try:
        time.sleep(random.uniform(0.1, 1.0))
        if is_file_locked_on_s3(lock_key):
            return False
        s3_client.put_object(Bucket=S3_CONFIG["BUCKET_NAME"], Key=lock_key, Body=b"Locked")
        return True
    except Exception:
        return False

def remove_s3_lock(lock_key):
    try:
        s3_client.delete_object(Bucket=S3_CONFIG["BUCKET_NAME"], Key=lock_key)
    except Exception:
        pass

# ==========================================
# دانلود و آپلود مستقیم
# ==========================================
def extract_urls_from_s3_txt(txt_key):
    filename = os.path.basename(txt_key).lower()
    if filename in SKIP_TEXT_FILES:
        logger.info(f"⏭️ Skipping link extraction for excluded file: {filename}")
        return []
    try:
        obj = s3_client.get_object(Bucket=S3_CONFIG["BUCKET_NAME"], Key=txt_key)
        content = obj['Body'].read().decode('utf-8', errors='ignore')
        urls = [line.strip() for line in content.splitlines() if line.strip().startswith(('http://', 'https://'))]
        return urls
    except Exception as e:
        logger.error(f"❌ Failed to extract URLs from {txt_key}: {str(e)}")
        return []

def download_single_file_direct(file_url, download_dir):
    abs_download_dir = os.path.abspath(download_dir)
    os.makedirs(abs_download_dir, exist_ok=True)

    parsed = urlparse(file_url)
    expected_filename = os.path.basename(unquote(parsed.path)) or f"download_{random.randint(1000, 9999)}"
    expected_path = os.path.join(abs_download_dir, expected_filename)

    if os.path.exists(expected_path) and os.path.getsize(expected_path) > 0:
        logger.info(f"⏭️ Local file already exists, skipping download: {expected_filename}")
        return True, expected_path

    tmp_id = random.randint(100000, 999999)
    tmp_file = os.path.join(abs_download_dir, f"input_{tmp_id}.txt")
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(file_url.strip() + "\n")

    aria_args = [
        "aria2c", f"--dir={abs_download_dir}", "-i", tmp_file,
        "-j1", "-x4", "-s4", "--check-certificate=false",
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--header=Accept: */*",
        "--auto-file-renaming=false",
        "--allow-overwrite=true", "--no-conf=true",
        "--timeout=120", "--connect-timeout=30", "--max-tries=10", "--retry-wait=3",
        "--file-allocation=none"
    ]

    try:
        logger.info(f"⬇️ Downloading directly: '{expected_filename}'...")
        res = subprocess.run(
            aria_args,
            cwd=abs_download_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3600
        )

        if res.returncode == 0:
            downloaded = False
            actual_file = expected_path
            if os.path.exists(expected_path) and os.path.getsize(expected_path) > 0:
                downloaded = True
            else:
                for f in os.listdir(abs_download_dir):
                    if f.endswith('.aria2') or f == os.path.basename(tmp_file) or f.startswith('input_'):
                        continue
                    fpath = os.path.join(abs_download_dir, f)
                    if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                        if f.lower().endswith(VIDEO_EXTS + ('.srt', '.vtt', '.ass', '.ssa', '.sub')):
                            downloaded = True
                            actual_file = fpath
                            break
            if downloaded:
                logger.info(f"✅ Download OK ({os.path.getsize(actual_file)} bytes): {os.path.basename(actual_file)}")
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                return True, actual_file
    except Exception as e:
        logger.error(f"❌ Exception downloading '{expected_filename}': {e}")
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

    return False, None

def upload_and_delete(local_path, s3_key):
    clean_s3_key = s3_key.replace("\\", "/").lstrip("/")
    try:
        logger.info(f"☁️ Uploading to S3: {clean_s3_key} ({os.path.getsize(local_path)} bytes)")
        s3_client.upload_file(local_path, S3_CONFIG["BUCKET_NAME"], clean_s3_key)
        logger.info(f"✅ S3 Upload OK: {clean_s3_key}")
        if os.path.exists(local_path):
            os.remove(local_path)
        return True
    except Exception as e:
        logger.error(f"❌ S3 Upload FAILED for {clean_s3_key}: {str(e)}")
        return False

# ==========================================
# پردازش ویدیو تک‌به‌تک
# ==========================================
def process_single_video_pipeline(video_url, target_s3_dir, work_dir, group_srts, used_subs):
    raw_filename = os.path.basename(unquote(urlparse(video_url).path))
    is_ser = is_series(target_s3_dir, raw_filename)
    is_dub = is_dubbed_file(f"{target_s3_dir} {raw_filename}")
    
    # حدس نام نهایی روی S3 جهت چک کردن عدم دانلود تکراری
    expected_s3_name = fix_tag_format(raw_filename, is_ser=is_ser, is_dubbed=is_dub, has_subtitle=True)
    expected_s3_key = os.path.join(target_s3_dir, expected_s3_name).replace("\\", "/")
    
    expected_s3_name_nosub = fix_tag_format(raw_filename, is_ser=is_ser, is_dubbed=is_dub, has_subtitle=False)
    expected_s3_key_nosub = os.path.join(target_s3_dir, expected_s3_name_nosub).replace("\\", "/")

    if check_file_exists_on_s3(expected_s3_key) or check_file_exists_on_s3(expected_s3_key_nosub):
        logger.info(f"⏭️ S3 Resume: File already exists on S3, skipping download: {raw_filename}")
        return True

    success, local_path = download_single_file_direct(video_url, work_dir)
    if not success or not local_path or not os.path.exists(local_path):
        return False

    try:
        video = os.path.basename(local_path)
        all_valid_srts_to_process = check_and_extract_embedded_subtitles(local_path, work_dir) + get_matching_srts(video, group_srts)
        logger.info(f"🎬 Processing video: {video} | Series={is_ser} | Dubbed={is_dub} | MatchedSubs={len(all_valid_srts_to_process)}")

        valid_sub_paths = []
        for srt_path in all_valid_srts_to_process:
            cleaned = process_and_clean_subtitle_file(srt_path)
            if cleaned and os.path.exists(cleaned):
                valid_sub_paths.append(cleaned)
                used_subs.add(srt_path)
                vtt_path = convert_srt_to_vtt(cleaned)
                if PCLOUD_ENABLED:
                    upload_to_pcloud(cleaned)
                    if vtt_path:
                        upload_to_pcloud(vtt_path)

        final_video_path = local_path
        has_subtitles = False
        if valid_sub_paths:
            out_path = os.path.join(work_dir, f"subbed_{random.randint(1000, 9999)}_{video}")
            cmd = ["ffmpeg", "-y", "-i", local_path]
            for sub_p in valid_sub_paths:
                cmd.extend(["-i", sub_p])
            cmd.extend(["-map", "0:v", "-map", "0:a?"])
            for idx in range(1, len(valid_sub_paths) + 1):
                cmd.extend(["-map", f"{idx}:s", f"-metadata:s:s:{idx-1}", f"title=Subtitle {idx}"])
            cmd.extend(["-c", "copy", "-c:s", "srt", out_path])
            ff_res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
            if ff_res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
                final_video_path = out_path
                has_subtitles = True
                if os.path.exists(local_path):
                    os.remove(local_path)

        new_name = fix_tag_format(video, is_ser=is_ser, is_dubbed=is_dub, has_subtitle=has_subtitles)
        s3_upload_key = os.path.join(target_s3_dir, new_name).replace("\\", "/")
        return upload_and_delete(final_video_path, s3_upload_key)
    except Exception as e:
        logger.error(f"❌ Error processing pipeline for {raw_filename}: {e}")
        if os.path.exists(local_path):
            os.remove(local_path)
        return False

# ==========================================
# Pipeline اصلی
# ==========================================
def list_s3_prefixes(prefix):
    prefixes = set()
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=S3_CONFIG["BUCKET_NAME"], Prefix=prefix, Delimiter='/'):
            for p in page.get('CommonPrefixes', []):
                prefixes.add(p['Prefix'])
    except Exception as e:
        logger.error(f"❌ list_s3_prefixes failed: {e}")
    return sorted(prefixes)

def list_s3_keys(prefix):
    keys = []
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=S3_CONFIG["BUCKET_NAME"], Prefix=prefix):
            for obj in page.get('Contents', []):
                keys.append(obj['Key'])
    except Exception as e:
        logger.error(f"❌ list_s3_keys failed: {e}")
    return keys

def move_s3_key(src_key, dst_key):
    try:
        s3_client.copy_object(
            Bucket=S3_CONFIG["BUCKET_NAME"],
            CopySource={'Bucket': S3_CONFIG["BUCKET_NAME"], 'Key': src_key},
            Key=dst_key
        )
        s3_client.delete_object(Bucket=S3_CONFIG["BUCKET_NAME"], Key=src_key)
        return True
    except Exception as e:
        logger.error(f"❌ move_s3_key {src_key} -> {dst_key}: {e}")
        return False

def move_folder_files_to_end(folder_prefix):
    keys = list_s3_keys(folder_prefix)
    for key in keys:
        rel = key[len(folder_prefix):] if key.startswith(folder_prefix) else os.path.basename(key)
        dst = f"{S3_CONFIG['END_PREFIX']}{folder_prefix.rstrip('/').split('/')[-1]}/{rel}"
        if move_s3_key(key, dst):
            logger.info(f"📦 Moved to END: {key} -> {dst}")

def process_one_folder(folder_prefix):
    folder_lock = f"{S3_FOLDER_LOCK_PREFIX}{folder_prefix.replace('/', '_')}.lock"
    if is_file_locked_on_s3(folder_lock):
        logger.info(f"⏭️ Folder locked, skip: {folder_prefix}")
        return
    if not create_s3_lock(folder_lock):
        logger.info(f"⏭️ Could not lock folder: {folder_prefix}")
        return

    work_dir = f"/tmp/work_{random.randint(10000, 99999)}"
    os.makedirs(work_dir, exist_ok=True)
    used_subs = set()

    try:
        keys = list_s3_keys(folder_prefix)
        txt_keys = [k for k in keys if k.lower().endswith('.txt') and os.path.basename(k).lower() not in SKIP_TEXT_FILES]
        if not txt_keys:
            logger.info(f"ℹ️ No downloadable txt in {folder_prefix}")
            move_folder_files_to_end(folder_prefix)
            return

        all_urls = []
        for tk in txt_keys:
            urls = extract_urls_from_s3_txt(tk)
            all_urls.extend(urls)

        if not all_urls:
            logger.info(f"ℹ️ No links in {folder_prefix}")
            move_folder_files_to_end(folder_prefix)
            return

        video_urls = [u for u in all_urls if not is_subtitle_url(u)]
        sub_urls = [u for u in all_urls if is_subtitle_url(u)]

        # ۱. ابتدا تمامی زیرنویس‌ها به‌صورت موازی دانلود می‌شوند
        local_subs = []
        if sub_urls:
            logger.info(f"⬇️ Downloading {len(sub_urls)} subtitles directly in parallel...")
            with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
                futures = [executor.submit(download_single_file_direct, su, work_dir) for su in sub_urls]
                for future in futures:
                    ok, spath = future.result()
                    if ok and spath:
                        local_subs.append(spath)

        target_s3_dir = S3_CONFIG["TARGET_PREFIX"].rstrip("/") + "/" + folder_prefix.rstrip("/").split("/")[-1]

        # ۲. پردازش و دانلود موازی ویدیوها طبق مقدار MAX_CONCURRENT_DOWNLOADS
        if video_urls:
            logger.info(f"⚡ Processing {len(video_urls)} videos in PARALLEL (Max Workers: {MAX_CONCURRENT_DOWNLOADS})...")
            with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
                futures = [
                    executor.submit(
                        process_single_video_pipeline, 
                        vu, 
                        target_s3_dir, 
                        work_dir, 
                        local_subs, 
                        used_subs
                    ) for vu in video_urls
                ]
                
                # منتظر ماندن برای اتمام تمامی تردها
                for future in futures:
                    future.result()

        move_folder_files_to_end(folder_prefix)
        logger.info(f"✅ Folder fully processed: {folder_prefix}")
    except Exception as e:
        logger.error(f"❌ process_one_folder error {folder_prefix}: {e}")
    finally:
        remove_s3_lock(folder_lock)
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass

def run_integrated_pipeline():
    logger.info("🚀 شروع دانلودر مستقیم با قابلیت Resume و آپلود همزمان و موازی")

    INPUT_PREFIX = S3_CONFIG["TARGET_PREFIX"]
    folders = list_s3_prefixes(INPUT_PREFIX)
    if not folders:
        folders = [INPUT_PREFIX]

    for folder in folders:
        process_one_folder(folder)

if __name__ == "__main__":
    run_integrated_pipeline()