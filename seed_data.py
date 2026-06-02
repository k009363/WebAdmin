"""
Seed script — populates MongoDB with:
  • 1 admin user (if not exists)
  • 1 demo user
  • 1 demo domain  (localhost/demo → first template)
  • 13 business-category templates with realistic content
"""
import os, sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("MONGO_DB",  "dynamic_websites")

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

NOW = datetime.now(timezone.utc)

# ── helpers ───────────────────────────────────────────────────────────────────
def make_nav():
    return [
        {"label": "Home",         "page": "home"},
        {"label": "Services",     "page": "services"},
        {"label": "Achievements", "page": "achievements"},
        {"label": "About Us",     "page": "about"},
        {"label": "Blog",         "page": "blog"},
        {"label": "Pricing",      "page": "pricing"},
        {"label": "Contact",      "page": "contact"},
        {"label": "Feedback",     "page": "feedback"},
    ]

def make_social(fb="", tw="", ig="", li=""):
    return {"facebook": fb, "twitter": tw, "instagram": ig, "linkedin": li}

def make_theme(primary, secondary, accent="#f59e0b",
               bg="#ffffff", text="#1f2937", muted="#6b7280", dark="#0f172a"):
    return {
        "primaryColor": primary, "secondaryColor": secondary,
        "accentColor": accent,   "bgColor": bg,
        "textColor": text,       "mutedColor": muted,
        "darkBg": dark,
        "fontBody": "'Inter', sans-serif",
        "fontHeading": "'Poppins', sans-serif",
    }

def make_config(*, name, tagline, phone, email, address,
                theme, header_tmpl, footer_tmpl,
                home_title, home_sub, home_features, home_stats,
                services_title, services_items,
                about_story, about_mission, about_values, team,
                awards, milestones, stats,
                categories):
    sid = name.lower().replace(" ", "_").replace("&", "and")
    return {
        "siteId": sid,
        "logo": f"https://placehold.co/160x50/{theme['primaryColor'].lstrip('#')}/ffffff?text={name.replace(' ', '+')}",
        "theme": theme,
        "header": {
            "template": header_tmpl,
            "tagline": tagline,
            "phone": phone,
            "email": email,
            "navLinks": make_nav(),
        },
        "footer": {
            "template": footer_tmpl,
            "description": tagline,
            "address": address,
            "phone": phone,
            "email": email,
            "copyrightYear": 2024,
        },
        "socialLinks": make_social(
            fb=f"https://facebook.com/{sid}",
            ig=f"https://instagram.com/{sid}",
            li=f"https://linkedin.com/company/{sid}",
        ),
        "pages": {
            "home": {
                "template": 2, "titleTemplate": 3,
                "title": home_title, "subtitle": home_sub,
                "heroImage": f"https://placehold.co/1400x700/{theme['primaryColor'].lstrip('#')}/ffffff?text={name.replace(' ', '+')}",
                "features": home_features,
                "stats": home_stats,
                "testimonials": [
                    {"name": "Ravi Kumar",  "role": "Happy Customer",  "text": "Excellent service and very professional team.", "avatar": f"https://placehold.co/80x80/{theme['primaryColor'].lstrip('#')}/ffffff?text=RK"},
                    {"name": "Priya Singh", "role": "Loyal Client",    "text": "Highly recommended. Quality work every time!",  "avatar": f"https://placehold.co/80x80/{theme['secondaryColor'].lstrip('#')}/ffffff?text=PS"},
                    {"name": "Arjun Mehta","role": "Regular Customer", "text": "Outstanding experience. Will come back again.",  "avatar": f"https://placehold.co/80x80/{theme['primaryColor'].lstrip('#')}/ffffff?text=AM"},
                ],
            },
            "services": {
                "template": 3, "titleTemplate": 1,
                "title": services_title, "subtitle": "Professional solutions tailored for you",
                "heroImage": f"https://placehold.co/1400x400/{theme['secondaryColor'].lstrip('#')}/ffffff?text=Services",
                "items": services_items,
            },
            "achievements": {
                "template": 1, "titleTemplate": 4,
                "title": "Our Achievements", "subtitle": "Milestones we are proud of",
                "heroImage": f"https://placehold.co/1400x400/{theme['primaryColor'].lstrip('#')}/ffffff?text=Achievements",
                "awards": awards,
                "milestones": milestones,
                "stats": stats,
            },
            "about": {
                "template": 4, "titleTemplate": 2,
                "title": "About Us", "subtitle": f"The story behind {name}",
                "heroImage": f"https://placehold.co/1400x400/0f172a/ffffff?text=About+Us",
                "story": about_story,
                "mission": about_mission,
                "vision": f"To be the most trusted {name.lower()} in the region.",
                "values": about_values,
                "team": team,
            },
            "blog": {
                "template": 1, "titleTemplate": 7,
                "title": "Latest Blog Posts", "subtitle": "Stay updated with our insights",
                "heroImage": f"https://placehold.co/1400x400/{theme['primaryColor'].lstrip('#')}/ffffff?text=Blog",
                "enabled": True,
                "description": "Read our latest articles and insights",
            },
            "pricing": {
                "template": 1, "titleTemplate": 8,
                "title": "Transparent Pricing", "subtitle": "Choose the plan that fits your needs",
                "heroImage": f"https://placehold.co/1400x400/{theme['primaryColor'].lstrip('#')}/ffffff?text=Pricing",
                "enabled": True,
                "plans": [
                    {"name": "Starter", "price": "0", "period": "month", "description": "Perfect for getting started",
                     "features": ["Basic Features", "5 Projects", "Community Support"], "badge": "", "cta": "Get Started", "highlighted": False},
                    {"name": "Professional", "price": "29", "period": "month", "description": "For growing businesses",
                     "features": ["All Starter Features", "Unlimited Projects", "Priority Support", "Advanced Analytics"], "badge": "Popular", "cta": "Start Free Trial", "highlighted": True},
                    {"name": "Enterprise", "price": "99", "period": "month", "description": "For large teams",
                     "features": ["All Professional Features", "Dedicated Account Manager", "Custom Integrations", "SLA Support"], "badge": "", "cta": "Contact Sales", "highlighted": False},
                ],
            },
            "contact": {
                "template": 2, "titleTemplate": 5,
                "title": "Contact Us", "subtitle": "We are here to help you",
                "heroImage": f"https://placehold.co/1400x400/{theme['primaryColor'].lstrip('#')}/ffffff?text=Contact+Us",
                "address": address,
                "phone": phone,
                "email": email,
                "officeHours": "Mon–Sat: 9 AM – 7 PM",
                "offices": [{"city": "Main Branch", "address": address, "phone": phone}],
            },
            "feedback": {
                "template": 1, "titleTemplate": 6,
                "title": "Share Your Feedback", "subtitle": "Your opinion matters to us",
                "heroImage": f"https://placehold.co/1400x400/{theme['secondaryColor'].lstrip('#')}/ffffff?text=Feedback",
                "categories": categories,
            },
        },
    }

# ── Template definitions ───────────────────────────────────────────────────────
TEMPLATES = [

    # 1. Events & Celebrations
    make_config(
        name="Dream Events", tagline="Creating Memories That Last Forever",
        phone="+91 98765 43210", email="info@dreamevents.in",
        address="42 MG Road, Bangalore, KA 560001",
        theme=make_theme("#9c27b0", "#e91e63", "#ff9800", "#fdf4ff", "#1a0533", "#7b1fa2", "#1a0533"),
        header_tmpl=2, footer_tmpl=3,
        home_title="Your Dream Event, Our Passion",
        home_sub="From intimate gatherings to grand celebrations — we bring your vision to life.",
        home_features=[
            {"icon": "💍", "title": "Wedding Planning",      "desc": "End-to-end wedding management with flawless execution."},
            {"icon": "🎂", "title": "Birthday Parties",      "desc": "Unique themed parties for all ages."},
            {"icon": "👶", "title": "Baby Showers",          "desc": "Memorable celebrations for moms-to-be."},
            {"icon": "🎭", "title": "Decoration Services",   "desc": "Stunning décor that transforms any venue."},
            {"icon": "📷", "title": "Photography",           "desc": "Professional photography & videography packages."},
            {"icon": "🎵", "title": "Sound & Lighting",      "desc": "State-of-the-art AV setup for every event."},
        ],
        home_stats=[{"value": "500+", "label": "Events Managed"}, {"value": "98%", "label": "Happy Clients"}, {"value": "10+", "label": "Years Experience"}, {"value": "50+", "label": "Expert Team"}],
        services_title="Our Event Services",
        services_items=[
            {"icon": "💍", "title": "Wedding Planning",    "desc": "Complete wedding management from venue to honeymoon.", "image": "https://placehold.co/400x250/9c27b0/ffffff?text=Wedding", "features": ["Venue Selection", "Catering", "Décor & Florals"]},
            {"icon": "🎂", "title": "Birthday Parties",    "desc": "Custom themed birthday parties for kids and adults.",   "image": "https://placehold.co/400x250/e91e63/ffffff?text=Birthday", "features": ["Theme Design", "Entertainment", "Catering"]},
            {"icon": "👶", "title": "Baby Shower",         "desc": "Beautiful baby shower events full of love.",            "image": "https://placehold.co/400x250/ff9800/ffffff?text=Baby+Shower", "features": ["Décor", "Games", "Gift Registry"]},
            {"icon": "🏛️", "title": "Naming Ceremony",    "desc": "Traditional and modern naming ceremonies.",             "image": "https://placehold.co/400x250/9c27b0/ffffff?text=Naming", "features": ["Traditional Setup", "Priest Arrangement", "Catering"]},
            {"icon": "🎭", "title": "Decoration",          "desc": "Floral, balloon & stage decorations.",                  "image": "https://placehold.co/400x250/e91e63/ffffff?text=Decoration", "features": ["Floral Décor", "Balloon Art", "Stage Setup"]},
            {"icon": "📷", "title": "Photography",         "desc": "HD photos & cinematic videos.",                         "image": "https://placehold.co/400x250/9c27b0/ffffff?text=Photography", "features": ["HD Camera", "Drone Shots", "Photo Albums"]},
        ],
        about_story="Dream Events was founded in 2014 with a simple belief — every celebration deserves to be extraordinary. We have made over 500 events magical across South India.",
        about_mission="To craft personalized celebrations that create lifetime memories for every family.",
        about_values=[
            {"icon": "✨", "title": "Creativity",    "desc": "Every event is unique, never a template."},
            {"icon": "🤝", "title": "Trust",         "desc": "Transparent pricing, no hidden costs."},
            {"icon": "⏰", "title": "Punctuality",   "desc": "We deliver on time, every time."},
            {"icon": "💝", "title": "Passion",       "desc": "We love what we do and it shows."},
        ],
        team=[
            {"name": "Aisha Nair",   "role": "Creative Director",  "avatar": "https://placehold.co/200x200/9c27b0/ffffff?text=AN"},
            {"name": "Raj Sharma",   "role": "Event Coordinator",  "avatar": "https://placehold.co/200x200/e91e63/ffffff?text=RS"},
            {"name": "Meena Iyer",   "role": "Décor Specialist",   "avatar": "https://placehold.co/200x200/9c27b0/ffffff?text=MI"},
            {"name": "Vikram Patel", "role": "Photography Head",   "avatar": "https://placehold.co/200x200/e91e63/ffffff?text=VP"},
        ],
        awards=[{"year": "2024", "title": "Best Event Company", "org": "Bangalore Business Awards", "icon": "🏆"}, {"year": "2023", "title": "Top Wedding Planner", "org": "WeddingBuzz India", "icon": "💍"}],
        milestones=[{"year": "2014", "title": "Founded", "desc": "Started with 2 coordinators."}, {"year": "2018", "title": "100th Wedding", "desc": "Celebrated 100 weddings milestone."}, {"year": "2022", "title": "500 Events", "desc": "Completed 500+ events across India."}],
        stats=[{"value": "500+", "label": "Events", "icon": "🎉"}, {"value": "98%", "label": "Satisfaction", "icon": "😊"}, {"value": "10+", "label": "Years", "icon": "📅"}, {"value": "50K+", "label": "Guests Served", "icon": "👥"}],
        categories=["Event Planning", "Decoration", "Catering", "Photography", "Overall Experience"],
    ),

    # 2. Retail Stores
    make_config(
        name="FreshMart Supermarket", tagline="Fresh. Quality. Value.",
        phone="+91 97654 32109", email="freshmart@gmail.com",
        address="12 Anna Nagar, Chennai, TN 600040",
        theme=make_theme("#2e7d32", "#f57c00", "#ffb300", "#f1f8e9", "#1b5e20", "#558b2f", "#1b5e20"),
        header_tmpl=1, footer_tmpl=2,
        home_title="Shop Fresh, Live Well",
        home_sub="Your neighbourhood supermarket with the freshest produce, daily essentials and great deals.",
        home_features=[
            {"icon": "🥦", "title": "Fresh Vegetables",  "desc": "Farm-to-shelf vegetables sourced daily."},
            {"icon": "🥛", "title": "Dairy & Eggs",       "desc": "Premium dairy products and farm-fresh eggs."},
            {"icon": "🍞", "title": "Bakery Items",       "desc": "Freshly baked bread, cakes & pastries."},
            {"icon": "🧴", "title": "Personal Care",      "desc": "All top personal care and hygiene brands."},
            {"icon": "🏠", "title": "Household Goods",   "desc": "Complete range of home essentials."},
            {"icon": "🚚", "title": "Home Delivery",      "desc": "Fast delivery within 2 hours."},
        ],
        home_stats=[{"value": "5000+", "label": "Products"}, {"value": "500+", "label": "Daily Customers"}, {"value": "15+", "label": "Years Serving"}, {"value": "3", "label": "Store Locations"}],
        services_title="What We Offer",
        services_items=[
            {"icon": "🥦", "title": "Fresh Produce",    "desc": "Daily fresh vegetables and fruits.",  "image": "https://placehold.co/400x250/2e7d32/ffffff?text=Fresh+Produce", "features": ["Daily Delivery", "100% Fresh", "Seasonal Picks"]},
            {"icon": "🥩", "title": "Meat & Seafood",   "desc": "Fresh meat, poultry and seafood.",    "image": "https://placehold.co/400x250/f57c00/ffffff?text=Meat", "features": ["Halal Certified", "Daily Fresh", "Custom Cuts"]},
            {"icon": "🧴", "title": "FMCG Products",    "desc": "All daily use consumer goods.",       "image": "https://placehold.co/400x250/2e7d32/ffffff?text=FMCG", "features": ["1000+ Brands", "Best Prices", "Bulk Orders"]},
            {"icon": "🚚", "title": "Home Delivery",    "desc": "Order online, get at your door.",     "image": "https://placehold.co/400x250/f57c00/ffffff?text=Delivery", "features": ["2-Hour Delivery", "Online Ordering", "No Min Order"]},
        ],
        about_story="FreshMart started in 2009 as a small grocery store in Anna Nagar. Today we run 3 outlets serving over 500 families daily with quality products at honest prices.",
        about_mission="To provide the freshest products at the fairest prices to every household in our community.",
        about_values=[
            {"icon": "🌱", "title": "Freshness",    "desc": "Only the freshest products on our shelves."},
            {"icon": "💰", "title": "Fair Price",   "desc": "Competitive pricing every single day."},
            {"icon": "🤝", "title": "Community",    "desc": "Rooted in and giving back to the community."},
            {"icon": "♻️", "title": "Eco-Friendly", "desc": "Reducing plastic, promoting sustainability."},
        ],
        team=[
            {"name": "Suresh Babu",  "role": "Owner & Manager",     "avatar": "https://placehold.co/200x200/2e7d32/ffffff?text=SB"},
            {"name": "Kavitha Raj",  "role": "Store Manager",        "avatar": "https://placehold.co/200x200/f57c00/ffffff?text=KR"},
        ],
        awards=[{"year": "2023", "title": "Best Local Supermarket", "org": "Chennai Retail Awards", "icon": "🏆"}],
        milestones=[{"year": "2009", "title": "Founded", "desc": "Opened first store in Anna Nagar."}, {"year": "2015", "title": "3rd Store", "desc": "Expanded to 3 locations."}, {"year": "2022", "title": "Online Launch", "desc": "Started home delivery service."}],
        stats=[{"value": "5000+", "label": "Products", "icon": "📦"}, {"value": "500+", "label": "Daily Customers", "icon": "👥"}, {"value": "15+", "label": "Years", "icon": "📅"}, {"value": "3", "label": "Stores", "icon": "🏪"}],
        categories=["Product Quality", "Customer Service", "Pricing", "Cleanliness", "Overall"],
    ),

    # 3. Printing & Digital Services
    make_config(
        name="DigiPrint Solutions", tagline="Print It. Brand It. Deliver It.",
        phone="+91 96543 21098", email="digiprint@gmail.com",
        address="7 Commercial Street, Hyderabad, TS 500001",
        theme=make_theme("#1565c0", "#00acc1", "#ff7043", "#e3f2fd", "#0d1b3e", "#1976d2", "#0d1b3e"),
        header_tmpl=2, footer_tmpl=4,
        home_title="Professional Printing & Digital Services",
        home_sub="High-quality printing, DTP, flex boards and digital services at affordable prices.",
        home_features=[
            {"icon": "🖨️", "title": "Printing Services",  "desc": "Digital, offset and large-format printing."},
            {"icon": "🎨", "title": "DTP & Design",        "desc": "Professional desktop publishing and design."},
            {"icon": "📐", "title": "Flex Printing",       "desc": "Eye-catching flex and banner printing."},
            {"icon": "🌐", "title": "Internet Services",   "desc": "High-speed internet and DTP services."},
            {"icon": "📚", "title": "Lamination & Binding","desc": "ID card, document lamination and binding."},
            {"icon": "📸", "title": "Photo Studio",        "desc": "Passport, ID and professional photos."},
        ],
        home_stats=[{"value": "10K+", "label": "Orders Delivered"}, {"value": "500+", "label": "Happy Clients"}, {"value": "8+", "label": "Years in Business"}, {"value": "24hr", "label": "Turnaround"}],
        services_title="Printing & Digital Services",
        services_items=[
            {"icon": "🖨️", "title": "Digital Printing",  "desc": "High resolution digital prints on any paper.", "image": "https://placehold.co/400x250/1565c0/ffffff?text=Digital+Print", "features": ["A4 to A0 Size", "Same Day", "Color & B&W"]},
            {"icon": "📐", "title": "Flex Printing",     "desc": "Outdoor flex boards and banners.",             "image": "https://placehold.co/400x250/00acc1/ffffff?text=Flex+Print", "features": ["Any Size", "UV Resistant", "Fast Delivery"]},
            {"icon": "🎨", "title": "DTP Services",      "desc": "Brochures, visiting cards, posters.",          "image": "https://placehold.co/400x250/ff7043/ffffff?text=DTP", "features": ["All Formats", "Design Help", "Quick TAT"]},
            {"icon": "📸", "title": "Photo Services",    "desc": "Passport photos, enlargements, prints.",       "image": "https://placehold.co/400x250/1565c0/ffffff?text=Photos", "features": ["Instant Prints", "All Sizes", "Digital Copy"]},
        ],
        about_story="DigiPrint Solutions has been serving businesses and individuals in Hyderabad since 2016 with reliable, high-quality printing and digital services at competitive rates.",
        about_mission="To be the go-to printing and digital services partner for every business and individual in the city.",
        about_values=[
            {"icon": "⚡", "title": "Speed",      "desc": "Quick turnaround without compromising quality."},
            {"icon": "🎯", "title": "Precision",  "desc": "Every print is sharp, accurate and vibrant."},
            {"icon": "💰", "title": "Affordable", "desc": "Best prices with no compromise on quality."},
            {"icon": "🔒", "title": "Reliable",   "desc": "Consistent quality you can count on."},
        ],
        team=[
            {"name": "Ramesh Rao",  "role": "Owner",            "avatar": "https://placehold.co/200x200/1565c0/ffffff?text=RR"},
            {"name": "Sita Devi",   "role": "Design Head",      "avatar": "https://placehold.co/200x200/00acc1/ffffff?text=SD"},
        ],
        awards=[{"year": "2023", "title": "Best Print Shop", "org": "Hyderabad Business Hub", "icon": "🏆"}],
        milestones=[{"year": "2016", "title": "Founded", "desc": "Started with 2 printers."}, {"year": "2020", "title": "Digital Expansion", "desc": "Added internet cafe services."}, {"year": "2023", "title": "10K Orders", "desc": "Delivered 10,000+ orders."}],
        stats=[{"value": "10K+", "label": "Orders", "icon": "🖨️"}, {"value": "500+", "label": "Clients", "icon": "👥"}, {"value": "8+", "label": "Years", "icon": "📅"}, {"value": "24hr", "label": "Delivery", "icon": "⚡"}],
        categories=["Print Quality", "Design Help", "Turnaround Time", "Pricing", "Overall"],
    ),

    # 4. Food & Beverage
    make_config(
        name="Spice Garden Restaurant", tagline="Authentic Flavours, Warm Hospitality",
        phone="+91 95432 10987", email="spicegarden@gmail.com",
        address="23 Park Road, Coimbatore, TN 641001",
        theme=make_theme("#bf360c", "#e65100", "#ffc107", "#fff8f0", "#3e1a00", "#d84315", "#1a0800"),
        header_tmpl=3, footer_tmpl=1,
        home_title="Taste the Authentic Flavours of India",
        home_sub="Fresh ingredients, traditional recipes, cooked with love — every meal is an experience.",
        home_features=[
            {"icon": "🍛", "title": "South Indian",     "desc": "Authentic dosas, idli, sambar and biryani."},
            {"icon": "🍜", "title": "North Indian",     "desc": "Tandoori, curries, dal makhani and more."},
            {"icon": "🎂", "title": "Bakery Items",     "desc": "Fresh cakes, pastries and breads daily."},
            {"icon": "🚗", "title": "Home Delivery",    "desc": "Hot meals delivered to your doorstep."},
            {"icon": "🏢", "title": "Catering",         "desc": "Office, wedding and event catering."},
            {"icon": "☕", "title": "Cafe Corner",       "desc": "Refreshing beverages and quick bites."},
        ],
        home_stats=[{"value": "200+", "label": "Menu Items"}, {"value": "1000+", "label": "Daily Orders"}, {"value": "12+", "label": "Years Serving"}, {"value": "4.8⭐", "label": "Google Rating"}],
        services_title="Our Menu & Services",
        services_items=[
            {"icon": "🍛", "title": "Restaurant Dining", "desc": "Dine-in with family and friends.",          "image": "https://placehold.co/400x250/bf360c/ffffff?text=Dining", "features": ["200+ Dishes", "AC Seating", "Family Packs"]},
            {"icon": "🚗", "title": "Home Delivery",     "desc": "Order hot food delivered to your door.",    "image": "https://placehold.co/400x250/e65100/ffffff?text=Delivery", "features": ["Swiggy & Zomato", "Direct Orders", "30 Min Delivery"]},
            {"icon": "🏢", "title": "Catering Services", "desc": "Corporate and event catering packages.",    "image": "https://placehold.co/400x250/ffc107/1a0800?text=Catering", "features": ["Min 50 Persons", "Custom Menu", "On-site Setup"]},
            {"icon": "🎂", "title": "Bakery & Sweets",   "desc": "Custom cakes and festive sweet boxes.",     "image": "https://placehold.co/400x250/bf360c/ffffff?text=Bakery", "features": ["Custom Cakes", "Gift Boxes", "Bulk Orders"]},
        ],
        about_story="Spice Garden was started in 2012 by Chef Murugesan with the goal of serving authentic Tamil Nadu cuisine. Today we are a beloved restaurant serving 1000+ customers daily.",
        about_mission="To serve wholesome, delicious food made with the freshest ingredients at prices everyone can afford.",
        about_values=[
            {"icon": "🌿", "title": "Fresh",    "desc": "Fresh ingredients sourced daily."},
            {"icon": "❤️",  "title": "Passion", "desc": "Cooking with love in every dish."},
            {"icon": "🧹", "title": "Hygiene",  "desc": "Highest standards of kitchen hygiene."},
            {"icon": "😊", "title": "Service",  "desc": "Warm hospitality for every guest."},
        ],
        team=[
            {"name": "Chef Murugesan", "role": "Head Chef & Owner",  "avatar": "https://placehold.co/200x200/bf360c/ffffff?text=CM"},
            {"name": "Lalitha Devi",   "role": "Restaurant Manager", "avatar": "https://placehold.co/200x200/e65100/ffffff?text=LD"},
        ],
        awards=[{"year": "2024", "title": "Best Family Restaurant", "org": "Coimbatore Food Awards", "icon": "🏆"}, {"year": "2022", "title": "4.8 Star Rating", "org": "Google Reviews", "icon": "⭐"}],
        milestones=[{"year": "2012", "title": "Founded", "desc": "Opened first restaurant."}, {"year": "2017", "title": "Catering Launch", "desc": "Started corporate catering."}, {"year": "2021", "title": "Online Orders", "desc": "Joined Swiggy & Zomato."}],
        stats=[{"value": "200+", "label": "Menu Items", "icon": "🍽️"}, {"value": "1K+", "label": "Daily Orders", "icon": "📦"}, {"value": "12+", "label": "Years", "icon": "📅"}, {"value": "4.8⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Food Quality", "Service", "Cleanliness", "Value for Money", "Overall"],
    ),

    # 5. Beauty & Wellness
    make_config(
        name="Glamour Beauty Salon", tagline="Look Good. Feel Great. Be You.",
        phone="+91 94321 09876", email="glamoursalon@gmail.com",
        address="15 Brigade Road, Bangalore, KA 560025",
        theme=make_theme("#c2185b", "#e91e63", "#ff80ab", "#fce4ec", "#880e4f", "#ad1457", "#880e4f"),
        header_tmpl=1, footer_tmpl=3,
        home_title="Your Beauty Destination in Bangalore",
        home_sub="Expert stylists, premium products and a relaxing atmosphere for a complete beauty experience.",
        home_features=[
            {"icon": "✂️", "title": "Hair Services",    "desc": "Cut, colour, styling and treatments."},
            {"icon": "💅", "title": "Nail Art",          "desc": "Manicure, pedicure and nail extensions."},
            {"icon": "🧖", "title": "Facial & Spa",      "desc": "Luxury facials and rejuvenating spa treatments."},
            {"icon": "💇", "title": "Bridal Makeup",     "desc": "Complete bridal packages for your big day."},
            {"icon": "🪷", "title": "Waxing & Threading","desc": "Smooth skin care and eyebrow styling."},
            {"icon": "💆", "title": "Massage Therapy",   "desc": "Relaxing body massages and stress relief."},
        ],
        home_stats=[{"value": "5000+", "label": "Happy Clients"}, {"value": "15+", "label": "Expert Stylists"}, {"value": "8+", "label": "Years Experience"}, {"value": "4.9⭐", "label": "Rating"}],
        services_title="Beauty & Wellness Services",
        services_items=[
            {"icon": "✂️", "title": "Hair Services",  "desc": "All hair cut, colour and treatment options.",   "image": "https://placehold.co/400x250/c2185b/ffffff?text=Hair", "features": ["All Hair Types", "Premium Products", "Expert Stylists"]},
            {"icon": "💅", "title": "Nail Services",  "desc": "Nail art, gel, acrylic and spa manicure.",      "image": "https://placehold.co/400x250/e91e63/ffffff?text=Nails", "features": ["Nail Art", "Gel Polish", "Extensions"]},
            {"icon": "💇", "title": "Bridal Package", "desc": "Complete bridal makeup and hair for your day.", "image": "https://placehold.co/400x250/c2185b/ffffff?text=Bridal", "features": ["Trial Session", "HD Makeup", "Hair Styling"]},
            {"icon": "🧖", "title": "Spa & Facial",   "desc": "Luxury facials and full body spa sessions.",    "image": "https://placehold.co/400x250/e91e63/ffffff?text=Spa", "features": ["International Products", "Trained Therapists", "Packages Available"]},
        ],
        about_story="Glamour Beauty Salon was founded in 2016 with a vision to offer world-class beauty services to every woman in Bangalore at affordable prices.",
        about_mission="To empower every woman to look and feel her absolute best with expert care and premium services.",
        about_values=[
            {"icon": "💎", "title": "Excellence",   "desc": "Only the best techniques and products."},
            {"icon": "🌸", "title": "Hygiene",      "desc": "Strict sanitization after every service."},
            {"icon": "💝", "title": "Care",         "desc": "Personalized attention for every client."},
            {"icon": "🎓", "title": "Expertise",    "desc": "Continuously trained and certified stylists."},
        ],
        team=[
            {"name": "Deepa Nair",    "role": "Senior Stylist",  "avatar": "https://placehold.co/200x200/c2185b/ffffff?text=DN"},
            {"name": "Pooja Sharma",  "role": "Makeup Artist",   "avatar": "https://placehold.co/200x200/e91e63/ffffff?text=PS"},
            {"name": "Rekha Menon",   "role": "Spa Therapist",   "avatar": "https://placehold.co/200x200/c2185b/ffffff?text=RM"},
            {"name": "Anita Verma",   "role": "Nail Technician", "avatar": "https://placehold.co/200x200/e91e63/ffffff?text=AV"},
        ],
        awards=[{"year": "2024", "title": "Best Salon Bangalore", "org": "Beauty Industry Awards", "icon": "💄"}],
        milestones=[{"year": "2016", "title": "Founded", "desc": "Opened with 5 stylists."}, {"year": "2019", "title": "Expanded", "desc": "Added spa and nail extension services."}, {"year": "2023", "title": "5000 Clients", "desc": "Reached 5000+ loyal clients."}],
        stats=[{"value": "5K+", "label": "Happy Clients", "icon": "😊"}, {"value": "15+", "label": "Stylists", "icon": "✂️"}, {"value": "8+", "label": "Years", "icon": "📅"}, {"value": "4.9⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Service Quality", "Stylist Expertise", "Hygiene", "Pricing", "Overall"],
    ),

    # 6. Education & Training
    make_config(
        name="Bright Future Academy", tagline="Education That Inspires Excellence",
        phone="+91 93210 98765", email="brightfuture@academy.in",
        address="88 Education Lane, Pune, MH 411001",
        theme=make_theme("#1565c0", "#0097a7", "#ffc107", "#e8f4fd", "#003580", "#1976d2", "#003580"),
        header_tmpl=2, footer_tmpl=2,
        home_title="Empowering Futures Through Quality Education",
        home_sub="Expert tutors, proven methods and a supportive learning environment for every student.",
        home_features=[
            {"icon": "📚", "title": "School Coaching",    "desc": "Classes 1–12 all subjects, CBSE & State board."},
            {"icon": "🎓", "title": "Competitive Exams",  "desc": "JEE, NEET, UPSC, Banking and SSC coaching."},
            {"icon": "💻", "title": "Computer Training",  "desc": "Tally, MS Office, Web Design, Programming."},
            {"icon": "🗣️", "title": "Spoken English",    "desc": "Improve communication and confidence."},
            {"icon": "🎨", "title": "Skill Development",  "desc": "Drawing, craft, music and personality development."},
            {"icon": "📝", "title": "Test Series",        "desc": "Regular mock tests and performance tracking."},
        ],
        home_stats=[{"value": "2000+", "label": "Students Enrolled"}, {"value": "95%", "label": "Pass Rate"}, {"value": "50+", "label": "Expert Faculty"}, {"value": "10+", "label": "Years Excellence"}],
        services_title="Courses & Programs",
        services_items=[
            {"icon": "📚", "title": "School Tuition",     "desc": "All subjects for classes 1 to 12.",             "image": "https://placehold.co/400x250/1565c0/ffffff?text=School", "features": ["All Subjects", "CBSE & State", "Doubt Sessions"]},
            {"icon": "🎓", "title": "Competitive Exams",  "desc": "JEE, NEET, UPSC and banking coaching.",         "image": "https://placehold.co/400x250/0097a7/ffffff?text=Competitive", "features": ["Expert Faculty", "Study Material", "Mock Tests"]},
            {"icon": "💻", "title": "Computer Courses",   "desc": "Practical computer and programming courses.",    "image": "https://placehold.co/400x250/1565c0/ffffff?text=Computer", "features": ["MS Office", "Tally", "Python/Web"]},
            {"icon": "🗣️", "title": "Spoken English",    "desc": "Communication skills and spoken English.",       "image": "https://placehold.co/400x250/ffc107/003580?text=English", "features": ["Group Classes", "Individual Sessions", "Certification"]},
        ],
        about_story="Bright Future Academy was established in 2014 by a team of experienced educators with the mission to make quality education accessible to every student in Pune.",
        about_mission="To provide affordable, high-quality education that builds knowledge, skills and confidence for a successful future.",
        about_values=[
            {"icon": "📖", "title": "Knowledge",    "desc": "In-depth teaching with conceptual clarity."},
            {"icon": "🌟", "title": "Excellence",   "desc": "Setting high standards for every student."},
            {"icon": "🤝", "title": "Support",      "desc": "Personal attention for every learner."},
            {"icon": "💡", "title": "Innovation",   "desc": "Modern teaching methods and technology."},
        ],
        team=[
            {"name": "Dr. Amit Shah",    "role": "Director & Founder",  "avatar": "https://placehold.co/200x200/1565c0/ffffff?text=AS"},
            {"name": "Mrs. Rekha Patil", "role": "Senior Faculty",       "avatar": "https://placehold.co/200x200/0097a7/ffffff?text=RP"},
            {"name": "Mr. Arun Joshi",   "role": "Science Coordinator",  "avatar": "https://placehold.co/200x200/1565c0/ffffff?text=AJ"},
            {"name": "Ms. Nisha Gupta",  "role": "English Faculty",      "avatar": "https://placehold.co/200x200/0097a7/ffffff?text=NG"},
        ],
        awards=[{"year": "2024", "title": "Best Coaching Institute", "org": "Pune Education Awards", "icon": "🏆"}, {"year": "2023", "title": "95% Board Results", "desc": "Record board exam results", "org": "Self Achievement", "icon": "🎓"}],
        milestones=[{"year": "2014", "title": "Founded", "desc": "Started with 50 students."}, {"year": "2018", "title": "500 Students", "desc": "Reached 500 enrolled students."}, {"year": "2023", "title": "2000 Students", "desc": "Growing family of 2000+ students."}],
        stats=[{"value": "2K+", "label": "Students", "icon": "👩‍🎓"}, {"value": "95%", "label": "Pass Rate", "icon": "🎯"}, {"value": "50+", "label": "Faculty", "icon": "👨‍🏫"}, {"value": "10+", "label": "Years", "icon": "📅"}],
        categories=["Teaching Quality", "Study Material", "Faculty Expertise", "Infrastructure", "Overall"],
    ),

    # 7. IT & Professional Services
    make_config(
        name="TechVision IT Solutions", tagline="Transforming Businesses Through Technology",
        phone="+91 92109 87654", email="info@techvision.in",
        address="301 Cyber Towers, Hyderabad, TS 500081",
        theme=make_theme("#1a237e", "#0288d1", "#00e5ff", "#e8eaf6", "#0d1b3e", "#283593", "#060d2e"),
        header_tmpl=4, footer_tmpl=2,
        home_title="Building Digital Solutions That Drive Growth",
        home_sub="Expert IT services, custom software, web design and digital marketing for businesses of all sizes.",
        home_features=[
            {"icon": "💻", "title": "Software Development", "desc": "Custom web and desktop application development."},
            {"icon": "🌐", "title": "Web Design",           "desc": "Responsive, modern websites and landing pages."},
            {"icon": "📱", "title": "Mobile Apps",          "desc": "iOS and Android app development."},
            {"icon": "📊", "title": "Digital Marketing",    "desc": "SEO, social media and paid ad campaigns."},
            {"icon": "☁️", "title": "Cloud Services",       "desc": "Cloud hosting, migration and management."},
            {"icon": "🔒", "title": "Cybersecurity",        "desc": "Protect your business with robust security."},
        ],
        home_stats=[{"value": "300+", "label": "Projects Delivered"}, {"value": "150+", "label": "Happy Clients"}, {"value": "8+", "label": "Years Experience"}, {"value": "40+", "label": "Expert Team"}],
        services_title="IT & Technology Services",
        services_items=[
            {"icon": "💻", "title": "Software Dev",     "desc": "Custom business software solutions.",        "image": "https://placehold.co/400x250/1a237e/ffffff?text=Software", "features": ["Web Apps", "ERP Systems", "API Development"]},
            {"icon": "🌐", "title": "Web Design",       "desc": "Professional website design and development.", "image": "https://placehold.co/400x250/0288d1/ffffff?text=Web+Design", "features": ["Responsive Design", "CMS", "E-commerce"]},
            {"icon": "📊", "title": "Digital Marketing","desc": "Data-driven marketing for business growth.",    "image": "https://placehold.co/400x250/1a237e/ffffff?text=Marketing", "features": ["SEO", "Google Ads", "Social Media"]},
            {"icon": "☁️", "title": "Cloud Solutions",  "desc": "AWS, Azure, GCP hosting and migration.",      "image": "https://placehold.co/400x250/0288d1/ffffff?text=Cloud", "features": ["AWS/Azure", "DevOps", "24/7 Support"]},
        ],
        about_story="TechVision was founded in 2016 by a team of experienced software engineers with the mission to democratize technology for small and medium businesses across India.",
        about_mission="To empower businesses with technology solutions that are affordable, reliable and impactful.",
        about_values=[
            {"icon": "🚀", "title": "Innovation",    "desc": "Always adopting the latest technologies."},
            {"icon": "⭐", "title": "Quality",       "desc": "Delivering excellence in every project."},
            {"icon": "🔒", "title": "Security",      "desc": "Building secure and resilient systems."},
            {"icon": "🤝", "title": "Partnership",   "desc": "Long-term relationships, not transactions."},
        ],
        team=[
            {"name": "Kiran Reddy",  "role": "CEO & Founder",        "avatar": "https://placehold.co/200x200/1a237e/ffffff?text=KR"},
            {"name": "Priya Nair",   "role": "CTO",                  "avatar": "https://placehold.co/200x200/0288d1/ffffff?text=PN"},
            {"name": "Rahul Verma",  "role": "Lead Developer",        "avatar": "https://placehold.co/200x200/1a237e/ffffff?text=RV"},
            {"name": "Sneha Rao",    "role": "Digital Marketing Head","avatar": "https://placehold.co/200x200/0288d1/ffffff?text=SR"},
        ],
        awards=[{"year": "2024", "title": "Best IT Company", "org": "Hyderabad Tech Awards", "icon": "🏆"}, {"year": "2023", "title": "Top Digital Agency", "org": "Digital India Summit", "icon": "🌐"}],
        milestones=[{"year": "2016", "title": "Founded", "desc": "Started with 5 developers."}, {"year": "2019", "title": "100 Projects", "desc": "Delivered 100th project."}, {"year": "2023", "title": "300+ Clients", "desc": "Expanded to 40+ member team."}],
        stats=[{"value": "300+", "label": "Projects", "icon": "💻"}, {"value": "150+", "label": "Clients", "icon": "🤝"}, {"value": "40+", "label": "Team", "icon": "👥"}, {"value": "8+", "label": "Years", "icon": "📅"}],
        categories=["Technical Quality", "Communication", "Delivery Time", "Support", "Overall"],
    ),

    # 8. Home & Local Services
    make_config(
        name="QuickFix Home Services", tagline="Your Trusted Home Service Partner",
        phone="+91 91098 76543", email="quickfix@homeservices.in",
        address="56 Gandhi Nagar, Jaipur, RJ 302001",
        theme=make_theme("#2e7d32", "#558b2f", "#ff8f00", "#f1f8e9", "#1b5e20", "#388e3c", "#1b4020"),
        header_tmpl=1, footer_tmpl=4,
        home_title="Reliable Home Services at Your Doorstep",
        home_sub="Certified professionals for electrical, plumbing, cleaning, interior and all home maintenance needs.",
        home_features=[
            {"icon": "⚡", "title": "Electrical Services", "desc": "Wiring, repairs and installations by certified electricians."},
            {"icon": "🔧", "title": "Plumbing",           "desc": "Pipe repair, installation and maintenance."},
            {"icon": "🧹", "title": "Cleaning Services",  "desc": "Deep cleaning, pest control and housekeeping."},
            {"icon": "🏠", "title": "Interior Design",    "desc": "Modern interior design and renovation."},
            {"icon": "🛠️", "title": "Home Maintenance",   "desc": "All general maintenance and repair work."},
            {"icon": "❄️", "title": "AC Services",         "desc": "AC installation, repair and service."},
        ],
        home_stats=[{"value": "10K+", "label": "Services Done"}, {"value": "5000+", "label": "Happy Homes"}, {"value": "7+", "label": "Years Serving"}, {"value": "4.7⭐", "label": "Average Rating"}],
        services_title="Home & Maintenance Services",
        services_items=[
            {"icon": "⚡", "title": "Electrical",  "desc": "All electrical work by certified engineers.",  "image": "https://placehold.co/400x250/2e7d32/ffffff?text=Electrical", "features": ["24/7 Emergency", "Certified Staff", "Guaranteed Work"]},
            {"icon": "🔧", "title": "Plumbing",    "desc": "Leak fix, pipe work and bathroom fitting.",    "image": "https://placehold.co/400x250/558b2f/ffffff?text=Plumbing", "features": ["Same Day Service", "All Brands", "Free Estimate"]},
            {"icon": "🧹", "title": "Cleaning",    "desc": "Home, office and commercial deep cleaning.",   "image": "https://placehold.co/400x250/ff8f00/ffffff?text=Cleaning", "features": ["Eco Products", "Trained Staff", "Packages Available"]},
            {"icon": "❄️", "title": "AC Services", "desc": "AC installation, repair and annual service.",  "image": "https://placehold.co/400x250/2e7d32/ffffff?text=AC+Service", "features": ["All Brands", "Gas Refill", "AMC Available"]},
        ],
        about_story="QuickFix Home Services started in 2017 to solve one problem: homeowners struggling to find reliable, skilled technicians quickly. Today we have a network of 100+ verified professionals.",
        about_mission="To make quality home services accessible to every household with transparent pricing and guaranteed workmanship.",
        about_values=[
            {"icon": "✅", "title": "Reliability",  "desc": "Show up on time, every time."},
            {"icon": "🔒", "title": "Safety",       "desc": "Verified, background-checked professionals."},
            {"icon": "💰", "title": "Transparency", "desc": "Upfront pricing, no hidden charges."},
            {"icon": "🛡️", "title": "Guarantee",   "desc": "30-day service guarantee on all work."},
        ],
        team=[
            {"name": "Sunil Gupta",  "role": "Founder & CEO",       "avatar": "https://placehold.co/200x200/2e7d32/ffffff?text=SG"},
            {"name": "Mahesh Kumar", "role": "Operations Manager",   "avatar": "https://placehold.co/200x200/558b2f/ffffff?text=MK"},
        ],
        awards=[{"year": "2023", "title": "Best Home Service App", "org": "Jaipur Startup Awards", "icon": "🏆"}],
        milestones=[{"year": "2017", "title": "Founded", "desc": "Started with 10 technicians."}, {"year": "2020", "title": "App Launch", "desc": "Launched mobile booking app."}, {"year": "2023", "title": "10K Services", "desc": "Completed 10,000+ service calls."}],
        stats=[{"value": "10K+", "label": "Jobs Done", "icon": "🛠️"}, {"value": "5K+", "label": "Homes Served", "icon": "🏠"}, {"value": "100+", "label": "Technicians", "icon": "👷"}, {"value": "4.7⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Service Quality", "Technician Behaviour", "Punctuality", "Pricing", "Overall"],
    ),

    # 9. Healthcare
    make_config(
        name="LifeCare Hospital & Clinic", tagline="Compassionate Care. Advanced Medicine.",
        phone="+91 90987 65432", email="care@lifecarehospital.in",
        address="78 Health Street, Kochi, KL 682001",
        theme=make_theme("#00695c", "#0097a7", "#80cbc4", "#e0f2f1", "#003d38", "#00796b", "#003d38"),
        header_tmpl=2, footer_tmpl=3,
        home_title="Your Health, Our Priority",
        home_sub="Expert doctors, modern facilities and compassionate care for every patient and their family.",
        home_features=[
            {"icon": "🏥", "title": "OPD & Consultations", "desc": "Specialist consultations across all departments."},
            {"icon": "🔬", "title": "Diagnostics",         "desc": "Advanced lab tests and imaging services."},
            {"icon": "💊", "title": "Pharmacy",            "desc": "24/7 in-house pharmacy with all medicines."},
            {"icon": "🚑", "title": "Emergency Care",      "desc": "24-hour emergency and trauma care."},
            {"icon": "🦷", "title": "Dental Clinic",       "desc": "Complete dental care and cosmetic dentistry."},
            {"icon": "🏃", "title": "Physiotherapy",       "desc": "Rehabilitation and physiotherapy services."},
        ],
        home_stats=[{"value": "50K+", "label": "Patients Treated"}, {"value": "30+", "label": "Specialist Doctors"}, {"value": "15+", "label": "Years of Care"}, {"value": "24/7", "label": "Emergency Service"}],
        services_title="Medical Services",
        services_items=[
            {"icon": "🏥", "title": "OPD Services",   "desc": "General and specialist doctor consultations.",  "image": "https://placehold.co/400x250/00695c/ffffff?text=OPD", "features": ["15+ Specialties", "Online Appointment", "No Long Wait"]},
            {"icon": "🔬", "title": "Diagnostics",    "desc": "Blood tests, X-ray, MRI, CT scan and more.",    "image": "https://placehold.co/400x250/0097a7/ffffff?text=Diagnostics", "features": ["NABL Certified", "Home Collection", "Online Reports"]},
            {"icon": "🚑", "title": "Emergency",      "desc": "24/7 emergency and critical care services.",    "image": "https://placehold.co/400x250/00695c/ffffff?text=Emergency", "features": ["24/7 ICU", "Ambulance", "Trauma Care"]},
            {"icon": "🦷", "title": "Dental Clinic",  "desc": "All dental procedures and cosmetic dentistry.", "image": "https://placehold.co/400x250/0097a7/ffffff?text=Dental", "features": ["Braces", "Implants", "Root Canal"]},
        ],
        about_story="LifeCare Hospital was established in 2009 to provide accessible, high-quality healthcare to the people of Kochi. With 30+ specialist doctors, we have treated over 50,000 patients.",
        about_mission="To deliver compassionate, affordable and technologically advanced healthcare to every patient.",
        about_values=[
            {"icon": "❤️",  "title": "Compassion",  "desc": "Every patient treated with care and dignity."},
            {"icon": "🔬", "title": "Excellence",   "desc": "Advanced medicine and evidence-based treatment."},
            {"icon": "🤝", "title": "Integrity",    "desc": "Transparent, ethical medical practice."},
            {"icon": "🌱", "title": "Wellness",     "desc": "Focus on prevention, not just cure."},
        ],
        team=[
            {"name": "Dr. Anil Menon",  "role": "Chief Medical Officer", "avatar": "https://placehold.co/200x200/00695c/ffffff?text=AM"},
            {"name": "Dr. Seema Nair",  "role": "Head of Surgery",       "avatar": "https://placehold.co/200x200/0097a7/ffffff?text=SN"},
            {"name": "Dr. Rao Thomas",  "role": "Cardiologist",           "avatar": "https://placehold.co/200x200/00695c/ffffff?text=RT"},
            {"name": "Dr. Latha Iyer",  "role": "Paediatrician",          "avatar": "https://placehold.co/200x200/0097a7/ffffff?text=LI"},
        ],
        awards=[{"year": "2024", "title": "Best Hospital Kochi", "org": "Healthcare Awards India", "icon": "🏆"}, {"year": "2023", "title": "Patient Choice Award", "org": "Health Ratings India", "icon": "❤️"}],
        milestones=[{"year": "2009", "title": "Founded", "desc": "Opened with 10 doctors."}, {"year": "2015", "title": "Expansion", "desc": "Added ICU and emergency wing."}, {"year": "2023", "title": "50K Patients", "desc": "Treated 50,000+ patients."}],
        stats=[{"value": "50K+", "label": "Patients Treated", "icon": "🏥"}, {"value": "30+", "label": "Doctors", "icon": "👨‍⚕️"}, {"value": "15+", "label": "Years", "icon": "📅"}, {"value": "24/7", "label": "Emergency", "icon": "🚑"}],
        categories=["Doctor Expertise", "Staff Behaviour", "Facilities", "Wait Time", "Overall Experience"],
    ),

    # 10. Travel & Transportation
    make_config(
        name="SwiftGo Travel Agency", tagline="Explore. Experience. Remember.",
        phone="+91 89876 54321", email="swiftgo@travel.in",
        address="12 Tourism Plaza, Mumbai, MH 400001",
        theme=make_theme("#0277bd", "#039be5", "#ff7043", "#e1f5fe", "#01355e", "#0288d1", "#01355e"),
        header_tmpl=3, footer_tmpl=1,
        home_title="Discover the World with SwiftGo",
        home_sub="Affordable holiday packages, visa services, honeymoon tours and adventure trips across India and abroad.",
        home_features=[
            {"icon": "✈️", "title": "Holiday Packages",  "desc": "Domestic and international holiday packages."},
            {"icon": "🏨", "title": "Hotel Booking",     "desc": "Best rates on hotels worldwide."},
            {"icon": "🪪", "title": "Visa Assistance",   "desc": "Hassle-free visa processing for any country."},
            {"icon": "💑", "title": "Honeymoon Tours",   "desc": "Romantic getaway packages for newlyweds."},
            {"icon": "🚌", "title": "Bus & Cab Booking", "desc": "Comfortable intercity travel arrangements."},
            {"icon": "🏕️", "title": "Adventure Tours",  "desc": "Trekking, camping and adventure activities."},
        ],
        home_stats=[{"value": "20K+", "label": "Travellers Served"}, {"value": "200+", "label": "Destinations"}, {"value": "12+", "label": "Years Experience"}, {"value": "4.8⭐", "label": "Client Rating"}],
        services_title="Travel & Tourism Services",
        services_items=[
            {"icon": "✈️", "title": "Holiday Packages", "desc": "Customized India and international tours.",   "image": "https://placehold.co/400x250/0277bd/ffffff?text=Holidays", "features": ["Custom Itinerary", "All Inclusive", "Group & Family"]},
            {"icon": "🪪", "title": "Visa Services",    "desc": "Visa processing for 50+ countries.",          "image": "https://placehold.co/400x250/039be5/ffffff?text=Visa", "features": ["Tourist Visa", "Business Visa", "Express Processing"]},
            {"icon": "💑", "title": "Honeymoon Tours",  "desc": "Romantic destinations and luxury packages.",  "image": "https://placehold.co/400x250/ff7043/ffffff?text=Honeymoon", "features": ["Maldives", "Europe", "Bali & Thailand"]},
            {"icon": "🏕️", "title": "Adventure Tours", "desc": "Trekking, camping and adventure holidays.",   "image": "https://placehold.co/400x250/0277bd/ffffff?text=Adventure", "features": ["Himalayan Trek", "River Rafting", "Wildlife Safari"]},
        ],
        about_story="SwiftGo Travel Agency was started in 2012 by travel enthusiast Raj Malhotra with the dream of making quality travel accessible to every Indian family at honest prices.",
        about_mission="To create unforgettable travel experiences that inspire people to explore the world.",
        about_values=[
            {"icon": "🌍", "title": "Discovery",   "desc": "We believe travel transforms lives."},
            {"icon": "💰", "title": "Value",        "desc": "Best rates with no hidden charges."},
            {"icon": "🔒", "title": "Trust",        "desc": "Safe and reliable travel at all times."},
            {"icon": "😊", "title": "Experience",   "desc": "Creating memories that last a lifetime."},
        ],
        team=[
            {"name": "Raj Malhotra", "role": "Founder & CEO",       "avatar": "https://placehold.co/200x200/0277bd/ffffff?text=RM"},
            {"name": "Aarti Singh",  "role": "Tour Manager",         "avatar": "https://placehold.co/200x200/039be5/ffffff?text=AS"},
            {"name": "Sanjay Mehta", "role": "Visa Specialist",      "avatar": "https://placehold.co/200x200/0277bd/ffffff?text=SM"},
            {"name": "Nita Patel",   "role": "Customer Relations",   "avatar": "https://placehold.co/200x200/039be5/ffffff?text=NP"},
        ],
        awards=[{"year": "2024", "title": "Best Travel Agency Mumbai", "org": "Travel Awards India", "icon": "✈️"}, {"year": "2023", "title": "Top Honeymoon Planner", "org": "Weddings Today", "icon": "💑"}],
        milestones=[{"year": "2012", "title": "Founded", "desc": "Started with 3 staff."}, {"year": "2017", "title": "10K Travellers", "desc": "Served 10,000 happy travellers."}, {"year": "2023", "title": "20K Milestone", "desc": "Reached 20,000 satisfied customers."}],
        stats=[{"value": "20K+", "label": "Travellers", "icon": "✈️"}, {"value": "200+", "label": "Destinations", "icon": "🌍"}, {"value": "12+", "label": "Years", "icon": "📅"}, {"value": "4.8⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Tour Quality", "Value for Money", "Guide Knowledge", "Accommodation", "Overall Experience"],
    ),

    # 11. Finance & Banking
    make_config(
        name="SecureWealth Finance", tagline="Your Financial Future Starts Here",
        phone="+91 88765 43210", email="info@securewealth.in",
        address="14 Finance District, New Delhi, DL 110001",
        theme=make_theme("#1a237e", "#303f9f", "#c5a028", "#e8eaf6", "#0a1050", "#283593", "#0a1050"),
        header_tmpl=4, footer_tmpl=2,
        home_title="Smart Financial Solutions for a Secure Tomorrow",
        home_sub="Trusted insurance, investment, tax planning and loan services for individuals and businesses.",
        home_features=[
            {"icon": "🛡️", "title": "Insurance Services",  "desc": "Life, health, vehicle and property insurance."},
            {"icon": "💹", "title": "Investment Planning",  "desc": "Mutual funds, SIP, FD and wealth management."},
            {"icon": "📋", "title": "Tax Consultancy",      "desc": "ITR filing, GST and tax planning services."},
            {"icon": "🏠", "title": "Home Loans",           "desc": "Best rates on home and personal loans."},
            {"icon": "🏢", "title": "Business Finance",    "desc": "Business loans and financial advisory."},
            {"icon": "📊", "title": "Financial Planning",   "desc": "Retirement and goal-based financial planning."},
        ],
        home_stats=[{"value": "5000+", "label": "Clients Served"}, {"value": "₹100Cr+", "label": "Assets Managed"}, {"value": "10+", "label": "Years Experience"}, {"value": "98%", "label": "Client Retention"}],
        services_title="Financial Services",
        services_items=[
            {"icon": "🛡️", "title": "Insurance",         "desc": "Comprehensive insurance solutions.",           "image": "https://placehold.co/400x250/1a237e/ffffff?text=Insurance", "features": ["Life Insurance", "Health Insurance", "Vehicle Insurance"]},
            {"icon": "💹", "title": "Investments",        "desc": "Mutual funds, SIP and portfolio management.",  "image": "https://placehold.co/400x250/303f9f/ffffff?text=Investments", "features": ["Mutual Funds", "SIP", "Equity & Debt"]},
            {"icon": "📋", "title": "Tax Services",       "desc": "ITR, GST filing and tax planning.",            "image": "https://placehold.co/400x250/c5a028/0a1050?text=Tax", "features": ["ITR Filing", "GST Compliance", "Tax Saving"]},
            {"icon": "🏠", "title": "Loan Services",      "desc": "Home, personal and business loans.",           "image": "https://placehold.co/400x250/1a237e/ffffff?text=Loans", "features": ["Low Interest", "Quick Approval", "All Banks"]},
        ],
        about_story="SecureWealth Finance was founded in 2014 by Certified Financial Planner Vikram Joshi with a vision to provide honest, transparent financial advice to ordinary Indians.",
        about_mission="To empower every Indian with the financial knowledge and tools to achieve their life goals.",
        about_values=[
            {"icon": "🔒", "title": "Trust",          "desc": "Your money, your decisions, our guidance."},
            {"icon": "📊", "title": "Transparency",   "desc": "No hidden fees, complete disclosure always."},
            {"icon": "🎓", "title": "Knowledge",      "desc": "Expert advice backed by certified professionals."},
            {"icon": "🌱", "title": "Growth",         "desc": "Focused on long-term wealth creation for clients."},
        ],
        team=[
            {"name": "Vikram Joshi",  "role": "CFP & Founder",       "avatar": "https://placehold.co/200x200/1a237e/ffffff?text=VJ"},
            {"name": "Rina Kapoor",   "role": "Insurance Specialist", "avatar": "https://placehold.co/200x200/303f9f/ffffff?text=RK"},
            {"name": "Deepak Arora",  "role": "Tax Consultant",       "avatar": "https://placehold.co/200x200/1a237e/ffffff?text=DA"},
            {"name": "Sunita Singh",  "role": "Investment Advisor",   "avatar": "https://placehold.co/200x200/303f9f/ffffff?text=SS"},
        ],
        awards=[{"year": "2024", "title": "Top Financial Advisor Delhi", "org": "Financial Services Awards", "icon": "🏆"}, {"year": "2023", "title": "Best Insurance Agency", "org": "IRDAI Regional Awards", "icon": "🛡️"}],
        milestones=[{"year": "2014", "title": "Founded", "desc": "Started as a solo practice."}, {"year": "2018", "title": "₹50Cr AUM", "desc": "Crossed ₹50 Crore assets under management."}, {"year": "2023", "title": "₹100Cr AUM", "desc": "Doubled AUM with 5000+ clients."}],
        stats=[{"value": "5K+", "label": "Clients", "icon": "👥"}, {"value": "₹100Cr+", "label": "AUM", "icon": "💰"}, {"value": "10+", "label": "Years", "icon": "📅"}, {"value": "98%", "label": "Retention", "icon": "🔒"}],
        categories=["Financial Advice", "Product Range", "Returns", "Customer Service", "Overall"],
    ),

    # 12. Real Estate
    make_config(
        name="DreamHome Properties", tagline="Find Your Perfect Home with Us",
        phone="+91 87654 32109", email="info@dreamhome.in",
        address="23 Builders Street, Noida, UP 201301",
        theme=make_theme("#5d4037", "#795548", "#ffc107", "#fdf8f0", "#321911", "#6d4c41", "#321911"),
        header_tmpl=3, footer_tmpl=3,
        home_title="Where Your Dream Home Becomes Reality",
        home_sub="Expert property consultation, verified listings and seamless transactions for buyers, sellers and renters.",
        home_features=[
            {"icon": "🏠", "title": "Residential Properties", "desc": "Apartments, villas and independent houses."},
            {"icon": "🏢", "title": "Commercial Properties",  "desc": "Offices, shops and commercial spaces."},
            {"icon": "🏗️", "title": "New Projects",           "desc": "Upcoming and under-construction projects."},
            {"icon": "🔑", "title": "Rental Services",        "desc": "Verified rental properties across the city."},
            {"icon": "⚖️", "title": "Legal Services",         "desc": "Property registration and legal documentation."},
            {"icon": "🏡", "title": "Interior Design",        "desc": "Turn your new house into a beautiful home."},
        ],
        home_stats=[{"value": "2000+", "label": "Properties Listed"}, {"value": "1500+", "label": "Happy Families"}, {"value": "12+", "label": "Years Experience"}, {"value": "₹500Cr+", "label": "Deals Closed"}],
        services_title="Property Services",
        services_items=[
            {"icon": "🏠", "title": "Buy Property",    "desc": "Find your dream home from verified listings.",   "image": "https://placehold.co/400x250/5d4037/ffffff?text=Buy", "features": ["2000+ Listings", "Verified Sellers", "Free Consultation"]},
            {"icon": "🔑", "title": "Rent Property",   "desc": "Hassle-free rental with verified landlords.",    "image": "https://placehold.co/400x250/795548/ffffff?text=Rent", "features": ["No Brokerage Option", "Quick Move-in", "Police Verified"]},
            {"icon": "🏗️", "title": "New Projects",    "desc": "Best upcoming projects with early-bird pricing.", "image": "https://placehold.co/400x250/ffc107/321911?text=Projects", "features": ["RERA Registered", "Bank Approved", "Site Visit Free"]},
            {"icon": "⚖️", "title": "Legal Services",  "desc": "End-to-end property registration and docs.",     "image": "https://placehold.co/400x250/5d4037/ffffff?text=Legal", "features": ["Registration", "Sale Deed", "Property Valuation"]},
        ],
        about_story="DreamHome Properties was founded in 2012 with a mission to bring transparency and trust to real estate transactions. We have helped 1500+ families find their perfect home.",
        about_mission="To make every property transaction simple, transparent and stress-free for buyers, sellers and investors.",
        about_values=[
            {"icon": "🔒", "title": "Transparency",  "desc": "No hidden costs, full disclosure always."},
            {"icon": "🤝", "title": "Trust",         "desc": "Verified listings and honest dealings."},
            {"icon": "⭐", "title": "Expertise",     "desc": "12+ years of local market knowledge."},
            {"icon": "❤️",  "title": "Care",          "desc": "Every family deserves their dream home."},
        ],
        team=[
            {"name": "Arjun Kapoor", "role": "Founder & Director",   "avatar": "https://placehold.co/200x200/5d4037/ffffff?text=AK"},
            {"name": "Seema Yadav",  "role": "Senior Property Agent", "avatar": "https://placehold.co/200x200/795548/ffffff?text=SY"},
            {"name": "Mohit Singh",  "role": "Legal Advisor",         "avatar": "https://placehold.co/200x200/5d4037/ffffff?text=MS"},
            {"name": "Priya Gupta",  "role": "Interior Consultant",   "avatar": "https://placehold.co/200x200/795548/ffffff?text=PG"},
        ],
        awards=[{"year": "2024", "title": "Top Real Estate Agency Noida", "org": "NCR Property Awards", "icon": "🏆"}, {"year": "2023", "title": "Most Trusted Brand", "org": "Real Estate Business Awards", "icon": "🔒"}],
        milestones=[{"year": "2012", "title": "Founded", "desc": "Started with 50 listed properties."}, {"year": "2017", "title": "500 Deals", "desc": "Closed 500 successful property deals."}, {"year": "2023", "title": "1500 Families", "desc": "Helped 1500 families find their dream home."}],
        stats=[{"value": "2K+", "label": "Listings", "icon": "🏠"}, {"value": "1.5K+", "label": "Families", "icon": "👨‍👩‍👧"}, {"value": "12+", "label": "Years", "icon": "📅"}, {"value": "₹500Cr+", "label": "Deals", "icon": "💰"}],
        categories=["Property Quality", "Agent Service", "Transparency", "Legal Support", "Overall"],
    ),

    # 13. Other Services — Pet Care
    make_config(
        name="PawsAndClaws Pet Care", tagline="Because Pets Deserve the Best",
        phone="+91 86543 21098", email="hello@pawsandclaws.in",
        address="9 Green Park, Bengaluru, KA 560016",
        theme=make_theme("#e65100", "#f57c00", "#66bb6a", "#fff8f0", "#883300", "#ef6c00", "#3e1a00"),
        header_tmpl=1, footer_tmpl=4,
        home_title="Premium Care for Your Beloved Pets",
        home_sub="Veterinary care, grooming, boarding, training and pet supplies — everything your pet needs under one roof.",
        home_features=[
            {"icon": "🏥", "title": "Veterinary Care",   "desc": "Expert vets for health check-ups and treatment."},
            {"icon": "✂️", "title": "Pet Grooming",       "desc": "Full grooming for dogs, cats and small pets."},
            {"icon": "🏨", "title": "Pet Boarding",       "desc": "Safe and comfortable stay when you travel."},
            {"icon": "🎾", "title": "Pet Training",       "desc": "Obedience and behaviour training programs."},
            {"icon": "🦴", "title": "Pet Nutrition",      "desc": "Premium pet food and nutritional supplements."},
            {"icon": "💉", "title": "Vaccination",        "desc": "Complete vaccination schedules for all pets."},
        ],
        home_stats=[{"value": "3000+", "label": "Pets Cared For"}, {"value": "5", "label": "Expert Vets"}, {"value": "6+", "label": "Years Serving"}, {"value": "4.9⭐", "label": "Pet Parent Rating"}],
        services_title="Pet Care Services",
        services_items=[
            {"icon": "🏥", "title": "Vet Consultations", "desc": "Diagnosis, treatment and surgery for all pets.",  "image": "https://placehold.co/400x250/e65100/ffffff?text=Vet+Care", "features": ["All Pets", "Emergency Care", "Post-Op Care"]},
            {"icon": "✂️", "title": "Pet Grooming",       "desc": "Bath, haircut, nail trim and styling.",          "image": "https://placehold.co/400x250/f57c00/ffffff?text=Grooming", "features": ["Dogs & Cats", "Breed-Specific", "Monthly Packages"]},
            {"icon": "🏨", "title": "Pet Boarding",       "desc": "Supervised boarding with play time and meals.",  "image": "https://placehold.co/400x250/66bb6a/ffffff?text=Boarding", "features": ["24/7 Care", "Daily Updates", "CCTV Monitored"]},
            {"icon": "🎾", "title": "Pet Training",       "desc": "Professional dog training programs.",             "image": "https://placehold.co/400x250/e65100/ffffff?text=Training", "features": ["Obedience", "Socialization", "Certified Trainer"]},
        ],
        about_story="PawsAndClaws was founded in 2018 by Dr. Kavya Reddy, a passionate veterinarian, to give pets the professional care they deserve in a warm, loving environment.",
        about_mission="To improve the health, happiness and longevity of every pet through expert veterinary care and genuine love for animals.",
        about_values=[
            {"icon": "❤️",  "title": "Love",        "desc": "Every pet is treated as our own."},
            {"icon": "🔬", "title": "Expertise",   "desc": "Certified vets and trained pet care staff."},
            {"icon": "🌱", "title": "Wellness",    "desc": "Preventive care for a longer, healthier life."},
            {"icon": "😊", "title": "Happiness",   "desc": "Happy pets, happy pet parents."},
        ],
        team=[
            {"name": "Dr. Kavya Reddy",  "role": "Chief Veterinarian & Founder", "avatar": "https://placehold.co/200x200/e65100/ffffff?text=KR"},
            {"name": "Dr. Arjun Rao",    "role": "Veterinary Surgeon",            "avatar": "https://placehold.co/200x200/f57c00/ffffff?text=AR"},
            {"name": "Preethi Nair",     "role": "Head Groomer",                   "avatar": "https://placehold.co/200x200/66bb6a/ffffff?text=PN"},
            {"name": "Sanjay Kumar",     "role": "Pet Trainer",                    "avatar": "https://placehold.co/200x200/e65100/ffffff?text=SK"},
        ],
        awards=[{"year": "2024", "title": "Best Pet Clinic Bengaluru", "org": "Pet Industry Awards India", "icon": "🐾"}, {"year": "2023", "title": "Top Grooming Salon", "org": "Pets World Awards", "icon": "✂️"}],
        milestones=[{"year": "2018", "title": "Founded", "desc": "Started with 1 vet and 2 staff."}, {"year": "2021", "title": "1000 Pets", "desc": "Cared for 1000+ pets."}, {"year": "2024", "title": "3000 Pets", "desc": "Grew to a 5-vet team serving 3000+ pets."}],
        stats=[{"value": "3K+", "label": "Pets Cared For", "icon": "🐾"}, {"value": "5", "label": "Expert Vets", "icon": "👨‍⚕️"}, {"value": "6+", "label": "Years", "icon": "📅"}, {"value": "4.9⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Vet Care Quality", "Grooming", "Staff Behaviour", "Cleanliness", "Overall"],
    ),

    # 14. Fitness Gym (Template 5 - 3-column grid)
    make_config(
        name="PowerFit Gym & Wellness", tagline="Transform Your Body, Strengthen Your Mind",
        phone="+91 94321 09876", email="info@powerfit.in",
        address="18 Fitness Lane, Mumbai, MH 400050",
        theme=make_theme("#d32f2f", "#ff6f00", "#ffc400", "#ffebee", "#bf360c", "#e53935", "#1a0e0e"),
        header_tmpl=3, footer_tmpl=1,
        home_title="Your Fitness Journey Starts Here",
        home_sub="State-of-the-art equipment, certified trainers, and personalized fitness plans for all goals.",
        home_features=[
            {"icon": "🏋️", "title": "Strength Training",  "desc": "Complete strength training with modern equipment."},
            {"icon": "🧘", "title": "Yoga Classes",        "desc": "Daily yoga classes for flexibility and mind peace."},
            {"icon": "🏃", "title": "Cardio Zone",         "desc": "Treadmills, bikes and ellipticals for cardio fitness."},
            {"icon": "👨‍🏫", "title": "Personal Training",  "desc": "One-on-one sessions with certified trainers."},
            {"icon": "🍎", "title": "Nutrition Plans",     "desc": "Customized diet plans by nutritionists."},
            {"icon": "🧖", "title": "Spa & Sauna",         "desc": "Relax and recover in our wellness center."},
        ],
        home_stats=[{"value": "1500+", "label": "Active Members"}, {"value": "30+", "label": "Certified Trainers"}, {"value": "8+", "label": "Years in Business"}, {"value": "5000sqft", "label": "Facility Area"}],
        services_title="Fitness Programs",
        services_items=[
            {"icon": "🏋️", "title": "Strength Training",    "desc": "Build muscle and gain strength.",                         "image": "https://placehold.co/400x250/d32f2f/ffffff?text=Strength", "features": ["Dumbbells", "Barbells", "Cable Machine"]},
            {"icon": "🧘", "title": "Yoga & Pilates",       "desc": "Flexibility, balance and core strength.",                  "image": "https://placehold.co/400x250/ff6f00/ffffff?text=Yoga", "features": ["Hatha Yoga", "Pilates", "Stretching"]},
            {"icon": "🏃", "title": "Cardio Classes",       "desc": "Burn calories with high-intensity cardio.",               "image": "https://placehold.co/400x250/ffc400/ffffff?text=Cardio", "features": ["Zumba", "Aerobics", "Spin Class"]},
            {"icon": "👨‍🏫", "title": "Personal Training",  "desc": "Customized workouts with expert trainers.",               "image": "https://placehold.co/400x250/d32f2f/ffffff?text=Training", "features": ["Goal Planning", "Form Correction", "Progress Tracking"]},
        ],
        about_story="PowerFit Gym was founded in 2016 to make fitness accessible to everyone in Mumbai. Today we have 1500+ happy members transforming their lives daily.",
        about_mission="To inspire and empower every person to achieve their fitness goals through world-class facilities and expert guidance.",
        about_values=[
            {"icon": "💪", "title": "Strength",   "desc": "We believe in building strength — body and mind."},
            {"icon": "🎯", "title": "Goal-Driven", "desc": "Every member has a clear fitness goal and plan."},
            {"icon": "🤝", "title": "Community",  "desc": "We foster a supportive fitness community."},
            {"icon": "📈", "title": "Progress",   "desc": "Measure and celebrate every milestone."},
        ],
        team=[
            {"name": "Rajesh Kumar",  "role": "Head Trainer & Founder",  "avatar": "https://placehold.co/200x200/d32f2f/ffffff?text=RK"},
            {"name": "Priya Gupta",   "role": "Yoga Instructor",         "avatar": "https://placehold.co/200x200/ff6f00/ffffff?text=PG"},
            {"name": "Arjun Singh",   "role": "Nutrition Specialist",    "avatar": "https://placehold.co/200x200/ffc400/ffffff?text=AS"},
        ],
        awards=[{"year": "2024", "title": "Best Gym in Mumbai", "org": "Fitness Awards India", "icon": "🏆"}, {"year": "2023", "title": "Top Fitness Center", "org": "Health & Wellness Awards", "icon": "💪"}],
        milestones=[{"year": "2016", "title": "Opened", "desc": "Started with 50 members."}, {"year": "2020", "title": "500 Members", "desc": "Crossed 500 active members."}, {"year": "2024", "title": "1500 Members", "desc": "Celebrating 1500+ fitness enthusiasts."}],
        stats=[{"value": "1.5K+", "label": "Members", "icon": "👥"}, {"value": "30+", "label": "Trainers", "icon": "👨‍🏫"}, {"value": "8+", "label": "Years", "icon": "📅"}, {"value": "5K+sqft", "label": "Facility", "icon": "🏢"}],
        categories=["Equipment Quality", "Trainer Expertise", "Class Variety", "Cleanliness", "Overall"],
    ),

    # 15. Fine Dining Restaurant (Template 6 - Sidebar)
    make_config(
        name="Flavor Bistro Premium Dining", tagline="Culinary Excellence Meets Fine Service",
        phone="+91 93210 98765", email="reservations@flavorbistro.in",
        address="52 Five-Star Lane, Delhi, DL 110001",
        theme=make_theme("#8b4513", "#d4af37", "#ffd700", "#fef5e7", "#3e2723", "#a1887f", "#2d1810"),
        header_tmpl=4, footer_tmpl=2,
        home_title="An Exquisite Culinary Experience",
        home_sub="Multi-cuisine fine dining restaurant featuring award-winning chefs and premium ingredients.",
        home_features=[
            {"icon": "👨‍🍳", "title": "Award-Winning Chefs",    "desc": "Experienced chefs creating culinary masterpieces."},
            {"icon": "🍽️", "title": "Multi-Cuisine Menu",      "desc": "Indian, Continental, Asian and Fusion cuisines."},
            {"icon": "🥂", "title": "Premium Bar & Drinks",     "desc": "Curated wine selection and signature cocktails."},
            {"icon": "🎻", "title": "Live Entertainment",       "desc": "Jazz and classical music every evening."},
            {"icon": "💎", "title": "Private Dining",           "desc": "Intimate spaces for celebrations and events."},
            {"icon": "🎓", "title": "Chef's Table",             "desc": "Exclusive culinary experience with the chef."},
        ],
        home_stats=[{"value": "5 ⭐", "label": "Rating"}, {"value": "200+", "label": "Covers Daily"}, {"value": "12+", "label": "Years Legacy"}, {"value": "95%", "label": "Repeat Guests"}],
        services_title="Our Menu & Services",
        services_items=[
            {"icon": "🍜", "title": "Indian Cuisine",      "desc": "Authentic regional Indian delicacies.",                   "image": "https://placehold.co/400x250/8b4513/ffffff?text=Indian", "features": ["North Indian", "South Indian", "Coastal Recipes"]},
            {"icon": "🥩", "title": "Continental Menu",    "desc": "European classics with modern twist.",                    "image": "https://placehold.co/400x250/d4af37/ffffff?text=Continental", "features": ["Steaks", "Seafood", "Pasta Specialties"]},
            {"icon": "🍱", "title": "Asian Fusion",        "desc": "Creative Asian-inspired contemporary dishes.",            "image": "https://placehold.co/400x250/ffd700/ffffff?text=Fusion", "features": ["Thai", "Japanese", "Chinese Fusion"]},
            {"icon": "🍰", "title": "Desserts & Drinks",   "desc": "Artisanal desserts and curated beverages.",                "image": "https://placehold.co/400x250/8b4513/ffffff?text=Desserts", "features": ["House Specials", "Wine Pairings", "Signature Cocktails"]},
        ],
        about_story="Flavor Bistro was founded in 2012 by Chef Vikram Verma to bring world-class fine dining to Delhi. Every dish is a story of tradition and innovation.",
        about_mission="To deliver an unforgettable dining experience through exceptional food, service, and ambiance.",
        about_values=[
            {"icon": "🌟", "title": "Excellence",  "desc": "Excellence in every aspect of dining."},
            {"icon": "🌿", "title": "Quality",     "desc": "Only premium and fresh ingredients used."},
            {"icon": "🎨", "title": "Creativity",  "desc": "Every dish is an art, not just food."},
            {"icon": "❤️", "title": "Hospitality", "desc": "Warm, attentive service always."},
        ],
        team=[
            {"name": "Chef Vikram Verma",  "role": "Executive Chef & Founder",  "avatar": "https://placehold.co/200x200/8b4513/ffffff?text=VV"},
            {"name": "Aditi Sharma",       "role": "Head Sommelier",            "avatar": "https://placehold.co/200x200/d4af37/ffffff?text=AS"},
            {"name": "Rajesh Patel",      "role": "Restaurant Manager",        "avatar": "https://placehold.co/200x200/ffd700/ffffff?text=RP"},
        ],
        awards=[{"year": "2024", "title": "Best Fine Dining Delhi", "org": "Culinary Awards India", "icon": "🏆"}, {"year": "2023", "title": "Chef's Excellence", "org": "Gourmet Magazine", "icon": "👨‍🍳"}],
        milestones=[{"year": "2012", "title": "Opened", "desc": "Chef Vikram's dream restaurant."}, {"year": "2018", "title": "5-Star Recognition", "desc": "Achieved 5-star dining status."}, {"year": "2024", "title": "12 Years", "desc": "A decade of culinary excellence."}],
        stats=[{"value": "5 ⭐", "label": "Rating", "icon": "⭐"}, {"value": "200+", "label": "Daily Covers", "icon": "🍽️"}, {"value": "12+", "label": "Years", "icon": "📅"}, {"value": "95%", "label": "Loyalty", "icon": "❤️"}],
        categories=["Food Quality", "Service", "Ambiance", "Value for Money", "Overall"],
    ),

    # 16. Beauty Salon (Template 7 - Alternating Cards)
    make_config(
        name="Glamour Studio Beauty Salon", tagline="Enhance Your Natural Beauty",
        phone="+91 92109 87654", email="book@glamourstudio.in",
        address="34 Fashion Street, Bangalore, KA 560001",
        theme=make_theme("#c2185b", "#e91e63", "#ff5252", "#fce4ec", "#880e4f", "#ad1457", "#4a0e4e"),
        header_tmpl=2, footer_tmpl=3,
        home_title="Your Beauty, Our Passion",
        home_sub="Premium beauty services from hair to nails, with trained professionals using international products.",
        home_features=[
            {"icon": "💇", "title": "Hair Styling",      "desc": "Cuts, colors, treatments and styling."},
            {"icon": "💄", "title": "Makeup Artistry",   "desc": "Bridal, party and everyday makeup."},
            {"icon": "💅", "title": "Nail Services",     "desc": "Manicure, pedicure and nail art."},
            {"icon": "💆", "title": "Spa & Massage",     "desc": "Body massage, facials and skincare."},
            {"icon": "🧴", "title": "Skincare",          "desc": "Dermatologist-approved skincare treatments."},
            {"icon": "✨", "title": "Threading & Wax",   "desc": "Professional hair removal services."},
        ],
        home_stats=[{"value": "3000+", "label": "Happy Clients"}, {"value": "25+", "label": "Beauty Experts"}, {"value": "6+", "label": "Years Beauty"}, {"value": "4.8⭐", "label": "Rating"}],
        services_title="Beauty Services",
        services_items=[
            {"icon": "💇", "title": "Hair Services",     "desc": "Complete hair care solutions.",                            "image": "https://placehold.co/400x250/c2185b/ffffff?text=Hair", "features": ["Coloring", "Smoothening", "Keratin Treatment"]},
            {"icon": "💄", "title": "Makeup & Bridal",   "desc": "Professional makeup for every occasion.",                  "image": "https://placehold.co/400x250/e91e63/ffffff?text=Makeup", "features": ["Bridal Makeup", "Party Makeup", "HD Makeup"]},
            {"icon": "💅", "title": "Nail Art Studio",   "desc": "Nails, extensions and nail art.",                          "image": "https://placehold.co/400x250/ff5252/ffffff?text=Nails", "features": ["Gel Nails", "Nail Art", "Acrylics"]},
            {"icon": "💆", "title": "Spa & Wellness",    "desc": "Relax with body treatments and massage.",                  "image": "https://placehold.co/400x250/c2185b/ffffff?text=Spa", "features": ["Full Body Massage", "Facials", "Body Scrubs"]},
        ],
        about_story="Glamour Studio was founded in 2018 by Priya Sharma to offer a sanctuary of beauty and wellness. We believe every woman deserves to feel beautiful.",
        about_mission="To empower women through beauty services and create a confidence-boosting experience.",
        about_values=[
            {"icon": "✨", "title": "Beauty",    "desc": "Enhancing natural beauty, not masking it."},
            {"icon": "🌸", "title": "Self-Care", "desc": "Wellness and self-care for all."},
            {"icon": "👥", "title": "Community", "desc": "A welcoming space for all beauty enthusiasts."},
            {"icon": "💎", "title": "Premium",   "desc": "Only quality products and services."},
        ],
        team=[
            {"name": "Priya Sharma",      "role": "Founder & Beauty Expert",  "avatar": "https://placehold.co/200x200/c2185b/ffffff?text=PS"},
            {"name": "Megha Verma",       "role": "Senior Makeup Artist",     "avatar": "https://placehold.co/200x200/e91e63/ffffff?text=MV"},
            {"name": "Neha Patel",        "role": "Hair Styling Specialist",  "avatar": "https://placehold.co/200x200/ff5252/ffffff?text=NP"},
            {"name": "Anjali Kumar",      "role": "Skincare Specialist",      "avatar": "https://placehold.co/200x200/c2185b/ffffff?text=AK"},
        ],
        awards=[{"year": "2024", "title": "Best Beauty Salon Bangalore", "org": "Beauty Awards India", "icon": "💎"}, {"year": "2023", "title": "Customer Favorite", "org": "Salon Awards", "icon": "⭐"}],
        milestones=[{"year": "2018", "title": "Opened", "desc": "Priya's dream beauty space."}, {"year": "2021", "title": "1000 Clients", "desc": "Served 1000 happy clients."}, {"year": "2024", "title": "3000 Clients", "desc": "Growing community of 3000+ beauty enthusiasts."}],
        stats=[{"value": "3K+", "label": "Happy Clients", "icon": "👥"}, {"value": "25+", "label": "Beauty Experts", "icon": "💇"}, {"value": "6+", "label": "Years", "icon": "📅"}, {"value": "4.8⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Service Quality", "Staff Expertise", "Hygiene", "Value for Money", "Overall"],
    ),

    # 17. Consulting Firm (Template 5 - 3-column grid)
    make_config(
        name="Strategic Minds Consulting", tagline="Business Solutions. Growth Guaranteed.",
        phone="+91 91098 76543", email="contact@strategicminds.in",
        address="101 Business Tower, Gurgaon, HR 122001",
        theme=make_theme("#1a237e", "#283593", "#3f51b5", "#eceff1", "#001064", "#1a237e", "#0d0e3f"),
        header_tmpl=1, footer_tmpl=4,
        home_title="Transform Your Business With Expert Strategies",
        home_sub="Management consulting services helping enterprises achieve sustainable growth and operational excellence.",
        home_features=[
            {"icon": "📊", "title": "Strategy Consulting", "desc": "Market analysis and strategic planning."},
            {"icon": "💼", "title": "Business Advisory",   "desc": "Expert business solutions and guidance."},
            {"icon": "🔍", "title": "Market Research",    "desc": "In-depth industry and market analysis."},
            {"icon": "🚀", "title": "Growth Planning",    "desc": "Scaling strategies for startups and enterprises."},
            {"icon": "💡", "title": "Innovation",         "desc": "Digital transformation and innovation."},
            {"icon": "📈", "title": "Performance Mgmt",   "desc": "KPI tracking and performance optimization."},
        ],
        home_stats=[{"value": "500+", "label": "Clients Served"}, {"value": "30+", "label": "Consultants"}, {"value": "15+", "label": "Industry Expertise"}, {"value": "85%", "label": "Success Rate"}],
        services_title="Consulting Services",
        services_items=[
            {"icon": "📊", "title": "Strategy & Planning",  "desc": "Comprehensive business strategy development.",        "image": "https://placehold.co/400x250/1a237e/ffffff?text=Strategy", "features": ["5-Year Plan", "Market Analysis", "Competitive Edge"]},
            {"icon": "💼", "title": "Operations Consulting", "desc": "Optimize business operations and processes.",          "image": "https://placehold.co/400x250/283593/ffffff?text=Operations", "features": ["Process Improvement", "Cost Reduction", "Efficiency"]},
            {"icon": "🚀", "title": "Growth & Scaling",     "desc": "Strategies for rapid and sustainable growth.",        "image": "https://placehold.co/400x250/3f51b5/ffffff?text=Growth", "features": ["Market Expansion", "New Revenue Streams", "M&A Advisory"]},
            {"icon": "💻", "title": "Digital Transformation","desc": "Tech integration and digital strategy.",              "image": "https://placehold.co/400x250/1a237e/ffffff?text=Digital", "features": ["Cloud Migration", "Automation", "Digital Marketing"]},
        ],
        about_story="Strategic Minds was founded in 2009 by a group of IIT and IIM alumni passionate about helping businesses succeed. We've guided 500+ companies through transformation.",
        about_mission="To empower businesses with strategic insights and actionable solutions for sustainable growth.",
        about_values=[
            {"icon": "🎯", "title": "Results-Driven", "desc": "Every consulting engagement delivers measurable results."},
            {"icon": "🧠", "title": "Expertise",     "desc": "Deep industry knowledge from seasoned consultants."},
            {"icon": "🤝", "title": "Partnership",   "desc": "We are partners in your success journey."},
            {"icon": "💡", "title": "Innovation",    "desc": "Forward-thinking solutions for tomorrow's challenges."},
        ],
        team=[
            {"name": "Dr. Rajeev Sharma",   "role": "Founder & Senior Partner",     "avatar": "https://placehold.co/200x200/1a237e/ffffff?text=RS"},
            {"name": "Geeta Sinha",         "role": "Strategy Lead",                "avatar": "https://placehold.co/200x200/283593/ffffff?text=GS"},
            {"name": "Akshay Mehta",        "role": "Operations Consultant",        "avatar": "https://placehold.co/200x200/3f51b5/ffffff?text=AM"},
            {"name": "Divya Reddy",         "role": "Digital Transformation Head",  "avatar": "https://placehold.co/200x200/1a237e/ffffff?text=DR"},
        ],
        awards=[{"year": "2024", "title": "Best Management Consultants", "org": "Business Excellence Awards", "icon": "🏆"}, {"year": "2023", "title": "Top Strategy Firm", "org": "Business Today", "icon": "📊"}],
        milestones=[{"year": "2009", "title": "Founded", "desc": "Started with 3 consultants."}, {"year": "2016", "title": "100 Clients", "desc": "Reached 100 consulting engagements."}, {"year": "2024", "title": "500 Clients", "desc": "500+ successful transformations."}],
        stats=[{"value": "500+", "label": "Clients", "icon": "🏢"}, {"value": "30+", "label": "Consultants", "icon": "👥"}, {"value": "15+", "label": "Industries", "icon": "🏭"}, {"value": "85%", "label": "Success", "icon": "✅"}],
        categories=["Consultant Expertise", "Solution Quality", "Project Delivery", "Value Delivered", "Overall"],
    ),

    # 18. E-Learning Platform (Template 6 - Sidebar)
    make_config(
        name="LearnHub Online Academy", tagline="Learn. Grow. Succeed.",
        phone="+91 90987 65432", email="support@learnhub.in",
        address="Virtual Platform - Pan India",
        theme=make_theme("#6f42c1", "#5a6268", "#ff7043", "#f8f9fa", "#3a0d5e", "#7952b3", "#2a0845"),
        header_tmpl=3, footer_tmpl=1,
        home_title="Master New Skills Online, At Your Pace",
        home_sub="Industry-leading courses in technology, business, and creative skills taught by expert instructors.",
        home_features=[
            {"icon": "💻", "title": "Tech Courses",      "desc": "Programming, web dev, data science and AI."},
            {"icon": "📈", "title": "Business Skills",   "desc": "Leadership, management and finance courses."},
            {"icon": "🎨", "title": "Creative Courses",  "desc": "Design, photography and content creation."},
            {"icon": "🏆", "title": "Certifications",    "desc": "Industry-recognized certificates upon completion."},
            {"icon": "🎯", "title": "Live Sessions",     "desc": "Interactive classes with instructors."},
            {"icon": "💰", "title": "Affordable Plans",  "desc": "Flexible pricing with lifetime access."},
        ],
        home_stats=[{"value": "50K+", "label": "Active Students"}, {"value": "500+", "label": "Courses"}, {"value": "100+", "label": "Expert Instructors"}, {"value": "4.7⭐", "label": "Rating"}],
        services_title="Course Categories",
        services_items=[
            {"icon": "💻", "title": "Web Development",     "desc": "Learn frontend, backend and full-stack.",              "image": "https://placehold.co/400x250/6f42c1/ffffff?text=Web+Dev", "features": ["React", "Node.js", "Python"]},
            {"icon": "📊", "title": "Data Science",        "desc": "Analytics, machine learning and AI.",                 "image": "https://placehold.co/400x250/5a6268/ffffff?text=Data", "features": ["Python ML", "TensorFlow", "Analytics"]},
            {"icon": "📈", "title": "Business & Finance",  "desc": "Management, accounting and economics.",               "image": "https://placehold.co/400x250/ff7043/ffffff?text=Business", "features": ["MBA Topics", "Finance", "Leadership"]},
            {"icon": "🎨", "title": "Creative Skills",     "desc": "Design, photography and content creation.",           "image": "https://placehold.co/400x250/6f42c1/ffffff?text=Creative", "features": ["UI/UX Design", "Photography", "Video Editing"]},
        ],
        about_story="LearnHub was founded in 2019 by tech educators passionate about democratizing quality education. Today 50K+ students learn from our platform.",
        about_mission="To make world-class education accessible to everyone, regardless of location or background.",
        about_values=[
            {"icon": "🌍", "title": "Accessibility",  "desc": "Education for everyone, everywhere."},
            {"icon": "🎓", "title": "Quality",       "desc": "Premium courses from industry experts."},
            {"icon": "🚀", "title": "Practical",     "desc": "Skills that directly apply to real jobs."},
            {"icon": "💪", "title": "Community",     "desc": "Supportive learning community."},
        ],
        team=[
            {"name": "Aryan Kapoor",       "role": "Founder & CEO",              "avatar": "https://placehold.co/200x200/6f42c1/ffffff?text=AK"},
            {"name": "Dr. Neha Verma",     "role": "Lead Instructor - Tech",     "avatar": "https://placehold.co/200x200/5a6268/ffffff?text=NV"},
            {"name": "Ravi Patel",        "role": "Business Course Lead",      "avatar": "https://placehold.co/200x200/ff7043/ffffff?text=RP"},
            {"name": "Shreya Desai",      "role": "Creative Skills Lead",      "avatar": "https://placehold.co/200x200/6f42c1/ffffff?text=SD"},
        ],
        awards=[{"year": "2024", "title": "Best Online Learning Platform", "org": "EdTech Awards India", "icon": "🏆"}, {"year": "2023", "title": "Fastest Growing EdTech", "org": "Tech Startup Awards", "icon": "📈"}],
        milestones=[{"year": "2019", "title": "Launched", "desc": "Started with 10 courses."}, {"year": "2021", "title": "10K Students", "desc": "Reached 10,000 students."}, {"year": "2024", "title": "50K Students", "desc": "Serving 50K+ active learners."}],
        stats=[{"value": "50K+", "label": "Students", "icon": "👥"}, {"value": "500+", "label": "Courses", "icon": "📚"}, {"value": "100+", "label": "Instructors", "icon": "👨‍🏫"}, {"value": "4.7⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Course Quality", "Instructor Expertise", "Learning Experience", "Value for Money", "Overall"],
    ),

    # 14. Testing & QA - Comprehensive Content Testing Template
    make_config(
        name="Content Testing Platform", tagline="Comprehensive UI Testing Solution for Modern Web Applications",
        phone="+1 (555) 987-6543", email="support@contentplatform.io",
        address="123 Innovation Street, Suite 500, Technology Park, San Francisco, CA 94105, United States",
        theme=make_theme("#3b82f6", "#06b6d4", "#8b5cf6", "#f0f9ff", "#1e3a8a", "#0369a1", "#082f49"),
        header_tmpl=2, footer_tmpl=3,
        home_title="Welcome to Content Testing Platform - Comprehensive UI Testing Solution for Modern Web Applications",
        home_sub="Validate your responsive designs with real-world content lengths. This platform provides lengthy text samples in all fields to help you identify layout issues before they reach production.",
        home_features=[
            {"icon": "📝", "title": "Comprehensive Content Testing Framework", "desc": "Our platform allows you to test your UI components with real-world content lengths. Every field contains lengthy text to help identify potential layout breaks, text overflow issues, and responsive design problems across different screen sizes and device types."},
            {"icon": "📊", "title": "Advanced Analytics and Performance Monitoring", "desc": "Track how your layouts perform with different content lengths using our built-in analytics dashboard. Monitor performance metrics, identify bottlenecks, and get actionable insights to improve your application's user experience and overall performance."},
            {"icon": "🎨", "title": "Design System Integration and Customization", "desc": "Seamlessly integrate with popular design systems and component libraries. Customize colors, typography, spacing, and other design tokens to match your brand guidelines while testing with varied content lengths and formats."},
            {"icon": "🔧", "title": "Developer-Friendly Tools and Documentation", "desc": "Access comprehensive documentation, API references, and code examples to get started quickly. Our developer-friendly tools include component previews, interactive playgrounds, and detailed troubleshooting guides for common issues."},
            {"icon": "🚀", "title": "Performance Optimization Utilities", "desc": "Identify and resolve performance bottlenecks with our optimization toolkit. Get recommendations for code splitting, lazy loading, image optimization, and other performance-enhancing techniques to ensure your application loads quickly."},
            {"icon": "🔒", "title": "Security and Compliance Management", "desc": "Built with security best practices and compliance requirements in mind. Our platform ensures your data is protected with encryption, follows GDPR and other regulations, and provides comprehensive audit logging for compliance verification."},
        ],
        home_stats=[{"value": "10,000+", "label": "Active Users Testing Designs"}, {"value": "500+", "label": "Component Variations"}, {"value": "99.9%", "label": "Uptime Guarantee"}, {"value": "24/7", "label": "Expert Support"}],
        services_title="Professional Services - Comprehensive Support for Your Testing Needs",
        services_items=[
            {"icon": "👥", "title": "Design Consultation and Strategy", "desc": "Work with our design experts to develop a comprehensive testing strategy. We analyze your current design system, identify areas for improvement, and provide actionable recommendations to enhance your user experience and component accessibility across all screen sizes and content scenarios.", "image": "https://placehold.co/400x250/3b82f6/ffffff?text=Consultation", "features": ["Strategy Development", "Analysis", "Recommendations"]},
            {"icon": "📚", "title": "Training and Workshop Programs", "desc": "Participate in our comprehensive training programs designed for designers, developers, and product managers. Learn best practices for responsive design, accessibility, performance optimization, and how to effectively use our content testing platform to catch issues early in the development cycle.", "image": "https://placehold.co/400x250/06b6d4/ffffff?text=Training", "features": ["Live Sessions", "Materials", "Certification"]},
            {"icon": "🔍", "title": "Quality Assurance and Testing Services", "desc": "Our QA team performs thorough testing of your designs across multiple devices, browsers, and content scenarios. We create detailed reports highlighting issues, suggest fixes, and provide recommendations for improving overall design quality and user experience consistency.", "image": "https://placehold.co/400x250/8b5cf6/ffffff?text=QA+Services", "features": ["Multi-Device Testing", "Reports", "Recommendations"]},
            {"icon": "🛠️", "title": "Custom Integration and Development", "desc": "Need custom features or integrations? Our development team can build tailored solutions that integrate seamlessly with your existing workflow. From API implementations to custom components, we handle all aspects of technical integration and customization.", "image": "https://placehold.co/400x250/3b82f6/ffffff?text=Integration", "features": ["Custom Features", "API Integration", "Support"]},
        ],
        about_story="Content Testing Platform was founded by a team of passionate designers and developers who recognized a critical gap in the market. We realized that many layout issues and responsive design problems only became apparent when real, lengthy content was introduced into designs. Traditional design tools often focused on static layouts without accounting for variable content lengths. We set out to change that by creating a comprehensive platform specifically designed for testing UI components with real-world content scenarios. Today, we're proud to serve thousands of teams across the globe who trust our platform to catch design issues before they reach production.",
        about_mission="Our mission is to empower designers and developers to create robust, accessible, and beautiful user interfaces that work seamlessly with any content length. We believe that great design is not just about aesthetics, but about functionality and how the interface adapts to real-world data. We're committed to providing tools, resources, and support to help our community build better products that deliver exceptional user experiences.",
        about_values=[
            {"icon": "✨", "title": "Excellence", "desc": "We strive for excellence in everything we do, from our product features to our customer support and comprehensive documentation."},
            {"icon": "🚀", "title": "Innovation", "desc": "We continuously innovate and improve our platform based on user feedback and emerging industry best practices in design and development."},
            {"icon": "🌍", "title": "Accessibility", "desc": "We believe quality design tools should be accessible to everyone, regardless of technical expertise, background, or budget constraints."},
            {"icon": "👥", "title": "Community", "desc": "We foster a vibrant community where users can share knowledge, help each other, and grow together in their design and development journey."},
        ],
        team=[
            {"name": "Sarah Chen", "role": "Founder & CEO", "avatar": "https://placehold.co/200x200/3b82f6/ffffff?text=SC"},
            {"name": "Michael Rodriguez", "role": "VP Product & Design", "avatar": "https://placehold.co/200x200/06b6d4/ffffff?text=MR"},
            {"name": "Dr. Priya Kapoor", "role": "Head of Engineering", "avatar": "https://placehold.co/200x200/8b5cf6/ffffff?text=PK"},
            {"name": "James Mitchell", "role": "Director of Customer Success", "avatar": "https://placehold.co/200x200/3b82f6/ffffff?text=JM"},
        ],
        awards=[{"year": "2024", "title": "Best Design Testing Tool", "org": "Tech Innovation Awards", "icon": "🏆"}, {"year": "2023", "title": "Customer Choice Award", "org": "Design Tools Review", "icon": "⭐"}],
        milestones=[{"year": "2024", "title": "Reached 10,000+ Users", "desc": "Our platform now serves over 10,000 active users worldwide helping them create better designs."}, {"year": "2023", "title": "Launched Advanced Analytics", "desc": "Released comprehensive analytics dashboard for tracking testing metrics and insights."}, {"year": "2022", "title": "Public Launch", "desc": "Officially launched our content testing platform after months of beta testing."}],
        stats=[{"value": "10,000+", "label": "Active Users", "icon": "👥"}, {"value": "500+", "label": "Component Templates", "icon": "🎨"}, {"value": "150+", "label": "Countries", "icon": "🌍"}, {"value": "4.9⭐", "label": "User Rating", "icon": "⭐"}],
        categories=["Feature Requests", "Bug Reports", "Performance Feedback", "UI/UX Suggestions", "Documentation", "General Feedback"],
    ),

    # 15. Cafe & Coffee Shop
    make_config(
        name="Brewing Coffee Cafe", tagline="Artisan Coffee & Cozy Vibes - Your Perfect Third Place",
        phone="+91 94567 12340", email="hello@brewingcoffee.in",
        address="45 Coffee Lane, Bangalore, KA 560042",
        theme=make_theme("#8B4513", "#D2691E", "#F4A460", "#FFF8DC", "#3E2723", "#6D4C41", "#1B0000"),
        header_tmpl=1, footer_tmpl=2,
        home_title="Brewing Coffee Cafe - Premium Artisan Coffee Experience in Bangalore",
        home_sub="Welcome to our cozy corner where premium coffee meets warm hospitality. Discover exceptional brews, pastries, and the perfect atmosphere for work, meetings, or relaxation.",
        home_features=[
            {"icon": "☕", "title": "Specialty Coffee Blends", "desc": "Freshly roasted beans from sustainable farms around the world. Our expert baristas craft each cup with precision and passion, delivering rich flavors and smooth textures in every sip."},
            {"icon": "🥐", "title": "Artisan Bakery Items", "desc": "Handcrafted pastries, croissants, and breads made fresh daily in our in-house bakery by our talented pastry chefs using premium ingredients."},
            {"icon": "🍰", "title": "Desserts & Cakes", "desc": "Indulgent desserts, custom cakes, and sweet treats prepared with love. From classic favorites to innovative creations, we have something for every palate and occasion."},
            {"icon": "🪑", "title": "Comfortable Seating Areas", "desc": "Spacious, well-lit seating with free high-speed WiFi and charging outlets. Perfect for work, study sessions, meetings, or simply relaxing with friends and family."},
            {"icon": "🎵", "title": "Live Music Performances", "desc": "Enjoy live acoustic performances from local artists every weekend. Our curated music selection creates the perfect ambiance throughout the week for relaxation."},
            {"icon": "📱", "title": "Mobile App & Loyalty Program", "desc": "Download our app for exclusive deals, easy ordering, and loyalty rewards. Earn points with every purchase and redeem them for free items and special discounts."},
        ],
        home_stats=[{"value": "2000+", "label": "Happy Customers Daily"}, {"value": "50+", "label": "Coffee Varieties"}, {"value": "8+", "label": "Years in Business"}, {"value": "4.8⭐", "label": "Customer Rating"}],
        services_title="Our Services & Offerings",
        services_items=[
            {"icon": "☕", "title": "Espresso Drinks & Specialty Coffee", "desc": "From classic cappuccinos and lattes to innovative specialty drinks like our signature brown butter oat milk latte. Each beverage is prepared by our trained baristas with the highest quality standards and attention to detail.", "image": "https://placehold.co/400x250/8B4513/ffffff?text=Coffee", "features": ["Espresso Drinks", "Cold Brew", "Specialty Beverages"]},
            {"icon": "🎂", "title": "Cakes & Custom Orders", "desc": "Celebrate special occasions with our custom-designed cakes and desserts. Our pastry team creates beautiful, delicious creations for birthdays, anniversaries, weddings, and corporate events with personalized touches.", "image": "https://placehold.co/400x250/D2691E/ffffff?text=Cakes", "features": ["Custom Cakes", "Event Desserts", "Same-day Orders"]},
            {"icon": "🏢", "title": "Corporate Catering Services", "desc": "Perfect solutions for your office meetings, conferences, and team events. We provide bulk coffee orders, pastry platters, and beverage stations with professional setup and service for your corporate needs.", "image": "https://placehold.co/400x250/F4A460/ffffff?text=Catering", "features": ["Bulk Orders", "Event Setup", "Corporate Packages"]},
            {"icon": "🎓", "title": "Coffee Tasting & Workshops", "desc": "Learn about coffee from bean to cup in our interactive workshops. Our expert instructors teach you about coffee origins, brewing techniques, and flavor profiles. Perfect for coffee enthusiasts and those looking to deepen their appreciation.", "image": "https://placehold.co/400x250/8B4513/ffffff?text=Workshop", "features": ["Tasting Sessions", "Brewing Classes", "Barista Training"]},
        ],
        about_story="Brewing Coffee Cafe was founded in 2016 by coffee enthusiast Rahul Desai with a vision to create a space where people could enjoy premium coffee without the pretense. What started as a small corner shop has grown into a beloved destination for coffee lovers, students, professionals, and families. Our passion for quality coffee and genuine hospitality remains unchanged.",
        about_mission="To be the premier destination for coffee lovers in Bangalore by serving exceptional coffee, fostering meaningful connections, and supporting sustainable coffee farming practices worldwide.",
        about_values=[
            {"icon": "☕", "title": "Quality First", "desc": "We obsess over coffee quality, sourcing, roasting, and brewing methods to deliver the best cup every single time."},
            {"icon": "🌍", "title": "Sustainability", "desc": "Supporting fair trade and sustainable farming practices. We believe in giving back to the communities that grow our coffee."},
            {"icon": "😊", "title": "Customer Care", "desc": "Every customer is welcomed with warmth and genuine care. We remember your name and your favorite order."},
            {"icon": "🎨", "title": "Creativity", "desc": "Constantly innovating with new flavors, brewing methods, and cafe experiences to surprise and delight our community."},
        ],
        team=[
            {"name": "Rahul Desai", "role": "Founder & Head Barista", "avatar": "https://placehold.co/200x200/8B4513/ffffff?text=RD"},
            {"name": "Anita Sharma", "role": "Pastry Chef & Manager", "avatar": "https://placehold.co/200x200/D2691E/ffffff?text=AS"},
            {"name": "Vikram Singh", "role": "Coffee Sourcing Specialist", "avatar": "https://placehold.co/200x200/F4A460/ffffff?text=VS"},
            {"name": "Maya Patel", "role": "Customer Experience Lead", "avatar": "https://placehold.co/200x200/8B4513/ffffff?text=MP"},
        ],
        awards=[{"year": "2024", "title": "Best Cafe in Bangalore", "org": "City Lifestyle Awards", "icon": "🏆"}, {"year": "2023", "title": "Most Loved Coffee Shop", "org": "Bangalore Times", "icon": "💝"}],
        milestones=[{"year": "2016", "title": "Founded", "desc": "Opened our first cozy cafe with a dream of serving great coffee."}, {"year": "2020", "title": "Expanded", "desc": "Opened second location and launched mobile app and loyalty program."}, {"year": "2024", "title": "1000 Daily Customers", "desc": "Celebrating thousands of happy customers and growing community."}],
        stats=[{"value": "2000+", "label": "Daily Customers", "icon": "👥"}, {"value": "50+", "label": "Coffee Types", "icon": "☕"}, {"value": "40+", "label": "Pastry Items", "icon": "🥐"}, {"value": "4.8⭐", "label": "Ratings", "icon": "⭐"}],
        categories=["Coffee Quality", "Service", "Ambiance", "Food Quality", "Value for Money"],
    ),

    # 16. Consulting & Advisory
    make_config(
        name="Strategic Minds Consulting", tagline="Transform Your Business With Data-Driven Strategic Solutions",
        phone="+91 96543 21098", email="info@strategicminds.co.in",
        address="Tower B, Business Plaza, 78 Cyber City, Bangalore, KA 560015",
        theme=make_theme("#1a365d", "#2d3748", "#ed8936", "#f7fafc", "#0f1419", "#2d3748", "#000000"),
        header_tmpl=3, footer_tmpl=1,
        home_title="Strategic Minds Consulting - Enterprise Transformation & Business Growth Solutions",
        home_sub="Partner with leading consultants to drive strategic transformation, operational excellence, and sustainable growth. We combine deep industry expertise with cutting-edge analytics and proven methodologies.",
        home_features=[
            {"icon": "📊", "title": "Business Strategy Consulting", "desc": "Develop comprehensive business strategies aligned with your vision and market opportunities. Our consultants conduct detailed market analysis, competitive positioning studies, and create actionable roadmaps for sustainable growth and market leadership."},
            {"icon": "💼", "title": "Organizational Transformation", "desc": "Navigate complex organizational changes with our expert guidance. From restructuring to culture change, we help implement new systems, processes, and structures that drive efficiency and employee engagement throughout your organization."},
            {"icon": "📈", "title": "Financial Performance Optimization", "desc": "Improve profitability and financial metrics through our comprehensive cost optimization and revenue enhancement programs. We identify inefficiencies, streamline operations, and unlock new revenue opportunities using data-driven insights."},
            {"icon": "🔧", "title": "Operations & Process Improvement", "desc": "Enhance operational efficiency through lean management, process automation, and supply chain optimization. Our methodologies reduce waste, improve quality, and deliver measurable improvements to your bottom line."},
            {"icon": "👥", "title": "Change Management & Training", "desc": "Successfully implement organizational changes with our comprehensive change management and training programs. We ensure employee adoption, minimize resistance, and build organizational capability for sustained success."},
            {"icon": "🎯", "title": "Digital Transformation Strategy", "desc": "Leverage digital technologies to reimagine your business model, customer experience, and operational processes. From cloud migration to AI implementation, we guide your digital journey with strategic vision and technical expertise."},
        ],
        home_stats=[{"value": "500+", "label": "Projects Completed"}, {"value": "250+", "label": "Fortune 500 Clients"}, {"value": "20+", "label": "Years of Expertise"}, {"value": "4.9⭐", "label": "Client Satisfaction"}],
        services_title="Our Consulting Services & Solutions",
        services_items=[
            {"icon": "🏢", "title": "Strategic Business Planning", "desc": "Comprehensive strategic planning services including market analysis, competitive positioning, growth strategy development, and performance measurement frameworks. We help you navigate market complexities and identify sustainable competitive advantages.", "image": "https://placehold.co/400x250/1a365d/ffffff?text=Strategy", "features": ["Market Analysis", "Growth Planning", "Competitive Strategy"]},
            {"icon": "⚙️", "title": "Operational Excellence Programs", "desc": "Transform operations through lean management, process optimization, and performance improvement initiatives. Our programs deliver measurable results including cost reduction, quality improvements, and enhanced customer satisfaction metrics.", "image": "https://placehold.co/400x250/2d3748/ffffff?text=Operations", "features": ["Lean Management", "Process Optimization", "Quality Improvement"]},
            {"icon": "💻", "title": "Digital & IT Strategy", "desc": "Navigate the digital landscape with our comprehensive IT and digital transformation strategies. We help you select, implement, and maximize technologies including cloud, AI, and automation for competitive advantage.", "image": "https://placehold.co/400x250/ed8936/ffffff?text=Digital", "features": ["Cloud Strategy", "AI Implementation", "Digital Roadmap"]},
            {"icon": "👔", "title": "Executive Coaching & Leadership Development", "desc": "Develop high-potential leaders through personalized coaching and executive development programs. Our experienced coaches work with C-suite executives to enhance leadership effectiveness and organizational impact.", "image": "https://placehold.co/400x250/1a365d/ffffff?text=Leadership", "features": ["Executive Coaching", "Team Development", "Leadership Skills"]},
        ],
        about_story="Strategic Minds Consulting was founded in 2004 by a group of seasoned management consultants with diverse backgrounds from leading global consulting firms. Over two decades, we have built a reputation for delivering transformational results for Fortune 500 companies and mid-market leaders. Our deep expertise, collaborative approach, and unwavering commitment to client success define everything we do.",
        about_mission="To empower organizations to achieve their strategic objectives through intelligent consulting, transformational thinking, and exceptional execution of complex business initiatives.",
        about_values=[
            {"icon": "🎯", "title": "Excellence", "desc": "We maintain the highest standards of professionalism, integrity, and quality in all our consulting engagements and client interactions."},
            {"icon": "💡", "title": "Innovation", "desc": "We combine industry best practices with innovative thinking to deliver breakthrough solutions that drive competitive advantage and sustainable growth."},
            {"icon": "🤝", "title": "Partnership", "desc": "We work as true partners with our clients, understanding their business deeply and being invested in their long-term success."},
            {"icon": "📊", "title": "Data-Driven", "desc": "All recommendations are grounded in rigorous analysis, data insights, and proven methodologies ensuring measurable, lasting impact."},
        ],
        team=[
            {"name": "Dr. Arvind Kumar", "role": "Managing Director & Principal Consultant", "avatar": "https://placehold.co/200x200/1a365d/ffffff?text=AK"},
            {"name": "Shreya Deshmukh", "role": "Senior Strategy Consultant", "avatar": "https://placehold.co/200x200/2d3748/ffffff?text=SD"},
            {"name": "Rajesh Nair", "role": "Operations Excellence Lead", "avatar": "https://placehold.co/200x200/ed8936/ffffff?text=RN"},
            {"name": "Priya Singh", "role": "Digital Transformation Specialist", "avatar": "https://placehold.co/200x200/1a365d/ffffff?text=PS"},
        ],
        awards=[{"year": "2024", "title": "Best Management Consulting Firm", "org": "India Business Excellence Awards", "icon": "🏆"}, {"year": "2023", "title": "Top 10 Consulting Firms", "org": "Business India", "icon": "📊"}],
        milestones=[{"year": "2004", "title": "Founded", "desc": "Established with vision to transform Indian business landscape through strategic consulting."}, {"year": "2015", "title": "500 Projects", "desc": "Completed 500+ successful consulting engagements across sectors."}, {"year": "2024", "title": "Global Expansion", "desc": "Expanded to Southeast Asia and served 250+ Fortune 500 companies."}],
        stats=[{"value": "500+", "label": "Projects Delivered", "icon": "📊"}, {"value": "250+", "label": "Fortune 500 Clients", "icon": "🏢"}, {"value": "20+", "label": "Years Expertise", "icon": "📚"}, {"value": "4.9⭐", "label": "Client Rating", "icon": "⭐"}],
        categories=["Consultant Expertise", "Project Delivery", "Strategic Thinking", "ROI Achievement", "Overall Satisfaction"],
    ),

    # 17. Hotel & Resort
    make_config(
        name="Serenity Resort & Wellness Spa", tagline="Luxury Escape Where Nature Meets Indulgence & Wellness",
        phone="+91 98765 54321", email="reservations@serenityresort.in",
        address="Hillside Valley, Kodaikanal, Tamil Nadu 624104",
        theme=make_theme("#10b981", "#059669", "#fbbf24", "#ecfdf5", "#064e3b", "#047857", "#021f12"),
        header_tmpl=2, footer_tmpl=3,
        home_title="Serenity Resort & Wellness Spa - Luxury Retreat in the Heart of Nature",
        home_sub="Experience ultimate relaxation and rejuvenation at our award-winning resort nestled in pristine natural surroundings with world-class amenities, spa treatments, and personalized wellness programs.",
        home_features=[
            {"icon": "🏨", "title": "Luxury Accommodations", "desc": "Spacious rooms and suites with panoramic views, premium furnishings, and modern amenities. Each room is designed to provide maximum comfort with private balconies, high-end toiletries, and personalized room service."},
            {"icon": "💆", "title": "Rejuvenating Spa & Wellness", "desc": "Comprehensive spa services including Ayurveda treatments, traditional massages, facials, and wellness therapies. Our certified therapists use natural ingredients and ancient techniques to restore your body and mind."},
            {"icon": "🍽️", "title": "Gourmet Dining Experiences", "desc": "Multiple dining venues serving international and local cuisine prepared by award-winning chefs using organic, locally-sourced ingredients. Enjoy fine dining, casual cafes, and private dining experiences."},
            {"icon": "🏊", "title": "Recreation & Activities", "desc": "Swimming pool, yoga sessions, nature walks, adventure activities, and cultural programs. Stay active or unwind with activities tailored to all age groups and fitness levels in our pristine natural setting."},
            {"icon": "🏔️", "title": "Natural Surroundings & Adventure", "desc": "Trek through scenic trails, explore waterfalls, and immerse yourself in nature. Our location offers perfect opportunities for adventure sports, photography, and peaceful nature experiences."},
            {"icon": "💼", "title": "Meetings & Events", "desc": "State-of-the-art conference facilities for corporate meetings, weddings, and special celebrations. Our experienced team handles every detail from planning to execution ensuring memorable events."},
        ],
        home_stats=[{"value": "150+", "label": "Rooms & Suites"}, {"value": "50+", "label": "Spa Treatments"}, {"value": "15+", "label": "Years Excellence"}, {"value": "4.9⭐", "label": "Guest Rating"}],
        services_title="Premium Services & Experiences",
        services_items=[
            {"icon": "🛎️", "title": "Concierge & Guest Services", "desc": "Dedicated concierge service to arrange activities, transportation, dining reservations, and special experiences. Our team goes above and beyond to make your stay unforgettable and hassle-free.", "image": "https://placehold.co/400x250/10b981/ffffff?text=Concierge", "features": ["Activity Planning", "Transportation", "Reservations"]},
            {"icon": "💑", "title": "Romantic Getaway Packages", "desc": "Specially curated romantic packages including couple spa treatments, candlelit dinners, and private experiences. Perfect for honeymoons, anniversaries, and romantic celebrations in paradise.", "image": "https://placehold.co/400x250/059669/ffffff?text=Romantic", "features": ["Couple Packages", "Private Dining", "Special Decor"]},
            {"icon": "🎯", "title": "Corporate Wellness Programs", "desc": "Tailored wellness retreats for corporate groups including team-building activities, wellness workshops, healthy cuisine, and stress management programs designed to rejuvenate and re-energize teams.", "image": "https://placehold.co/400x250/fbbf24/ffffff?text=Corporate", "features": ["Team Retreats", "Wellness Programs", "Training Sessions"]},
            {"icon": "👨‍👩‍👧‍👦", "title": "Family Holiday Packages", "desc": "Fun-filled family packages with activities for all ages, kids clubs, adventure sports, and family dining experiences. Create lasting memories in our beautiful natural setting with excellent facilities.", "image": "https://placehold.co/400x250/10b981/ffffff?text=Family", "features": ["Kids Activities", "Family Dining", "Adventure Sports"]},
        ],
        about_story="Serenity Resort & Wellness Spa was envisioned as a sanctuary of tranquility where guests could escape the chaos of urban life and reconnect with nature and themselves. Founded in 2009, we have consistently delivered exceptional hospitality and wellness experiences, earning recognition as one of India's premier wellness destinations.",
        about_mission="To provide a transformative wellness and hospitality experience that nurtures the mind, body, and soul while respecting and preserving our natural environment.",
        about_values=[
            {"icon": "🌿", "title": "Sustainability", "desc": "Committed to eco-friendly practices and preserving the natural beauty that makes our location special for future generations."},
            {"icon": "😊", "title": "Hospitality", "desc": "Every guest is treated like family with warmth, care, and personalized attention ensuring unforgettable experiences."},
            {"icon": "💚", "title": "Wellness", "desc": "Holistic wellness approach integrating physical, mental, and spiritual rejuvenation through authentic practices."},
            {"icon": "🎭", "title": "Experience", "desc": "Creating memorable experiences that go beyond accommodation, offering transformative moments and meaningful connections."},
        ],
        team=[
            {"name": "Sanjay Kumar", "role": "General Manager", "avatar": "https://placehold.co/200x200/10b981/ffffff?text=SK"},
            {"name": "Dr. Anamika Sharma", "role": "Wellness Director", "avatar": "https://placehold.co/200x200/059669/ffffff?text=AS"},
            {"name": "Chef Vikram Desai", "role": "Executive Chef", "avatar": "https://placehold.co/200x200/fbbf24/ffffff?text=VD"},
            {"name": "Anjali Nair", "role": "Guest Experience Manager", "avatar": "https://placehold.co/200x200/10b981/ffffff?text=AN"},
        ],
        awards=[{"year": "2024", "title": "Best Wellness Resort", "org": "India Travel Awards", "icon": "🏆"}, {"year": "2023", "title": "Luxury Resort of the Year", "org": "Travel & Leisure", "icon": "💎"}],
        milestones=[{"year": "2009", "title": "Opened", "desc": "Established as a luxury wellness destination with vision of holistic healing."}, {"year": "2017", "title": "Expanded", "desc": "Added spa facilities and adventure activities expanding service offerings significantly."}, {"year": "2024", "title": "20,000+ Guests", "desc": "Welcomed over 20,000 guests who found rejuvenation and peace at Serenity."}],
        stats=[{"value": "150+", "label": "Rooms", "icon": "🏨"}, {"value": "50+", "label": "Spa Services", "icon": "💆"}, {"value": "5⭐", "label": "Star Rating", "icon": "⭐"}, {"value": "98%", "label": "Guest Satisfaction", "icon": "😊"}],
        categories=["Accommodation Quality", "Spa Services", "Food & Beverage", "Staff Hospitality", "Overall Experience"],
    ),

    # 18. Digital Marketing Agency
    make_config(
        name="Digital Pulse Marketing Agency", tagline="Data-Driven Digital Solutions That Drive Real Business Results",
        phone="+91 95432 10987", email="hello@digitalpulse.in",
        address="Creative Hub, 5th Floor, Marketing Tower, Mumbai, MH 400020",
        theme=make_theme("#ec4899", "#f43f5e", "#a855f7", "#fce7f3", "#831843", "#be185d", "#3f0f12"),
        header_tmpl=1, footer_tmpl=2,
        home_title="Digital Pulse Marketing Agency - Comprehensive Digital Marketing Solutions for Growth",
        home_sub="Transform your digital presence with our comprehensive marketing solutions. From SEO and content marketing to social media and paid advertising, we drive measurable results and sustainable growth.",
        home_features=[
            {"icon": "📱", "title": "Social Media Marketing", "desc": "Strategic social media campaigns across all platforms designed to increase engagement, build community, and drive conversions. Our creative team develops content that resonates with your target audience."},
            {"icon": "🔍", "title": "Search Engine Optimization", "desc": "Comprehensive SEO strategies to improve your online visibility and organic rankings. We conduct detailed keyword research, optimize on-page and off-page factors, and implement technical SEO for sustainable growth."},
            {"icon": "✉️", "title": "Email Marketing Campaigns", "desc": "Personalized email marketing campaigns that nurture leads and drive customer loyalty. We design beautiful templates, segment audiences, and optimize for maximum engagement and conversion."},
            {"icon": "📊", "title": "Analytics & Reporting", "desc": "Advanced analytics and detailed reporting to track campaign performance and ROI. We provide actionable insights that inform strategy and drive continuous optimization."},
            {"icon": "🎬", "title": "Video Content Creation", "desc": "High-quality video content production including commercials, explainer videos, testimonials, and social media videos. Our creative team tells your brand story in compelling and engaging ways."},
            {"icon": "💰", "title": "Paid Advertising Campaigns", "desc": "Strategic PPC campaigns across Google Ads, Facebook, Instagram, and LinkedIn designed to maximize ROI. We handle keyword research, ad creation, bidding strategy, and continuous optimization."},
        ],
        home_stats=[{"value": "500+", "label": "Campaigns Executed"}, {"value": "250+", "label": "Clients Served"}, {"value": "10+", "label": "Years Experience"}, {"value": "4.8⭐", "label": "Client Rating"}],
        services_title="Our Digital Marketing Services",
        services_items=[
            {"icon": "🌐", "title": "Website Design & Development", "desc": "Custom website design and development services creating stunning, high-converting websites optimized for user experience and search engines. We build responsive sites that work perfectly across all devices.", "image": "https://placehold.co/400x250/ec4899/ffffff?text=Web+Design", "features": ["Responsive Design", "SEO Optimized", "Fast Loading"]},
            {"icon": "📈", "title": "Digital Strategy & Consulting", "desc": "Comprehensive digital marketing strategy development aligned with your business goals. We analyze your current position, competitive landscape, and develop actionable roadmaps for growth.", "image": "https://placehold.co/400x250/f43f5e/ffffff?text=Strategy", "features": ["Market Analysis", "Roadmap Development", "Competitive Insight"]},
            {"icon": "🎨", "title": "Brand Design & Content", "desc": "Creative brand design, logo development, and high-quality content creation. Our designers and copywriters work together to build cohesive brand identity and compelling brand messaging.", "image": "https://placehold.co/400x250/a855f7/ffffff?text=Branding", "features": ["Logo Design", "Brand Guidelines", "Content Creation"]},
            {"icon": "🚀", "title": "Growth Hacking & Optimization", "desc": "Innovative growth hacking strategies and continuous optimization to accelerate business growth. We identify growth opportunities, test strategies rapidly, and scale what works.", "image": "https://placehold.co/400x250/ec4899/ffffff?text=Growth", "features": ["A/B Testing", "Conversion Optimization", "Growth Strategies"]},
        ],
        about_story="Digital Pulse Marketing Agency was founded in 2014 by a group of digital marketing experts who believed in data-driven marketing and measurable results. Starting from a small team, we have grown to become a leading full-service digital marketing agency serving diverse clients from startups to established enterprises.",
        about_mission="To empower businesses with digital marketing excellence, helping them achieve their growth objectives through strategic, creative, and data-driven solutions.",
        about_values=[
            {"icon": "📊", "title": "Data-Driven", "desc": "All strategies backed by comprehensive data analysis and insights ensuring every decision is optimized for results."},
            {"icon": "💡", "title": "Innovation", "desc": "We stay ahead of digital trends, testing new strategies and tools to deliver cutting-edge solutions for our clients."},
            {"icon": "🎯", "title": "Results-Focused", "desc": "We measure success by your business results, not just metrics, and are committed to delivering measurable ROI."},
            {"icon": "🤝", "title": "Partnership", "desc": "We work as true partners, understanding your business deeply and being invested in your long-term success."},
        ],
        team=[
            {"name": "Aditya Patel", "role": "Founder & Strategy Head", "avatar": "https://placehold.co/200x200/ec4899/ffffff?text=AP"},
            {"name": "Neha Sharma", "role": "Content & Creative Director", "avatar": "https://placehold.co/200x200/f43f5e/ffffff?text=NS"},
            {"name": "Rohan Singh", "role": "SEO & SEM Specialist", "avatar": "https://placehold.co/200x200/a855f7/ffffff?text=RS"},
            {"name": "Priya Verma", "role": "Social Media Manager", "avatar": "https://placehold.co/200x200/ec4899/ffffff?text=PV"},
        ],
        awards=[{"year": "2024", "title": "Best Digital Marketing Agency", "org": "Indian Marketing Excellence Awards", "icon": "🏆"}, {"year": "2023", "title": "Top Digital Agency", "org": "Forbes India", "icon": "📈"}],
        milestones=[{"year": "2014", "title": "Founded", "desc": "Started with passion for digital marketing and commitment to results."}, {"year": "2019", "title": "500 Campaigns", "desc": "Completed 500+ successful marketing campaigns with measurable results."}, {"year": "2024", "title": "250 Clients", "desc": "Serving 250+ satisfied clients across industries and geographies."}],
        stats=[{"value": "500+", "label": "Campaigns", "icon": "📊"}, {"value": "250+", "label": "Clients", "icon": "🏢"}, {"value": "10+", "label": "Years", "icon": "📅"}, {"value": "4.8⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Campaign Effectiveness", "Team Expertise", "Communication", "ROI Delivered", "Customer Service"],
    ),

    # 19. Photography Studio
    make_config(
        name="Lens & Light Photography Studio", tagline="Professional Photography Services - Capturing Your Most Precious Moments",
        phone="+91 94321 09876", email="bookings@lensandlight.in",
        address="Artist Quarter, 3rd Floor, Creative Building, New Delhi, DL 110001",
        theme=make_theme("#1f2937", "#374151", "#f59e0b", "#f9fafb", "#111827", "#4b5563", "#030712"),
        header_tmpl=3, footer_tmpl=1,
        home_title="Lens & Light Photography Studio - Professional Photography Services for Every Occasion",
        home_sub="Capture life's precious moments with our award-winning photography team. From weddings and portraits to commercial photography, we deliver stunning images that tell your unique story.",
        home_features=[
            {"icon": "💍", "title": "Wedding Photography", "desc": "Comprehensive wedding coverage capturing every emotional moment from pre-wedding preparations to grand celebrations. Our artistic approach combines candid moments with stunning formal portraits creating timeless memories."},
            {"icon": "👨‍👩‍👧", "title": "Family Portrait Sessions", "desc": "Professional family portrait photography in studio or outdoor settings. We create relaxed, natural environments where genuine emotions shine through resulting in beautiful, cherished portraits."},
            {"icon": "👶", "title": "Newborn & Child Photography", "desc": "Specialized newborn and child photography services with patience, creativity, and attention to detail. We create safe, comfortable environments for babies and children resulting in adorable, timeless images."},
            {"icon": "📸", "title": "Event & Celebration Photography", "desc": "Professional coverage of corporate events, birthday parties, anniversaries, and celebrations. We capture the excitement, joy, and important moments ensuring nothing is missed."},
            {"icon": "🏢", "title": "Commercial & Product Photography", "desc": "High-quality commercial photography for businesses including product photography, corporate headshots, and brand imagery. We understand commercial requirements and deliver images that support your business goals."},
            {"icon": "✏️", "title": "Pre-Wedding Shoot", "desc": "Creative and romantic pre-wedding photography sessions capturing the couple's chemistry and love story. We scout beautiful locations and create artistic, cinematic images for lasting memories."},
        ],
        home_stats=[{"value": "1000+", "label": "Weddings Covered"}, {"value": "10,000+", "label": "Happy Clients"}, {"value": "12+", "label": "Years Experience"}, {"value": "4.9⭐", "label": "Client Rating"}],
        services_title="Photography Services & Packages",
        services_items=[
            {"icon": "💍", "title": "Complete Wedding Package", "desc": "Full-day wedding coverage including pre-wedding, ceremony, reception, and post-wedding events. High-quality edited photos delivered in digital and print formats with album options.", "image": "https://placehold.co/400x250/1f2937/ffffff?text=Wedding", "features": ["Full Day Coverage", "Edited Photos", "Albums"]},
            {"icon": "👨‍👩‍👧", "title": "Portrait Sessions", "desc": "Professional portrait sessions for families, individuals, and groups in studio or outdoor locations. Includes styling consultation, multiple outfit changes, and beautifully retouched photographs.", "image": "https://placehold.co/400x250/374151/ffffff?text=Portraits", "features": ["Multiple Outfits", "Retouching", "Digital & Print"]},
            {"icon": "🎬", "title": "Cinematic Video Filming", "desc": "Professional wedding and event videography creating cinematic stories of your special moments. We use professional equipment and editing to produce high-quality highlight reels and full-length films.", "image": "https://placehold.co/400x250/f59e0b/ffffff?text=Video", "features": ["Cinematic Style", "Professional Editing", "Drone Footage"]},
            {"icon": "🎨", "title": "Photography Training Workshops", "desc": "Learn professional photography techniques through our hands-on workshops and one-on-one training sessions. Suitable for beginners to intermediate photographers wanting to improve their skills.", "image": "https://placehold.co/400x250/1f2937/ffffff?text=Workshop", "features": ["Live Sessions", "Hands-on Training", "Portfolio Building"]},
        ],
        about_story="Lens & Light Photography Studio was established in 2012 by passionate photographer Vikram Kapoor with a vision to preserve life's most precious moments through exceptional photography. Over the years, we have built a reputation for excellence, creativity, and genuine care for our clients' memories.",
        about_mission="To preserve and celebrate life's most precious moments through exceptional photography that tells authentic stories and creates lasting memories for generations to come.",
        about_values=[
            {"icon": "❤️", "title": "Passion", "desc": "We genuinely love what we do and it shows in every photograph. Your moments matter to us as much as they matter to you."},
            {"icon": "🎨", "title": "Creativity", "desc": "We blend technical expertise with artistic vision to create unique, beautiful images that reflect your personality and story."},
            {"icon": "⏰", "title": "Reliability", "desc": "Punctuality, professionalism, and accountability in every engagement ensuring smooth experiences and timely delivery."},
            {"icon": "🤝", "title": "Connection", "desc": "We build genuine relationships with clients, understanding their vision and delivering beyond expectations."},
        ],
        team=[
            {"name": "Vikram Kapoor", "role": "Lead Photographer & Founder", "avatar": "https://placehold.co/200x200/1f2937/ffffff?text=VK"},
            {"name": "Anjali Sharma", "role": "Senior Photographer", "avatar": "https://placehold.co/200x200/374151/ffffff?text=AS"},
            {"name": "Arjun Desai", "role": "Videographer & Editor", "avatar": "https://placehold.co/200x200/f59e0b/ffffff?text=AD"},
            {"name": "Maya Nair", "role": "Photo Editor & Studio Manager", "avatar": "https://placehold.co/200x200/1f2937/ffffff?text=MN"},
        ],
        awards=[{"year": "2024", "title": "Best Wedding Photographer", "org": "Indian Photography Awards", "icon": "🏆"}, {"year": "2023", "title": "Most Creative Photography Studio", "org": "Delhi Times", "icon": "🎨"}],
        milestones=[{"year": "2012", "title": "Founded", "desc": "Established studio with vision to preserve precious memories through exceptional photography."}, {"year": "2018", "title": "1000 Weddings", "desc": "Celebrated milestone of photographing 1000 weddings and creating 10,000+ happy couples."}, {"year": "2024", "title": "Awards & Recognition", "desc": "Recognized as leading photography studio with multiple awards and features in major publications."}],
        stats=[{"value": "1000+", "label": "Weddings", "icon": "💍"}, {"value": "10,000+", "label": "Happy Clients", "icon": "😊"}, {"value": "12+", "label": "Years", "icon": "📅"}, {"value": "4.9⭐", "label": "Rating", "icon": "⭐"}],
        categories=["Photo Quality", "Videography", "Professionalism", "Creativity", "Customer Satisfaction"],
    ),

    # 20. Luxury Hotel & Resort
    make_config(
        name="Luxe Haven Hotels & Resorts", tagline="Experience Unparalleled Luxury and World-Class Hospitality",
        phone="+1 (555) 555-0123", email="reservations@luxehaven.com",
        address="Beachfront Avenue, Suite 1000, Luxury Island Resort, Paradise City 90210, USA",
        theme=make_theme("#d4af37", "#8b7355", "#ffd700", "#1a1612", "#f5f5dc", "#8b6914", "#0a0a08"),
        header_tmpl=2, footer_tmpl=3,
        home_title="Luxe Haven Hotels & Resorts - Your Ultimate Destination for Luxury Travel and World-Class Amenities",
        home_sub="Experience the pinnacle of luxury hospitality at our prestigious international resorts. From stunning oceanfront suites to personalized concierge services, discover an unforgetable escape.",
        home_features=[
            {"icon": "🏨", "title": "Luxury Suite Accommodations", "desc": "Exquisitely designed suites with panoramic views, premium bedding, marble bathrooms with heated floors, private balconies, and state-of-the-art technology systems for maximum comfort."},
            {"icon": "🍽️", "title": "Michelin-Starred Dining", "desc": "Award-winning restaurants featuring international and local cuisine prepared by celebrity chefs using premium organic ingredients and innovative culinary techniques."},
            {"icon": "🏊", "title": "World-Class Spa & Wellness", "desc": "Holistic wellness center offering treatments from around the world, yoga sessions, fitness facilities, personal training, and nutrition counseling for complete rejuvenation."},
            {"icon": "🌴", "title": "Beach & Water Activities", "desc": "Private beach access with water sports, diving, sailing, and snorkeling. Experienced instructors ensure safety and maximum enjoyment of aquatic adventures."},
            {"icon": "👔", "title": "Personalized Concierge Service", "desc": "24/7 dedicated concierge team arranges anything from helicopter tours to private jet charters, yacht rentals, and exclusive access to premium events."},
            {"icon": "💼", "title": "Conference & Event Venues", "desc": "State-of-the-art meeting facilities with high-tech presentation equipment, dedicated event planners, and catering services for corporate meetings and celebrations."},
        ],
        home_stats=[{"value": "15+", "label": "International Locations"}, {"value": "500+", "label": "Luxury Rooms"}, {"value": "50+", "label": "Years Legacy"}, {"value": "5⭐", "label": "Michelin Rating"}],
        services_title="Exclusive Services & Premium Experiences",
        services_items=[
            {"icon": "✈️", "title": "Luxury Travel Arrangements", "desc": "Complete travel coordination including flights, transportation, visa assistance, travel insurance, and customized itineraries tailored to your preferences and interests.", "image": "https://placehold.co/400x250/d4af37/ffffff?text=Travel", "features": ["Private Flights", "Ground Transport", "Travel Insurance"]},
            {"icon": "💒", "title": "Destination Wedding Planning", "desc": "Bespoke wedding services including venue selection, catering, entertainment, floral design, and photography to create your dream destination wedding experience.", "image": "https://placehold.co/400x250/8b7355/ffffff?text=Weddings", "features": ["Venue Selection", "Catering", "Entertainment"]},
            {"icon": "🎭", "title": "Entertainment & Events", "desc": "Exclusive entertainment packages including live performances, private concerts, cultural shows, and curated experiences for unforgettable celebrations and memories.", "image": "https://placehold.co/400x250/ffd700/ffffff?text=Events", "features": ["Live Music", "Shows", "Private Parties"]},
            {"icon": "🛥️", "title": "Yacht & Adventure Charters", "desc": "Private yacht charters, island hopping expeditions, helicopter tours, and adventure activities with expert guides ensuring safety and ultimate luxury throughout.", "image": "https://placehold.co/400x250/d4af37/ffffff?text=Adventure", "features": ["Yacht Charter", "Island Tours", "Helicopter Rides"]},
        ],
        about_story="Luxe Haven Hotels & Resorts was founded in 1975 by renowned hospitality visionary Marcus Sterling with a commitment to delivering unparalleled luxury experiences. Over nearly five decades, we've established ourselves as the premier destination for discerning travelers seeking sophistication, comfort, and world-class service across our international properties.",
        about_mission="To create transformative luxury travel experiences that exceed expectations, foster meaningful connections with our guests, and set the global standard for premium hospitality and personalized service.",
        about_values=[
            {"icon": "✨", "title": "Excellence", "desc": "Unwavering commitment to delivering excellence in every aspect of our operations, from room design to staff training and guest service."},
            {"icon": "🤝", "title": "Hospitality", "desc": "Genuine warmth and personal attention that makes every guest feel valued, respected, and truly welcome throughout their stay."},
            {"icon": "🌍", "title": "Sustainability", "desc": "Environmental responsibility and community engagement ensuring our resorts positively contribute to local economies and ecosystems."},
            {"icon": "💎", "title": "Luxury", "desc": "Commitment to providing the finest amenities, accommodations, and experiences that define true luxury hospitality and elegance."},
        ],
        team=[
            {"name": "Marcus Sterling", "role": "Founder & Chairman", "avatar": "https://placehold.co/200x200/d4af37/ffffff?text=MS"},
            {"name": "Isabelle Laurent", "role": "Chief Operations Officer", "avatar": "https://placehold.co/200x200/8b7355/ffffff?text=IL"},
            {"name": "Dr. Antoine Beaumont", "role": "Director of Culinary Excellence", "avatar": "https://placehold.co/200x200/ffd700/ffffff?text=AB"},
            {"name": "Sophia Rossi", "role": "VP Guest Experience", "avatar": "https://placehold.co/200x200/d4af37/ffffff?text=SR"},
        ],
        awards=[{"year": "2024", "title": "Best Luxury Resort Brand", "org": "International Travel Awards", "icon": "🏆"}, {"year": "2023", "title": "Five-Star Resort Rating", "org": "Luxury Hotel Guide", "icon": "⭐⭐⭐⭐⭐"}],
        milestones=[{"year": "1975", "title": "Founded", "desc": "Established first luxury resort with vision for excellence and personalized service."}, {"year": "2000", "title": "15 Properties", "desc": "Expanded to 15 international locations across continents."}, {"year": "2024", "title": "Leading Global Brand", "desc": "Recognized as world's most prestigious luxury resort brand with millions of satisfied guests."}],
        stats=[{"value": "15+", "label": "Global Locations", "icon": "🌍"}, {"value": "5000+", "label": "Staff Members", "icon": "👥"}, {"value": "5⭐", "label": "Star Rating", "icon": "⭐"}, {"value": "98%", "label": "Guest Satisfaction", "icon": "😊"}],
        categories=["Accommodations", "Dining Experience", "Service Quality", "Amenities", "Value for Money"],
    ),
]

# ── Seed ──────────────────────────────────────────────────────────────────────
def run():
    print(f"\n📦 Connecting to MongoDB: {DB_NAME}")
    print(f"   Collections: {db.list_collection_names()}\n")

    # 1. Admin user (with role and contact info)
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    if not db.admins.find_one({"username": username}):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        # Super admin gets all pages
        all_pages = ["dashboard", "domains", "users", "templates", "blog", "contacts", "feedback", "settings", "reports", "websitePreview", "adminManagement", "adminContact"]
        db.admins.insert_one({
            "username": username,
            "password_hash": hashed,
            "email": "admin@yourdomain.com",
            "phone": "+1 (555) 000-0000",
            "role": "super_admin",
            "created_by_id": None,
            "page_permissions": all_pages,
            "created_at": NOW,
            "updated_at": NOW,
        })
        print(f"✅ Admin created: {username} / {password} (role: super_admin)")
        print(f"   Pages: {', '.join(all_pages)}")
    else:
        print(f"⏭️  Admin already exists: {username}")

    # 1b. Initialize settings with admin contact
    if not db.settings.find_one({}):
        db.settings.insert_one({
            "admin_contact": {
                "email": "admin@yourdomain.com",
                "phone": "+1 (555) 000-0000",
                "social_media": {
                    "facebook": "",
                    "twitter": "",
                    "instagram": "",
                    "linkedin": ""
                }
            },
            "updated_at": NOW,
        })
        print(f"✅ Settings initialized with admin contact")
    else:
        # Ensure admin_contact field exists
        db.settings.update_one({}, {
            "$setOnInsert": {
                "admin_contact": {
                    "email": "admin@yourdomain.com",
                    "phone": "+1 (555) 000-0000",
                    "social_media": {
                        "facebook": "",
                        "twitter": "",
                        "instagram": "",
                        "linkedin": ""
                    }
                }
            }
        }, upsert=False)

    # 2. Demo user
    demo_user = db.users.find_one({"email": "demo@dynamicwebsites.in"})
    if not demo_user:
        demo_user = {
            "name": "Demo Business Owner",
            "email": "demo@dynamicwebsites.in",
            "phone": "+91 98765 00001",
            "company": "Demo Company",
            "domain": "localhost",
            "created_at": NOW,
        }
        result = db.users.insert_one(demo_user)
        demo_user["_id"] = result.inserted_id
        print(f"✅ Demo user created: {demo_user['email']}")
    else:
        print(f"⏭️  Demo user exists: {demo_user['email']}")

    # 3. Insert all 19 templates
    template_ids = []
    for tmpl_data in TEMPLATES:
        name = tmpl_data["siteId"].replace("_", " ").title()
        existing = db.templates.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
        if existing:
            template_ids.append(existing["_id"])
            print(f"⏭️  Template exists: {name}")
        else:
            category_map = {
                "dream_events": "Events & Celebrations",
                "freshmart_supermarket": "Retail Stores",
                "digiprint_solutions": "Printing & Digital Services",
                "spice_garden_restaurant": "Food & Beverage",
                "glamour_beauty_salon": "Beauty & Wellness",
                "bright_future_academy": "Education & Training",
                "techvision_it_solutions": "IT & Professional Services",
                "quickfix_home_services": "Home & Local Services",
                "lifecare_hospital_and_clinic": "Healthcare",
                "swiftgo_travel_agency": "Travel & Transportation",
                "securewealth_finance": "Finance & Banking",
                "dreamhome_properties": "Real Estate",
                "pawsandclaws_pet_care": "Other Services",
                "content_testing_platform": "Testing & QA",
                "brewing_coffee_cafe": "Food & Beverage",
                "strategic_minds_consulting": "Consulting & Advisory",
                "serenity_resort_and_wellness_spa": "Travel & Hospitality",
                "digital_pulse_marketing_agency": "Digital Marketing",
                "lens_and_light_photography_studio": "Photography & Media",
                "luxe_haven_hotels_and_resorts": "Hospitality & Luxury",
            }
            sid = tmpl_data.get("siteId", "")
            cat = category_map.get(sid, "General")
            doc = {
                "name": name,
                "description": f"{cat} template — {tmpl_data.get('header', {}).get('tagline', '')}",
                "thumbnail_url": "",
                "config": tmpl_data,
                "enabled": True,
                "created_at": NOW,
                "updated_at": NOW,
            }
            result = db.templates.insert_one(doc)
            template_ids.append(result.inserted_id)
            print(f"✅ Template created: {name} ({cat})")

    # 4. Demo domains (with admin_id and subscription)
    # Get the super admin's ID
    super_admin = db.admins.find_one({"role": "super_admin"})
    admin_id = super_admin["_id"] if super_admin else None

    demo_domains = [
        {"domain": "localhost", "path": "", "template_idx": 0, "desc": "localhost (root)"},
        {"domain": "localhost", "path": "demo", "template_idx": 0, "desc": "localhost/demo"},
        {"domain": "localhost", "path": "testbusiness", "template_idx": 1, "desc": "localhost/testbusiness"},
    ]
    for domain_config in demo_domains:
        full_key = domain_config["domain"] if domain_config["path"] == "" else f"{domain_config['domain']}/{domain_config['path']}"
        if not db.domains.find_one({"full_key": full_key}):
            db.domains.insert_one({
                "domain": domain_config["domain"],
                "path": domain_config["path"],
                "full_key": full_key,
                "template_id": template_ids[domain_config["template_idx"]],
                "user_id": demo_user["_id"],
                "admin_id": admin_id,
                "enabled": True,
                "subscription": {
                    "type": "none",
                    "start_date": NOW,
                    "end_date": NOW + timedelta(days=30),
                    "price": None,
                    "is_active": True
                },
                "created_at": NOW,
                "updated_at": NOW,
            })
            print(f"✅ Domain created: {domain_config['desc']} (trial: 30 days)")
        else:
            print(f"⏭️  Domain exists: {domain_config['desc']}")

    print(f"\n🎉 Seed complete! {len(template_ids)} templates in database.")
    print("   Test URL: http://localhost:5173/demo\n")

if __name__ == "__main__":
    run()
