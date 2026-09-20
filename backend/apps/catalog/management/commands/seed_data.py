import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.accounts.models import Address, UserProfile
from apps.catalog.models import Category, ProductType, Brand, Product, ProductImage, ProductSpecification
from apps.promotions.models import Coupon, Banner
from apps.reviews.models import Review
from apps.orders.models import Order, OrderItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds SoundSphere database with 8 categories, 25 product types, 13 brands, 35+ products, and coupons.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Seeding SoundSphere Database ---'))

        # 1. Admin & Demo User
        admin_user, created = User.objects.get_or_create(
            email='admin@soundsphere.com',
            defaults={
                'username': 'admin',
                'first_name': 'SoundSphere',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('AdminPassword123!')
            admin_user.save()
            UserProfile.objects.get_or_create(user=admin_user)
            self.stdout.write(self.style.SUCCESS('Created superuser: admin@soundsphere.com / AdminPassword123!'))

        demo_user, created = User.objects.get_or_create(
            email='customer@soundsphere.com',
            defaults={
                'username': 'alex_audiophile',
                'first_name': 'Alex',
                'last_name': 'Rivers',
                'phone': '+1 (555) 234-5678',
            }
        )
        if created:
            demo_user.set_password('CustomerPassword123!')
            demo_user.save()
            UserProfile.objects.get_or_create(user=demo_user)
            Address.objects.get_or_create(
                user=demo_user,
                full_name='Alex Rivers',
                phone='+1 (555) 234-5678',
                address_line='742 Evergreen Terrace, Apt 4B',
                city='San Francisco',
                district='California',
                postal_code='94107',
                country='United States',
                is_default=True
            )
            self.stdout.write(self.style.SUCCESS('Created demo customer: customer@soundsphere.com / CustomerPassword123!'))

        # 2. Categories & Product Types (All 8 categories & 25 exact types)
        categories_data = [
            {
                'name': 'Bluetooth Speakers',
                'description': 'Engineered for untethered acoustic freedom. From ultra-compact pocket drivers to high-decibel outdoor party beasts.',
                'icon_svg': 'speaker-bluetooth.svg',
                'product_types': [
                    'Mini Bluetooth Speaker',
                    'Portable Bluetooth Speaker',
                    'Waterproof Bluetooth Speaker',
                    'Party Speaker',
                    'Trolley Speaker',
                    'Karaoke Speaker',
                    'Tower Speaker',
                ]
            },
            {
                'name': 'Soundbars',
                'description': 'Cinematic audio bars featuring Dolby Atmos spatial decoding, multi-channel soundstages, and deep wireless bass.',
                'icon_svg': 'speaker-soundbar.svg',
                'product_types': [
                    'Soundbar',
                    '2.1 Channel Soundbar',
                    'Dolby Atmos Soundbar',
                ]
            },
            {
                'name': 'Multimedia Speakers',
                'description': 'Precision 2.0, 2.1, and 4.1 desktop and living room speakers delivering crisp vocals and punchy sub-bass.',
                'icon_svg': 'speaker-multimedia.svg',
                'product_types': [
                    '2.0 Multimedia Speaker',
                    '2.1 Multimedia Speaker',
                    '4.1 Multimedia Speaker',
                ]
            },
            {
                'name': 'Home Theater',
                'description': 'Pure 5.1 and 7.1 surround sound architectures that transport movie theater acoustics directly into your living room.',
                'icon_svg': 'speaker-hometheater.svg',
                'product_types': [
                    '5.1 Home Theater Speaker',
                ]
            },
            {
                'name': 'Bookshelf & Hi-Fi Speakers',
                'description': 'Audiophile-grade studio monitors, active bookshelf pairs, and massive floor-standing acoustic drivers.',
                'icon_svg': 'speaker-bookshelf.svg',
                'product_types': [
                    'Bookshelf Speaker',
                    'Active Bookshelf Speaker',
                    'Floor Standing Speaker',
                    'Subwoofer',
                    'Wireless Subwoofer',
                ]
            },
            {
                'name': 'Gaming & Computer Audio',
                'description': 'Ultra-low latency drivers, immersive spatial stereo imaging, and customizable dynamic RGB lighting.',
                'icon_svg': 'speaker-gaming.svg',
                'product_types': [
                    'Gaming Speaker',
                    'RGB Gaming Speaker',
                    'Computer Speaker',
                ]
            },
            {
                'name': 'Professional Audio',
                'description': 'Tour-grade portable PA line arrays and reference studio monitors tuned for zero coloration and extreme fidelity.',
                'icon_svg': 'speaker-propa.svg',
                'product_types': [
                    'Portable PA Speaker',
                    'Studio Monitor Speaker',
                ]
            },
            {
                'name': 'Karaoke',
                'description': 'High-power wireless karaoke systems equipped with digital DSP echo effects and ultra-clear wireless microphones.',
                'icon_svg': 'speaker-karaoke.svg',
                'product_types': [
                    'Wireless Karaoke Speaker',
                ]
            },
        ]

        cat_map = {}
        type_map = {}

        for cat_info in categories_data:
            cat_obj, _ = Category.objects.get_or_create(
                name=cat_info['name'],
                defaults={
                    'description': cat_info['description'],
                    'icon_svg': cat_info['icon_svg'],
                    'is_active': True,
                }
            )
            cat_map[cat_obj.name] = cat_obj

            for pt_name in cat_info['product_types']:
                pt_obj, _ = ProductType.objects.get_or_create(
                    category=cat_obj,
                    name=pt_name,
                    defaults={
                        'description': f"High-performance {pt_name} crafted for premium acoustic reproduction.",
                        'is_active': True
                    }
                )
                type_map[pt_name] = pt_obj

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(cat_map)} categories and {len(type_map)} product types."))

        # 3. Brands (13 Brands)
        brands_data = [
            {'name': 'JBL', 'website': 'https://www.jbl.com', 'desc': 'Legendary Pro Sound and rugged portable audio.'},
            {'name': 'Sony', 'website': 'https://www.sony.com', 'desc': 'Pioneers in high-resolution audio, Extra Bass, and spatial sound.'},
            {'name': 'Bose', 'website': 'https://www.bose.com', 'desc': 'World-renowned acoustic engineering and premium noise control.'},
            {'name': 'Marshall', 'website': 'https://www.marshallheadphones.com', 'desc': 'Iconic rock ‘n’ roll heritage with modern wireless tech.'},
            {'name': 'Anker', 'website': 'https://www.soundcore.com', 'desc': 'Cutting-edge Soundcore audio with incredible battery efficiency.'},
            {'name': 'Edifier', 'website': 'https://www.edifier.com', 'desc': 'Mastercrafted studio bookshelf speakers and Hi-Res desktop audio.'},
            {'name': 'Yamaha', 'website': 'https://www.yamaha.com', 'desc': 'Professional concert hall acoustics and high-fidelity AV sound.'},
            {'name': 'Logitech', 'website': 'https://www.logitech.com', 'desc': 'High-performance PC desktop audio and immersive gaming speakers.'},
            {'name': 'Audio-Technica', 'website': 'https://www.audio-technica.com', 'desc': 'Decades of Japanese acoustic precision and studio monitoring.'},
            {'name': 'Harman Kardon', 'website': 'https://www.harmankardon.com', 'desc': 'Sculptural luxury designs with room-filling spatial sound.'},
            {'name': 'Samsung', 'website': 'https://www.samsung.com', 'desc': 'True Dolby Atmos Q-Symphony soundbar systems.'},
            {'name': 'LG', 'website': 'https://www.lg.com', 'desc': 'Meridian-tuned soundbars and XBOOM party audio.'},
            {'name': 'Xiaomi', 'website': 'https://www.mi.com', 'desc': 'Smart connected audio with minimalist design and punchy sound.'},
        ]

        brand_map = {}
        for b in brands_data:
            brand_obj, _ = Brand.objects.get_or_create(
                name=b['name'],
                defaults={'website': b['website'], 'description': b['desc'], 'is_active': True}
            )
            brand_map[b['name']] = brand_obj

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(brand_map)} audio brands."))

        # 4. Realistic Audio Products (35+ products covering all 25 product types)
        products_catalog = [
            # Bluetooth Speakers
            {
                'name': 'Flip 7 Ultra Waterproof Speaker',
                'sku': 'JBL-FLIP7-BLK',
                'brand': 'JBL',
                'category': 'Bluetooth Speakers',
                'product_type': 'Waterproof Bluetooth Speaker',
                'price': Decimal('139.99'),
                'discount_price': Decimal('119.99'),
                'stock': 45,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-bluetooth.svg',
                'short': 'IP67 waterproof and dustproof portable speaker with racetrack driver and 14 hours playtime.',
                'desc': 'Take crystal-clear acoustic fidelity wherever adventure leads. The JBL Flip 7 Ultra delivers deep, impactful bass and punchy midrange, wrapped in an IP67 military-grade waterproof housing. Features Auracast multi-speaker pairing.',
                'specs': [
                    ('Output Power', '30W RMS'),
                    ('Battery Life', '14 Hours Playtime'),
                    ('Water Resistance', 'IP67 Waterproof & Dustproof'),
                    ('Bluetooth Version', 'Bluetooth 5.3 + LE Audio'),
                    ('Frequency Response', '60Hz – 20kHz'),
                    ('Weight', '550 grams'),
                ]
            },
            {
                'name': 'Soundcore Motion 300 Wireless Hi-Res',
                'sku': 'ANK-MOT300-SLV',
                'brand': 'Anker',
                'category': 'Bluetooth Speakers',
                'product_type': 'Portable Bluetooth Speaker',
                'price': Decimal('79.99'),
                'discount_price': None,
                'stock': 60,
                'is_featured': True,
                'is_new_arrival': True,
                'image_url': '/static/images/speaker-bluetooth.svg',
                'short': 'Wireless Hi-Res portable speaker featuring SmartTune adaptive acoustic technology.',
                'desc': 'Experience Studio Hi-Res wireless sound on the go. Equipped with LDAC codec support and SmartTune DSP that auto-detects speaker orientation to optimize stereo separation.',
                'specs': [
                    ('Output Power', '30W Stereo'),
                    ('Audio Codec', 'LDAC / AAC / SBC'),
                    ('Battery Life', '13 Hours'),
                    ('Water Resistance', 'IPX7'),
                    ('SmartTune DSP', 'Auto Orientation Tuning'),
                ]
            },
            {
                'name': 'Emberton II Portable Rock Speaker',
                'sku': 'MSH-EMB2-BRS',
                'brand': 'Marshall',
                'category': 'Bluetooth Speakers',
                'product_type': 'Portable Bluetooth Speaker',
                'price': Decimal('179.99'),
                'discount_price': Decimal('159.99'),
                'stock': 28,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-bluetooth.svg',
                'short': '360° True Stereophonic acoustic design with classic Marshall vintage brass aesthetics.',
                'desc': 'Emberton II delivers 30+ hours of portable playtime on a single charge. Uses Marshall True Stereophonic multidirectional audio to ensure sweet-spot listening from any angle.',
                'specs': [
                    ('Output Power', '2x 10W Class-D Amplifiers'),
                    ('Battery Life', '30+ Hours'),
                    ('Acoustic Architecture', 'True Stereophonic 360°'),
                    ('Water Resistance', 'IP67'),
                    ('Stack Mode', 'Connect multiple Emberton IIs'),
                ]
            },
            {
                'name': 'SRS-XB100 Pocket Wireless Speaker',
                'sku': 'SNY-XB100-BLU',
                'brand': 'Sony',
                'category': 'Bluetooth Speakers',
                'product_type': 'Mini Bluetooth Speaker',
                'price': Decimal('59.99'),
                'discount_price': Decimal('49.99'),
                'stock': 85,
                'is_new_arrival': True,
                'image_url': '/static/images/speaker-bluetooth.svg',
                'short': 'Ultra-compact mini Bluetooth speaker with Sound Diffusion Processor and extra bass radiator.',
                'desc': 'Small body, expansive sound. The Sony SRS-XB100 packs an off-center diaphragm and sound diffusion processor to spread acoustic pressure evenly in pocket-sized portability.',
                'specs': [
                    ('Driver Size', '46mm Monoaural'),
                    ('Battery Life', '16 Hours'),
                    ('Water Resistance', 'IP67 Waterproof/Dustproof'),
                    ('Hands-free Mic', 'Echo Cancelling Microphone'),
                    ('Weight', '274g'),
                ]
            },
            {
                'name': 'PartyBox Club 120 High-Power Beast',
                'sku': 'JBL-PB120-RGB',
                'brand': 'JBL',
                'category': 'Bluetooth Speakers',
                'product_type': 'Party Speaker',
                'price': Decimal('399.99'),
                'discount_price': Decimal('349.99'),
                'stock': 15,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-karaoke.svg',
                'short': '160W explosive party speaker with dynamic synced light show and dual mic/guitar inputs.',
                'desc': 'Turn any venue into a concert arena. The JBL PartyBox Club 120 delivers thunderous JBL Original Pro Sound with AI Sound Boost analysis and a full-body rhythmic RGB strobe light show.',
                'specs': [
                    ('Output Power', '160W RMS'),
                    ('Battery Life', '12 Hours (Swappable battery)'),
                    ('Inputs', 'Dual 1/4" Mic & Guitar Inputs'),
                    ('Lightshow', 'Futuristic Starry RGB Light Grid'),
                    ('Bass Boost', 'Deep Bass Dual Mode'),
                ]
            },
            {
                'name': 'XBOOM XL7S High Power Trolley Speaker',
                'sku': 'LG-XL7S-TRL',
                'brand': 'LG',
                'category': 'Bluetooth Speakers',
                'product_type': 'Trolley Speaker',
                'price': Decimal('499.99'),
                'discount_price': Decimal('449.99'),
                'stock': 8,
                'low_stock_threshold': 3,
                'image_url': '/static/images/speaker-karaoke.svg',
                'short': '250W giant trolley party speaker with telescopic handle, smooth wheels, and pixel LED screen.',
                'desc': 'Rolling power on wheels. The LG XBOOM XL7S combines an 8-inch giant woofer, dual 2.5-inch dome tweeters, and customizable Dot Matrix text display for total mobile event performance.',
                'specs': [
                    ('Output Power', '250W Total System Power'),
                    ('Woofer', '8-inch Giant Bass Driver'),
                    ('Mobility', 'Telescopic Handle & Rugged Wheels'),
                    ('Display', 'Customizable Pixel LED Text Screen'),
                    ('Battery', '18 Hours Continuous Playback'),
                ]
            },
            {
                'name': 'Soundcore Rave Neo 2 Tower Beast',
                'sku': 'ANK-RAVETW-01',
                'brand': 'Anker',
                'category': 'Bluetooth Speakers',
                'product_type': 'Tower Speaker',
                'price': Decimal('229.99'),
                'discount_price': Decimal('199.99'),
                'stock': 22,
                'image_url': '/static/images/speaker-karaoke.svg',
                'short': '80W standing tower speaker with BassUp technology and floating waterproof chassis.',
                'desc': 'Vertical acoustic projection designed to energize outdoor gatherings. Features dual passive radiators and 360-degree beat-driven illumination.',
                'specs': [
                    ('Output Power', '80W RMS'),
                    ('Bass Tech', 'BassUp 2.0 DSP'),
                    ('Water Resistance', 'IPX7 Waterproof (It floats!)'),
                    ('PartyCast', 'Sync up to 100+ Speakers'),
                ]
            },
            {
                'name': 'SingMaster Pro Bluetooth Karaoke Box',
                'sku': 'SNY-SING-K1',
                'brand': 'Sony',
                'category': 'Bluetooth Speakers',
                'product_type': 'Karaoke Speaker',
                'price': Decimal('279.99'),
                'discount_price': Decimal('249.99'),
                'stock': 19,
                'image_url': '/static/images/speaker-karaoke.svg',
                'short': 'All-in-one Bluetooth karaoke speaker with built-in vocal fader and echo effects processor.',
                'desc': 'Turn any music track into an instant karaoke backing track. Built-in voice canceller strips vocals from regular Bluetooth streams so you take center stage.',
                'specs': [
                    ('Output Power', '100W Peak'),
                    ('Vocal Effects', 'Echo, Pitch Control, Voice Morph'),
                    ('Microphones', 'Includes 1 Wireless VHF Microphone'),
                    ('Battery', '10 Hours Playtime'),
                ]
            },

            # Soundbars
            {
                'name': 'Q-Series HW-Q990D 11.1.4ch Soundbar',
                'sku': 'SAM-Q990D-ATM',
                'brand': 'Samsung',
                'category': 'Soundbars',
                'product_type': 'Dolby Atmos Soundbar',
                'price': Decimal('1499.99'),
                'discount_price': Decimal('1299.99'),
                'stock': 12,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-soundbar.svg',
                'short': 'Flagship 11.1.4 Channel wireless Dolby Atmos system with up-firing rear speakers and 8" wireless subwoofer.',
                'desc': 'The pinnacle of home theater acoustics. 22 discrete speakers create a three-dimensional hemispherical soundfield. Features SpaceFit Sound Pro auto-room calibration and HDMI 2.1 4K 120Hz passthrough.',
                'specs': [
                    ('Channels', '11.1.4 Discrete Channels (22 Drivers)'),
                    ('Spatial Decoders', 'Dolby Atmos, DTS:X, Dolby TrueHD'),
                    ('Subwoofer', '8-inch Wireless Acoustic Lens Sub'),
                    ('Rear Speakers', 'Wireless Up-Firing & Side-Firing Units'),
                    ('Connectivity', 'HDMI eARC, 2x HDMI 2.1 Inputs, Wi-Fi, AirPlay 2'),
                ]
            },
            {
                'name': 'Cinema SB580 3.1 Dolby Atmos Bar',
                'sku': 'JBL-SB580-ATM',
                'brand': 'JBL',
                'category': 'Soundbars',
                'product_type': 'Dolby Atmos Soundbar',
                'price': Decimal('449.99'),
                'discount_price': Decimal('389.99'),
                'stock': 24,
                'image_url': '/static/images/speaker-soundbar.svg',
                'short': '440W 3.1 channel soundbar with dedicated center dialogue driver and 6.5" wireless sub.',
                'desc': 'Crystal clear dialogue meets earth-shaking movie bass. Virtual Dolby Atmos decoding creates an expansive soundstage without cluttering your living room with extra cables.',
                'specs': [
                    ('Output Power', '440W Max Power'),
                    ('Subwoofer', '6.5-inch Wireless Subwoofer'),
                    ('Dialogue Enhancement', 'Dedicated Center Channel with PureVoice'),
                    ('Inputs', 'HDMI eARC, Optical, Bluetooth 5.3'),
                ]
            },
            {
                'name': 'Smart Soundbar 600 Compact Spatial',
                'sku': 'BOS-SB600-BLK',
                'brand': 'Bose',
                'category': 'Soundbars',
                'product_type': 'Soundbar',
                'price': Decimal('499.00'),
                'discount_price': None,
                'stock': 18,
                'is_featured': True,
                'image_url': '/static/images/speaker-soundbar.svg',
                'short': 'Compact standalone Dolby Atmos soundbar with proprietary TrueSpace technology and upward transducers.',
                'desc': 'Bose Soundbar 600 delivers shockingly immersive audio for its slim size. Five transducers spread sound all around your room, even from overhead.',
                'specs': [
                    ('Transducers', '5 Total (including 2 Upward-Firing)'),
                    ('Spatial Tech', 'Bose TrueSpace Spatial Processing'),
                    ('Voice Assistant', 'Amazon Alexa & Google Assistant built-in'),
                    ('App Control', 'Bose Music App'),
                ]
            },
            {
                'name': 'SR-B20A 2.1 All-in-One Soundbar',
                'sku': 'YAM-SRB20A-01',
                'brand': 'Yamaha',
                'category': 'Soundbars',
                'product_type': '2.1 Channel Soundbar',
                'price': Decimal('199.95'),
                'discount_price': Decimal('169.95'),
                'stock': 35,
                'image_url': '/static/images/speaker-soundbar.svg',
                'short': 'Built-in dual subwoofers with Clear Voice technology and DTS Virtual:X 3D surround.',
                'desc': 'All-in-one simplicity without needing a separate floor subwoofer. Dual internal 3-inch subwoofers deliver rich bass response directly from the slim bar.',
                'specs': [
                    ('Channels', '2.1 Channel (Dual Internal Subwoofers)'),
                    ('Surround Tech', 'DTS Virtual:X'),
                    ('Dialogue Clarity', 'Yamaha Clear Voice DSP'),
                    ('Connectivity', 'HDMI ARC, Optical, Bluetooth'),
                ]
            },

            # Multimedia Speakers
            {
                'name': 'S350DB 2.1 Powered Multimedia Bookshelf',
                'sku': 'EDF-S350DB-WOD',
                'brand': 'Edifier',
                'category': 'Multimedia Speakers',
                'product_type': '2.1 Multimedia Speaker',
                'price': Decimal('399.99'),
                'discount_price': Decimal('349.99'),
                'stock': 14,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-multimedia.svg',
                'short': 'Audiophile 150W 2.1 active speaker system with 8" massive subwoofer and titanium dome tweeters.',
                'desc': 'The benchmark in computer and media audio. S350DB features a classic retro cherry wood cabinet, planar titanium dome tweeters, and an 8-inch long-throw subwoofer for studio-grade realism.',
                'specs': [
                    ('Total Output', '150W RMS (Sub: 70W + Satellites: 2x 40W)'),
                    ('Subwoofer Driver', '8-inch Long-Throw Bass Unit'),
                    ('Tweeter', '3/4" Titanium Dome Tweeters'),
                    ('DSP Architecture', 'Texas Instruments TAS5754M Digital Processing'),
                    ('Remote', 'Wireless Precision Dial Remote Included'),
                ]
            },
            {
                'name': 'R1280DBs 2.0 Active Bluetooth Monitors',
                'sku': 'EDF-R1280DBS-BRN',
                'brand': 'Edifier',
                'category': 'Multimedia Speakers',
                'product_type': '2.0 Multimedia Speaker',
                'price': Decimal('159.99'),
                'discount_price': Decimal('139.99'),
                'stock': 40,
                'image_url': '/static/images/speaker-multimedia.svg',
                'short': 'Classic 42W 2.0 studio desk monitors with Subwoofer Line-Out and optical/coaxial inputs.',
                'desc': 'Clean, uncolored acoustic performance in a handcrafted wooden MDF enclosure. Includes dedicated sub-out port to connect an external active sub when needed.',
                'specs': [
                    ('Output Power', '42W RMS'),
                    ('Drivers', '4-inch Bass Driver + 13mm Silk Dome Tweeter'),
                    ('Sub Out', 'Dedicated Subwoofer Output Jack'),
                    ('Cabinet', '100% MDF Wooden Housing'),
                ]
            },
            {
                'name': 'Z607 4.1 Surround Sound Multimedia System',
                'sku': 'LOG-Z607-41SS',
                'brand': 'Logitech',
                'category': 'Multimedia Speakers',
                'product_type': '4.1 Multimedia Speaker',
                'price': Decimal('129.99'),
                'discount_price': None,
                'stock': 26,
                'image_url': '/static/images/speaker-multimedia.svg',
                'short': '160W peak multimedia 4.1 surround system with booming subwoofer and Bluetooth 5.0.',
                'desc': 'Fills your room with vibrant sound from your TV, PC, phone, or gaming console. Long 6.2-meter rear satellite cables allow effortless room arrangement.',
                'specs': [
                    ('Peak Power', '160W (80W RMS)'),
                    ('Subwoofer', '5.25-inch Bass Driver'),
                    ('Satellite Array', '4 Satellites + 1 Subwoofer'),
                    ('Inputs', 'Bluetooth 5.0, 3.5mm AUX, RCA, SD Card, USB'),
                ]
            },

            # Home Theater
            {
                'name': 'AuraCinema 5.1 True Surround System',
                'sku': 'SNY-HT-AURA51',
                'brand': 'Sony',
                'category': 'Home Theater',
                'product_type': '5.1 Home Theater Speaker',
                'price': Decimal('799.99'),
                'discount_price': Decimal('699.99'),
                'stock': 10,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-hometheater.svg',
                'short': '1000W total system power with dual floorstanding tallboys, dedicated center, and 10" powered sub.',
                'desc': 'Experience true Dolby Digital cinema surround with five real acoustic channels and an active 10-inch subwoofer. Delivers pristine vocal clarity and chest-thumping action dynamics.',
                'specs': [
                    ('System Power', '1000W Total Output'),
                    ('Configuration', '5.1 Real Discrete Surround'),
                    ('Subwoofer', '10-inch High-Excursion Powered Sub'),
                    ('Tallboy Towers', 'Dual 3-way Floorstanding Columns'),
                    ('Surround Decoder', 'Dolby Digital Pro Logic II'),
                ]
            },
            {
                'name': 'NS-51 Series 5.1 Audiophile Package',
                'sku': 'YAM-NS51-51PKG',
                'brand': 'Yamaha',
                'category': 'Home Theater',
                'product_type': '5.1 Home Theater Speaker',
                'price': Decimal('1199.00'),
                'discount_price': Decimal('1049.00'),
                'stock': 7,
                'low_stock_threshold': 2,
                'image_url': '/static/images/speaker-hometheater.svg',
                'short': 'High-performance home theater speaker package producing natural, balanced concert sound.',
                'desc': 'Matched acoustic voicing across all five channels with low-resonance bass reflex floorstanders. Designed for demanding movie soundtracks and lossless orchestral music.',
                'specs': [
                    ('Floorstanders', 'Dual 6.5" Woofers + 1" Soft Dome Tweeters'),
                    ('Center Channel', 'Dual 4" Drivers Acoustic Suspension'),
                    ('Surround Bookshelves', '4" Compact Satellite Pair'),
                    ('Subwoofer', 'Advanced YST II 8" Active Sub'),
                ]
            },

            # Bookshelf & Hi-Fi
            {
                'name': 'S880DB Hi-Res Certified Active Bookshelf',
                'sku': 'EDF-S880DB-HRS',
                'brand': 'Edifier',
                'category': 'Bookshelf & Hi-Fi Speakers',
                'product_type': 'Active Bookshelf Speaker',
                'price': Decimal('299.99'),
                'discount_price': Decimal('269.99'),
                'stock': 20,
                'is_featured': True,
                'image_url': '/static/images/speaker-bookshelf.svg',
                'short': 'Hi-Res Audio Certified active compact desktop monitors with XMOS USB audio decoder.',
                'desc': 'Certified for studio Hi-Res playback up to 24-bit/192kHz without downsampling. Titanium dome tweeters and 3.75-inch aluminum bass drivers deliver stunning clarity.',
                'specs': [
                    ('Hi-Res Certification', '192kHz / 24-bit XMOS Processor'),
                    ('Amplifier', 'Class-D Digital Bi-Amplifier'),
                    ('Cabinet', 'Matte White with Natural Wood Finish'),
                    ('Remote', 'Circular IR Remote Controller'),
                ]
            },
            {
                'name': 'Debut 2.0 B6.2 Passive Bookshelf Monitors',
                'sku': 'ADT-B62-PAS',
                'brand': 'Audio-Technica',
                'category': 'Bookshelf & Hi-Fi Speakers',
                'product_type': 'Bookshelf Speaker',
                'price': Decimal('349.99'),
                'discount_price': None,
                'stock': 16,
                'image_url': '/static/images/speaker-bookshelf.svg',
                'short': '6.5-inch woven aramid-fiber driver with wide-dispersion waveguide tweeter.',
                'desc': 'Audiophile reference passive bookshelf pair. Aramid fiber cones provide superior stiffness and damping compared to poly or paper cones.',
                'specs': [
                    ('Frequency Range', '44Hz – 35kHz'),
                    ('Nominal Impedance', '6 Ohms'),
                    ('Sensitivity', '87 dB @ 2.83 v/1m'),
                    ('Cabinet Type', 'Front Dual Flared Bass Reflex Port'),
                ]
            },
            {
                'name': 'Stage A180 2.5-Way Floor Standing Tower',
                'sku': 'JBL-A180-FLR',
                'brand': 'JBL',
                'category': 'Bookshelf & Hi-Fi Speakers',
                'product_type': 'Floor Standing Speaker',
                'price': Decimal('499.99'),
                'discount_price': Decimal('429.99'),
                'stock': 12,
                'image_url': '/static/images/speaker-bookshelf.svg',
                'short': 'Dual 6.5" polycellulose woofer tower speaker with High Definition Imaging (HDI) waveguide.',
                'desc': 'Experience live concert energy in your room. The 1-inch aluminum dome tweeter with HDI waveguide creates pinpoint acoustic imaging across the entire listening area.',
                'specs': [
                    ('Design', '2.5-Way Floor Standing Loudspeaker'),
                    ('Woofers', 'Dual 6.5" Polycellulose Low-Frequency Woofers'),
                    ('Tweeter', '1" Aluminum Dome with HDI Waveguide'),
                    ('Max Amp Power', '225W Recommended'),
                ]
            },
            {
                'name': 'Soundcore Sub 100 Wireless Subwoofer',
                'sku': 'ANK-SUB100-WRL',
                'brand': 'Anker',
                'category': 'Bookshelf & Hi-Fi Speakers',
                'product_type': 'Wireless Subwoofer',
                'price': Decimal('199.99'),
                'discount_price': Decimal('179.99'),
                'stock': 25,
                'image_url': '/static/images/speaker-bookshelf.svg',
                'short': '100W down-firing wireless active subwoofer with dual-band 5.8GHz low latency transmission.',
                'desc': 'Seamlessly pair with any SoundSphere wireless ecosystem to add subterranean 28Hz bass impact without running unsightly audio cables.',
                'specs': [
                    ('Output Power', '100W RMS (200W Peak)'),
                    ('Driver Size', '8-inch Down-Firing High-Excursion'),
                    ('Wireless Tech', '5.8GHz Zero-Latency Wireless Link'),
                    ('Frequency Range', '28Hz – 180Hz'),
                ]
            },
            {
                'name': 'StudioSub 12 Powered Pro Subwoofer',
                'sku': 'YAM-SUB12-PRO',
                'brand': 'Yamaha',
                'category': 'Bookshelf & Hi-Fi Speakers',
                'product_type': 'Subwoofer',
                'price': Decimal('449.00'),
                'discount_price': Decimal('399.00'),
                'stock': 11,
                'image_url': '/static/images/speaker-bookshelf.svg',
                'short': '300W 12-inch active studio subwoofer featuring Twisted Flare Port technology.',
                'desc': 'Engineered to eliminate turbulent air noise. The Twisted Flare Port creates a smooth flow of air around the port edge, producing tight, clear, and realistic low frequencies.',
                'specs': [
                    ('Driver', '12-inch (30cm) Cone Woofer'),
                    ('Dynamic Power', '300W High Efficiency Amp'),
                    ('Port Technology', 'Twisted Flare Bass Reflex'),
                    ('Crossover Control', 'Continuous 40Hz – 140Hz Adjustment'),
                ]
            },

            # Gaming & Computer Audio
            {
                'name': 'G560 LIGHTSYNC RGB PC Gaming Speakers',
                'sku': 'LOG-G560-RGB',
                'brand': 'Logitech',
                'category': 'Gaming & Computer Audio',
                'product_type': 'RGB Gaming Speaker',
                'price': Decimal('249.99'),
                'discount_price': Decimal('219.99'),
                'stock': 32,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-gaming.svg',
                'short': '240W peak gaming audio system with dynamic screen-reactive LIGHTSYNC RGB lighting.',
                'desc': 'Immerse your senses with explosive game audio and lighting that automatically synchronizes with colors on your screen. Delivers DTS:X Ultra positional 3D sound.',
                'specs': [
                    ('Total Peak Power', '240W (120W RMS)'),
                    ('RGB Zones', '4 Customizable Reactive Light Zones'),
                    ('Positional Sound', 'DTS:X Ultra 3D Spatial Audio'),
                    ('Connections', 'USB, 3.5mm AUX, Bluetooth 4.1 with Easy-Switch'),
                ]
            },
            {
                'name': 'Katana Pro Multi-Core Gaming Soundbar',
                'sku': 'SNY-KATANA-PRO',
                'brand': 'Sony',
                'category': 'Gaming & Computer Audio',
                'product_type': 'Gaming Speaker',
                'price': Decimal('299.99'),
                'discount_price': Decimal('269.99'),
                'stock': 20,
                'image_url': '/static/images/speaker-gaming.svg',
                'short': 'Tri-amplified multi-core audio DSP soundbar designed for monitor under-shelf placement.',
                'desc': 'Fits discreetly under your gaming monitor. Features dedicated high-resolution 24-bit 96kHz DAC and Scout Mode to amplify footsteps and tactical cues.',
                'specs': [
                    ('Amplification', 'Tri-Amplified 5-Driver System (75W RMS)'),
                    ('DAC Quality', '24-bit/96kHz High-Resolution Audio'),
                    ('Gaming DSP', 'Scout Mode Footstep Enhancement'),
                    ('RGB Aurora', '16.8 Million Colors Underglow'),
                ]
            },
            {
                'name': 'Z207 Bluetooth Desktop Computer Speakers',
                'sku': 'LOG-Z207-BLK',
                'brand': 'Logitech',
                'category': 'Gaming & Computer Audio',
                'product_type': 'Computer Speaker',
                'price': Decimal('59.99'),
                'discount_price': Decimal('49.99'),
                'stock': 50,
                'image_url': '/static/images/speaker-gaming.svg',
                'short': 'Compact 10W stereo desktop speakers with seamless Easy-Switch between 2 Bluetooth devices.',
                'desc': 'Clean stereo sound with four drivers (two active and two passive radiators) to produce rich acoustics for video calls, podcasts, and workspace music.',
                'specs': [
                    ('Peak Power', '10W (5W RMS)'),
                    ('Easy-Switch', 'Pair up to 2 Bluetooth Devices simultaneously'),
                    ('Headphone Jack', 'Integrated 3.5mm Port on Front'),
                    ('Volume Knob', 'Convenient Front Dial'),
                ]
            },

            # Professional Audio
            {
                'name': 'EON715 15" Powered PA Loudspeaker',
                'sku': 'JBL-EON715-PA',
                'brand': 'JBL',
                'category': 'Professional Audio',
                'product_type': 'Portable PA Speaker',
                'price': Decimal('599.00'),
                'discount_price': Decimal('549.00'),
                'stock': 12,
                'is_featured': True,
                'image_url': '/static/images/speaker-propa.svg',
                'short': '1300W 15-inch portable PA speaker with advanced dbx DSP and Bluetooth 5.0 control.',
                'desc': 'Tour-grade acoustics for touring musicians, DJs, and live venues. Features dbx Automatic Feedback Suppression, 8-band output EQ, and ducking for speech priority.',
                'specs': [
                    ('System Power', '1300W Peak (650W Continuous)'),
                    ('Max SPL', '128 dB'),
                    ('Woofer Size', '15-inch Custom Ferrite Woofer'),
                    ('HF Driver', '2414H 1-inch Neodymium Compression Driver'),
                    ('DSP Engine', 'dbx AFS, Ducking, 100ms Delay Tuning'),
                ]
            },
            {
                'name': 'HS8 8" Active Studio Reference Monitor',
                'sku': 'YAM-HS8-MON',
                'brand': 'Yamaha',
                'category': 'Professional Audio',
                'product_type': 'Studio Monitor Speaker',
                'price': Decimal('399.99'),
                'discount_price': None,
                'stock': 15,
                'is_featured': True,
                'is_best_seller': True,
                'image_url': '/static/images/speaker-propa.svg',
                'short': 'Iconic white cone 120W bi-amplified nearfield reference studio monitor.',
                'desc': 'The world standard in studio mixing. Bi-amplified nearfield monitor with an 8-inch cone woofer and 1-inch dome tweeter delivering an uncompromisingly honest frequency response.',
                'specs': [
                    ('Amplifier', '120W Bi-Amp (75W LF + 45W HF)'),
                    ('Frequency Response', '38Hz – 30kHz'),
                    ('Controls', 'Room Control & High-Trim Response Switches'),
                    ('Inputs', 'XLR and TRS Phone Jack Balanced Inputs'),
                ]
            },
            {
                'name': 'ATH-M80 Active Nearfield Studio Monitor',
                'sku': 'ADT-M80-STUDIO',
                'brand': 'Audio-Technica',
                'category': 'Professional Audio',
                'product_type': 'Studio Monitor Speaker',
                'price': Decimal('329.99'),
                'discount_price': Decimal('299.99'),
                'stock': 18,
                'image_url': '/static/images/speaker-propa.svg',
                'short': 'Precision reference monitor with dual Kevlar cones and ribbon tweeter.',
                'desc': 'Tuned specifically for critical mastering, audio editing, and high-fidelity acoustic reproduction without harmonic distortion.',
                'specs': [
                    ('Power', '90W RMS Bi-Amplified'),
                    ('Woofer', '5.25-inch Woven Carbon Fiber'),
                    ('Tweeter', 'High-Velocity Folded Ribbon Tweeter'),
                    ('Cabinet', 'Acoustically Inert Aluminum Alloy Baffle'),
                ]
            },

            # Karaoke
            {
                'name': 'SoundBox Karaoke Stage Dual Mic System',
                'sku': 'JBL-STG-KARAOKE',
                'brand': 'JBL',
                'category': 'Karaoke',
                'product_type': 'Wireless Karaoke Speaker',
                'price': Decimal('349.99'),
                'discount_price': Decimal('299.99'),
                'stock': 22,
                'is_featured': True,
                'is_new_arrival': True,
                'image_url': '/static/images/speaker-karaoke.svg',
                'short': 'Dual wireless rechargeable UHF microphones with professional studio echo processor.',
                'desc': 'The ultimate home and party karaoke rig. Ships with two low-latency UHF wireless metal microphones, digital reverberation controls, and rhythm-synced LED illumination ring.',
                'specs': [
                    ('Output Power', '120W Peak Sound'),
                    ('Microphones', '2x UHF Rechargeable Metal Handheld Mics Included'),
                    ('Vocal Effects', 'Echo, Reverb, Vocal Cut / Background Isolator'),
                    ('Battery Life', '10 Hours Continuous Party Mode'),
                    ('Inputs', 'Bluetooth 5.3, USB Media, Optical, AUX'),
                ]
            },
            {
                'name': 'Mi Smart Wireless Party Vocalist',
                'sku': 'XIA-VOCAL-SMART',
                'brand': 'Xiaomi',
                'category': 'Karaoke',
                'product_type': 'Wireless Karaoke Speaker',
                'price': Decimal('149.99'),
                'discount_price': Decimal('129.99'),
                'stock': 30,
                'image_url': '/static/images/speaker-karaoke.svg',
                'short': 'Smart Bluetooth karaoke speaker with built-in voice effects and magnetic microphone dock.',
                'desc': 'Compact, stylish, and intelligent. Integrates with your favorite karaoke apps on iOS and Android with zero configuration.',
                'specs': [
                    ('Output Power', '60W RMS'),
                    ('Microphone', 'Includes 1 Wireless Cardioid Mic with Charging Dock'),
                    ('Smart Features', 'App-Controlled Audio Pitch & Sound Effects'),
                    ('Battery', '8 Hours Playtime'),
                ]
            },
        ]

        created_count = 0
        for p_data in products_catalog:
            cat = cat_map.get(p_data['category'])
            pt = type_map.get(p_data['product_type'])
            br = brand_map.get(p_data['brand'])

            if not (cat and pt and br):
                continue

            product, created = Product.objects.get_or_create(
                sku=p_data['sku'],
                defaults={
                    'name': p_data['name'],
                    'brand': br,
                    'category': cat,
                    'product_type': pt,
                    'short_description': p_data['short'],
                    'description': p_data['desc'],
                    'price': p_data['price'],
                    'discount_price': p_data.get('discount_price'),
                    'stock_quantity': p_data['stock'],
                    'low_stock_threshold': p_data.get('low_stock_threshold', 5),
                    'is_featured': p_data.get('is_featured', False),
                    'is_best_seller': p_data.get('is_best_seller', False),
                    'is_new_arrival': p_data.get('is_new_arrival', False),
                    'is_active': True,
                }
            )

            # Add primary product image
            ProductImage.objects.get_or_create(
                product=product,
                image_url=p_data.get('image_url', '/static/images/placeholder-speaker.svg'),
                defaults={
                    'alt_text': f"{product.name} High Definition Audio",
                    'is_primary': True,
                    'display_order': 0,
                }
            )

            # Add extra gallery image
            ProductImage.objects.get_or_create(
                product=product,
                image_url='/static/images/placeholder-speaker.svg',
                defaults={
                    'alt_text': f"{product.name} Studio Profile",
                    'is_primary': False,
                    'display_order': 1,
                }
            )

            # Add Specifications
            for order, (s_name, s_val) in enumerate(p_data.get('specs', [])):
                ProductSpecification.objects.get_or_create(
                    product=product,
                    specification_name=s_name,
                    defaults={
                        'specification_value': s_val,
                        'display_order': order
                    }
                )

            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Loaded {created_count} audio products with images and full specifications."))

        # 5. Coupons
        now = timezone.now()
        coupons_data = [
            {
                'code': 'WELCOME10',
                'type': Coupon.DiscountType.PERCENTAGE,
                'val': Decimal('10.00'),
                'min_subtotal': Decimal('50.00'),
                'max_discount': Decimal('50.00'),
                'usage_limit': 500,
            },
            {
                'code': 'SOUND20',
                'type': Coupon.DiscountType.PERCENTAGE,
                'val': Decimal('20.00'),
                'min_subtotal': Decimal('150.00'),
                'max_discount': Decimal('100.00'),
                'usage_limit': 200,
            },
            {
                'code': 'AUDIO50',
                'type': Coupon.DiscountType.FIXED,
                'val': Decimal('50.00'),
                'min_subtotal': Decimal('300.00'),
                'usage_limit': 100,
            },
        ]

        for c in coupons_data:
            Coupon.objects.get_or_create(
                code=c['code'],
                defaults={
                    'discount_type': c['type'],
                    'discount_value': c['val'],
                    'min_purchase_amount': c['min_subtotal'],
                    'max_discount_amount': c.get('max_discount'),
                    'usage_limit': c.get('usage_limit'),
                    'valid_from': now - timezone.timedelta(days=1),
                    'valid_to': now + timezone.timedelta(days=365),
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Loaded promotional discount coupons.'))

        # 6. Banners
        banners_data = [
            {
                'title': 'Acoustic Mastery Unleashed',
                'subtitle': 'Experience true spatial depth with Dolby Atmos soundbars and high-fidelity reference monitors.',
                'badge_text': 'NEW ARRIVALS 2026',
                'link_url': '/shop/?category=soundbars',
                'button_text': 'Explore Soundbars',
                'display_order': 1,
            },
            {
                'title': 'Power Your Outdoor Sound',
                'subtitle': 'Rugged IP67 waterproof and high-decibel party speakers engineered for any weather.',
                'badge_text': 'SUMMER AUDIO SALE',
                'link_url': '/shop/?category=bluetooth-speakers',
                'button_text': 'Shop Portable Audio',
                'display_order': 2,
            },
        ]

        for b in banners_data:
            Banner.objects.get_or_create(
                title=b['title'],
                defaults={
                    'subtitle': b['subtitle'],
                    'badge_text': b['badge_text'],
                    'link_url': b['link_url'],
                    'button_text': b['button_text'],
                    'display_order': b['display_order'],
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Loaded marketing banners.'))

        # 7. Sample Initial Reviews
        first_product = Product.objects.filter(is_featured=True).first()
        if first_product:
            Review.objects.get_or_create(
                user=demo_user,
                product=first_product,
                defaults={
                    'rating': 5,
                    'title': 'Astonishing sound clarity and rich bass!',
                    'comment': 'The acoustic dispersion and transient response on this speaker are unmatched. Fills my entire living room with crystal-clear audio.',
                    'is_verified_purchase': True,
                    'is_approved': True,
                }
            )
            first_product.update_rating()

        self.stdout.write(self.style.SUCCESS('--- SoundSphere Database Seeded Successfully! ---'))
