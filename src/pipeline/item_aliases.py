import re
import unicodedata

def norm(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s&/-]", ' ', s)
    s = s.replace('&', ' and ')
    s = s.replace('/', ' ')
    s = s.replace('-', ' ')
    s = re.sub(r"\s+", ' ', s).strip()
    return s

ITEM_ALIASES = {
  "asian pulled pork": "Asian Pulled Pork",
  "beer": "Beer",
  "cajun fried catch": "Cajun Fried Catch",
  "carne asada": "Carne Asada",
  "catering": "Catering",
  "cheesesteak": "Cheesesteak",
  "chips": "Chips",
  "chocolate chip cookie": "Chocolate Chip Cookie",
  "close": "Close",
  "contact": "Contact",
  "dank brownie": "Dank Brownie",
  "dank salad": "Dank Salad",
  "email": "Email",
  "email signup": "Email Signup",
  "faq": "FAQ",
  "facebook": "Facebook",
  "first name": "First Name",
  "fountain drinks": "Fountain Drinks",
  "franchise opportunities": "Franchise Opportunities",
  "guacamole": "Guacamole",
  "hand made in house": "Hand-made in house",
  "hand-made in house": "Hand-made in house",
  "honey truffle buffalo": "Honey Truffle Buffalo",
  "how we roll": "How We Roll",
  "instagram": "Instagram",
  "jerk chicken": "Jerk Chicken",
  "join us": "Join Us",
  "keto salad": "Keto Salad",
  "kids bowl": "Kids Bowl",
  "kids burrito": "Kids Burrito",
  "kids cheese quesadilla": "Kids Cheese Quesadilla",
  "kids chicken tenders": "Kids Chicken Tenders",
  "last name": "Last Name",
  "locations": "Locations",
  "made fresh in house": "Made fresh in-house",
  "made fresh in-house": "Made fresh in-house",
  "main content starts here": "Main content starts here",
  "nutella creme brulee": "Nutella Cr\u00e8me Brulee",
  "nutella cr\u00e8me brulee": "Nutella Cr\u00e8me Brulee",
  "order now": "Order Now",
  "paleo salad": "Paleo Salad",
  "pico": "Pico",
  "plain jane": "Plain Jane",
  "plain jane beef or chicken": "Plain Jane Beef or Chicken",
  "please": "Please",
  "pork belly": "Pork Belly",
  "privacy policy": "Privacy Policy",
  "queso": "Queso",
  "rewards": "Rewards",
  "rice & beans": "Rice & Beans",
  "rice and beans": "Rice & Beans",
  "rice krispy treat": "Rice Krispy Treat",
  "shop": "Shop",
  "shrimp burger": "Shrimp Burger",
  "sides & drinks": "Sides & Drinks",
  "sides and drinks": "Sides & Drinks",
  "skip to main content": "Skip to main content",
  "spicy pico": "Spicy Pico",
  "submit": "Submit",
  "sweet and unsweet tea": "Sweet & Unsweet Tea",
  "sweet & unsweet tea": "Sweet & Unsweet Tea",
  "teriyaki": "Teriyaki",
  "terms of service": "Terms of Service",
  "toggle navigation": "Toggle Navigation",
  "tree hugger": "Tree Hugger",
  "twitter": "Twitter",
  "vanilla cr\u00e8me brulee": "Vanilla Cr\u00e8me Brulee",
  "vanilla creme brulee": "Vanilla Cr\u00e8me Brulee",
  "water": "Water",
  "youtube": "Youtube",
  "beans": "beans",
  "carolina slaw": "carolina slaw",
  "choice of slaw or salsa": "choice of slaw or salsa",
  "cilantro": "cilantro",
  "dill cocktail sauce": "dill cocktail sauce",
  "enter a valid email": "enter a valid email",
  "enter a valid first name": "enter a valid first name",
  "enter a valid last name": "enter a valid last name",
  "fried shrimp": "fried shrimp",
  "lime": "lime",
  "marinated pulled pork": "marinated pulled pork",
  "rice": "rice",
  "sour cream": "sour cream",
  "soy-ginger slaw": "soy-ginger slaw",
  "soy ginger slaw": "soy-ginger slaw",
  "tab to start navigating": "tab to start navigating",
  "bond me": "banh mi-style veggies",
  "bahn me": "banh mi-style veggies",
  "ban me": "banh mi-style veggies",
  "chipotle aioli": "chipotle aioli"
}

def apply_aliases(text: str) -> str:
    low = norm(text)
    # phrase replace using normalized aliases
    for a, canon in ITEM_ALIASES.items():
        # word-boundary-ish replace on normalized text
        low = re.sub(r'\b' + re.escape(a) + r'\b', norm(canon), low)
    return low
